'''
A test suite for diplomacy reminder script
'''

import unittest
from datetime import datetime
import os
from dip_reminder import reminder_required, get_time_left, send_email, set_last_reminder, get_last_reminder

class TestDipReminder(unittest.TestCase):
    '''
    Unit tests for the diplomacy reminder package
    '''

    def setUp(self):
        GMAIL_ADDRESS = os.environ.get('GMAIL_ADDRESS')
        GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')


    def test_reminder_required(self):
        '''
        A reminder is required if the days remaining is less than
        the reminder threshold and there wasn't a reminder this phase.

        Last reminder is set to epoch in this example
        '''
        self.assertEqual(
            reminder_required(
                days=3, days_left=2,
                last_reminder=datetime.fromtimestamp(1), phase=7)['required'],
            True)


    def test_reminder_already_sent(self):
        '''
        Reminder should not be true if it has already been sent this phase
        '''
        self.assertEqual(
            reminder_required(
                days=3, days_left=2,
                last_reminder=datetime.now(), phase=7)['message'],
            'Reminder already sent this turn')


    def test_reminder_threshold_not_met(self):
        '''
        Reminder shouldn't be sent if there are still more days left than
        the days threshold
        '''
        self.assertEqual(
            reminder_required(
                days=1, days_left=2,
                last_reminder=datetime.fromtimestamp(0), phase=7)['message'],
            'Reminder threshold not met')


    def test_time_left(self):
        '''
        Check that the scraping code still works by checking it returns a value

        This will always fail without internet access
        '''
        self.assertIsNotNone(
            get_time_left(160982)
            )


    def test_send_mail(self):
        '''
        Checks that an email will be sent
        '''
        self.assertNotEqual(
            send_email('thmcmahon@gmail.com', 1),
            'Unable to send mail'
            )


    def test_set_last_reminder(self):
        '''
        Checks whether a reminder can be pickled
        '''
        self.assertEqual(
            set_last_reminder(),
            'Item pickled'
            )

    def test_get_last_reminder(self):
        '''
        Checks whether the reminder can be loaded
        '''
        self.assertNotEqual(
            set_last_reminder(), get_last_reminder(),
            'No last reminder time'
            )

if __name__ == '__main__':
    unittest.main()
