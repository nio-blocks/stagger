from ..stagger_block import Stagger, StaggerData
from nio.signal.base import Signal
from time import sleep
from nio.testing.block_test_case import NIOBlockTestCase


class TestStaggerBlock(NIOBlockTestCase):

    def test_stagger_data_5_3(self):
        """ 5 signals over 3 groups
        signals_per_group = 1.66666

        2 | 1 | 2
        """
        sd_3_5 = self._get_stagger_deque(3, 5)
        self.assertEqual(len(sd_3_5), 3)
        self.assertEqual(sd_3_5[0], [0, 1])
        self.assertEqual(sd_3_5[1], [2])
        self.assertEqual(sd_3_5[2], [3, 4])

    def test_stagger_data_6_3(self):
        """ 6 signals over 3 groups
        signals_per_group = 2.0

        2 | 2 | 2
        """
        sd_3_6 = self._get_stagger_deque(3, 6)
        self.assertEqual(len(sd_3_6), 3)
        self.assertEqual(sd_3_6[0], [0, 1])
        self.assertEqual(sd_3_6[1], [2, 3])
        self.assertEqual(sd_3_6[2], [4, 5])

    def test_stagger_data_1_3(self):
        """ 1 signal over 3 groups
        signals_per_group = 0.33

        0 | 1 | 0
        """
        sd_3_1 = self._get_stagger_deque(3, 1)
        self.assertEqual(len(sd_3_1), 3)
        self.assertEqual(sd_3_1[0], [])
        self.assertEqual(sd_3_1[1], [0])
        self.assertEqual(sd_3_1[2], [])

    def _get_stagger_deque(self, groups, num_sigs):
        sd = StaggerData(None, groups, [i for i in range(num_sigs)])
        return sd.signals_deque

    def test_stagger_block_normal(self):
        """ Assert signals get notified in a staggered fashion """
        blk = Stagger()
        self.configure_block(blk, {
            "period": {"seconds": 2},
            "log_level": "DEBUG"
        })
        num_signals = 5
        blk.process_signals([Signal({"num": i}) for i in range(num_signals)])

        # Assert that half get notified first
        sleep(1)
        self.assert_num_signals_notified(3)

        # Assert that after the full interval all signals are notified
        sleep(1)
        self.assert_num_signals_notified(num_signals)

    def test_stagger_block_overloaded(self):
        """ Assert all signals get notified if more signals than groups """
        blk = Stagger()
        self.configure_block(blk, {
            "period": {"seconds": 1},
            "log_level": "DEBUG"
        })
        num_signals = 33
        blk.process_signals([Signal({"num": i}) for i in range(num_signals)])

        # Assert that after the full interval all signals are notified
        sleep(1.1)
        self.assert_num_signals_notified(num_signals)
