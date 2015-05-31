'''
A script to send reminders to email addresses when diplomacy turns is over
'''

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
import os
import click
import pickle

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
    now = datetime.now()
    # timeremaining is the class of the diplomacy span
    # it includes the due date in epoch time
    due_time = datetime.fromtimestamp(int(soup.find('span',
        {"class": "timeremaining"}).attrs['unixtime']))
    time_left = due_time - now
    return time_left


def send_email(group_address, time_left):
    '''
    Send facebook group a reminder that there are only `time_left` days
    remaining until next turn
    '''

    # Check keys are set
    if GMAIL_ADDRESS and GMAIL_PASSWORD is None:
        raise KeyError('Environment variables not set!')

    # Send this message
    msg = 'DiploBot Reminder--There are %s day(s)' \
          'remaining until the next turn' % time_left
    print(msg)
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
    server.sendmail(GMAIL_ADDRESS, group_address, msg)
    server.quit()


def set_last_reminder():
    '''
    Set the last reminder time and encode it to disk
    '''
    last_reminder = []
    last_reminder.append(datetime.now())
    with open('last_reminder.p', 'wb') as pickle_file:
        pickle.dump(last_reminder, pickle_file)


@click.command()
@click.option('--days', default=1, help='How many days left before reminder')
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

    try:
        last_reminder = pickle.load(open('last_reminder.p', 'rb'))[0]
        print('Last reminder sent on: ' +
              datetime.strftime(last_reminder, '%d/%m/%y'))

    except FileNotFoundError:
        # Set the last reminder time to aincent to force script to run
        last_reminder = datetime.fromtimestamp(1)
        print('No last reminder time')

    # If the last reminder was longer than a phase ago and it's now in the
    # reminder time then send the reminder!
    if (datetime.now() - last_reminder).days > phase and days_left <= days:
        send_email(email, days_left)
        set_last_reminder()
    else:
        print('No reminder required at this point')


if __name__ == '__main__':
    # Run the main function
    reminder()
