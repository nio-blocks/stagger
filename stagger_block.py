from datetime import timedelta
from collections import deque
from time import sleep
import math
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.block.base import Block
from nio.metadata.properties import TimeDeltaProperty
from nio.modules.threading import spawn


@Discoverable(DiscoverableType.block)
class Stagger(Block):

    # How much we want to "spread out" the incoming signals
    period = TimeDeltaProperty(title='Period', default=timedelta(seconds=1))

    # This is the minimum interval we will emit signals. If a large number of
    # signals comes through, we don't necessarily want to notify them one by
    # one anymore, but rather in many small groups. This is the interval that
    # those small groups will be notified.
    #
    # Defaults to 100 milliseconds (10 notifications per second)
    min_interval = TimeDeltaProperty(
        title='Minimum Interval',
        visible=False,
        default=timedelta(microseconds=100000))

    def process_signals(self, signals, input_group=None):
        stagger_period = self._get_stagger_period(len(signals))
        self._logger.debug("{} signals received, notifying every {}".format(
            len(signals), stagger_period))

        # Launch the notification mechanism in a new thread so that it can
        # sleep between notifications
        spawn(self._do_notification, StaggerData(
            stagger_period, math.ceil(self.period / stagger_period), signals))


    def _get_stagger_period(self, num_signals):
        """ Returns the stagger period based on a number of signals """
        return max(self.period / num_signals, self.min_interval)

    def _do_notification(self, stagger_data):
        """ Take a stagger data object and perform the signal notifications """
        while stagger_data.signals_deque:
            sigs_out = stagger_data.signals_deque.popleft()
            self._logger.debug("Notifying {} signals".format(len(sigs_out)))
            self.notify_signals(sigs_out)
            sleep(stagger_data.interval.total_seconds())

class StaggerData(object):

    """ A class containing an interval and a stack of signals to notify """

    interval = None
    num_groups = None
    signals = None
    signals_deque = None

    def __init__(self, interval, num_groups, signals):
        self.interval = interval
        self.num_groups = num_groups
        self.signals = signals
        self._build_deque()

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
