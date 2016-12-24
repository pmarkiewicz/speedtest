import unittest
from datetime import datetime
from processor import *

class ProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.hr1 = [{'upload': 100, 'download': 100, 'ping': 100, 'timestamp': datetime(2016, 1, 1, 10, 10)}]
        self.hr5 = [{'upload': 200, 'download': 200, 'ping': 200, 'timestamp': datetime(2016, 1, 1, 10, 10)},
                    {'upload': 100, 'download': 100, 'ping': 100, 'timestamp': datetime(2016, 1, 1, 10, 20)},
                    {'upload': 50, 'download': 50, 'ping': 50, 'timestamp': datetime(2016, 1, 1, 10, 30)},
                    {'upload': 50, 'download': 50, 'ping': 50, 'timestamp': datetime(2016, 1, 1, 10, 40)},
                    {'upload': 100, 'download': 100, 'ping': 100, 'timestamp': datetime(2016, 1, 1, 11, 10)}]

    def test_hr1(self):
        r = average_speed_hourly(self.hr1)
        self.assertEqual(len(r), 1)
        avg = r.get('2016010110')
        self.assertTrue(avg)
        self.assertEqual(avg['upload'], 100)
        self.assertEqual(avg['download'], 100)
        self.assertEqual(avg['ping'], 100)

    def test_hr5(self):
        r = average_speed_hourly(self.hr5)
        self.assertEqual(len(r), 2)

        avg = r.get('2016010110')
        self.assertTrue(avg)
        self.assertEqual(avg['upload'], 100)
        self.assertEqual(avg['download'], 100)
        self.assertEqual(avg['ping'], 100)

        avg = r.get('2016010111')
        self.assertTrue(avg)
        self.assertEqual(avg['upload'], 100)
        self.assertEqual(avg['download'], 100)
        self.assertEqual(avg['ping'], 100)
