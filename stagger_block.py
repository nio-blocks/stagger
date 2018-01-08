from collections import deque
from copy import copy, deepcopy
from datetime import timedelta
import math

from nio.block.base import Block
from nio.properties import TimeDeltaProperty, VersionProperty
from nio.modules.scheduler.job import Job


class Stagger(Block):

    version = VersionProperty("1.0.1")
    period = TimeDeltaProperty(title='Period', default={"seconds": 1})
    min_interval = TimeDeltaProperty(
        title='Minimum Interval',
        visible=False,
        default={"microseconds": 100000})

    def process_signals(self, signals, input_id=None):
        stagger_period = self._get_stagger_period(len(signals))
        self.logger.debug("{} signals received, notifying every {}".format(
            len(signals), stagger_period))

        # Launch the notification mechanism in a new thread so that it can
        # sleep between notifications
        stagger_data = StaggerData(
            stagger_period,
            math.ceil(self.period() / stagger_period),
            signals,
            self.notify_signals,
            self.logger,
        )
        stagger_data.start_notify()

    def _get_stagger_period(self, num_signals):
        """ Returns the stagger period based on a number of signals """
        return max(self.period() / num_signals, self.min_interval())


class StaggerData(object):

    """ A class containing an interval and a stack of signals to notify """

    def __init__(self, interval, num_groups, signals, notify_signals, logger):
        self.interval = interval
        self.num_groups = num_groups
        try:
            self.signals = deepcopy(signals)
        except:
            self.signals = copy(signals)
        self.notify_signals = notify_signals
        self.logger = logger
        self._build_deque()

    def start_notify(self):
        # Notify the first signals right away
        self._notify()
        # Repeat notify every interval until cancelled
        self._notify_job = Job(
            self._notify,
            timedelta(seconds=self.interval.total_seconds()),
            True)

    def _notify(self):
        if not self.signals_deque:
            self._notify_job.cancel()
        else:
            sigs_out = self.signals_deque.popleft()
            self.logger.debug("Notifying {} signals".format(len(sigs_out)))
            self.notify_signals(sigs_out)

    def _build_deque(self):
        """ Build the stack of signals based on number of groups we want """
        self.signals_deque = deque()
        signals_included = 0
        signals_per_group = len(self.signals) / self.num_groups
        for group_num in range(self.num_groups):

            # How many we should have after this iteration
            total_expected = (group_num + 1) * signals_per_group

            # Take what we expect to have and subtract the number of signals
            # we already have to determine how many to add for this iteration.
            # Round the number to space out uneven intervals
            signals_this_time = round(total_expected - signals_included)

            # Make sure to account for the signals we just added
            signals_included += signals_this_time

            # Build a list of signals for this interval and push it on to the
            # stack - pop the signals off the original list
            signals_to_include = list()
            for sig in range(signals_this_time):
                signals_to_include.append(self.signals.pop(0))
            self.signals_deque.append(signals_to_include)
