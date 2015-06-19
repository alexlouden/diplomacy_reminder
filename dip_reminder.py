'''
A script to send reminders to email address when diplmacy turn is nearly over
'''
import os
import pickle
import smtplib
from datetime import datetime

import click
import requests
from bs4 import BeautifulSoup


GMAIL_ADDRESS = os.environ.get('GMAIL_ADDRESS')
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')


def get_time_left(game_id):
    '''
    Scrape webdiplomacy url for the amount of time left in the season

    Returns: a datetime.timedelta object of the amount of time left
    '''
    game_url = "http://webdiplomacy.net/board.php?gameID=%s#gamePanel" % game_id
    request = requests.get(game_url)
    soup = BeautifulSoup(request.text)
    # timeremaining is the class of the diplomacy span
    # it includes the due date in epoch time
    time_remaining_el = soup.find('span', {"class": "timeremaining"}).attrs['unixtime']
    due_time = datetime.fromtimestamp(int(time_remaining_el))
    now = datetime.now()
    time_left = due_time - now
    return time_left


def send_email(group_address, time_left):
    '''
    Send facebook group a reminder that there are only `time_left` days
    remaining until next turn
    '''

    # Check keys are set
    if GMAIL_ADDRESS is None or GMAIL_PASSWORD is None:
        raise KeyError('Environment variables not set!')

    # Send this message
    msg = 'DiploBot Reminder--There are %s day(s)' \
          'remaining until the next turn' % time_left

    try:
        server = smtplib.SMTP("smtp.gmail.com:587")
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, group_address, msg)
        server.quit()
        # print('Mail sent with message: %s') % msg

    except smtplib.SMTPException:
        print('Unable to send mail')


def set_last_reminder():
    '''
    Set the last reminder time and encode it to disk
    '''
    last_reminder = []
    last_reminder.append(datetime.now())
    with open('last_reminder.p', 'wb') as pickle_file:
        pickle.dump(last_reminder, pickle_file)
        return 'Item pickled'


def get_last_reminder():
    '''
    Get the last reminder date from the pickled file

    Returns: datetime object of the last time a reminder was sent
    '''
    try:
        with open('last_reminder.p', 'rb') as f:
            last_reminder = pickle.load(f)[0]
            print('Last reminder sent on: {:%d/%m/%y}'.format(last_reminder))

    except IOError:
        # Set the last reminder time to ancient to force script to run
        last_reminder = datetime.fromtimestamp(1)
        print('No last reminder time')

    return last_reminder


def reminder_required(days, days_left, last_reminder, phase):
    '''
    Test if a reminder is required
    '''
    # If days since last reminder is more than the length of the phase
    if (datetime.now() - last_reminder).days > phase:
        # If number of days_left is less than or equal to the desired reminder
        # threshold
        if days_left < days:
            return {'required': True, 'message': 'Email required'}
        else:
            return {'required': False, 'message': 'Reminder threshold not met'}
    else:
        return {'required': False, 'message': 'Reminder already sent this turn'}


@click.command()
@click.option('--days', default=1,
              help='How many days left before reminder is sent')
@click.option('--phase', default=7, help='How many days per phase?')
@click.option('--email', help='What email should I send the reminder to?',
              required=True)
@click.option('--game_id', help='Diplomacy game ID', required=True)
def reminder(days, phase, email, game_id):
    '''
    Send the reminder email if environment variables are set and the day
    threshold has been met
    '''
    days_left = get_time_left(game_id).days
    last_reminder = get_last_reminder()
    reminder_needed = reminder_required(days, days_left, last_reminder, phase)

    if reminder_needed['required']:
        send_email(email, days_left)
        set_last_reminder()
        print('Reminder email sent to %s' % email)
    else:
        # If reminder is not true, then return the error message
        print(reminder_needed['message'])


if __name__ == '__main__':
    # Run the main function
    reminder()
