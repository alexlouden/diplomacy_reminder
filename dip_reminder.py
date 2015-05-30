import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
import os
import click

gmail_address = os.environ.get('GMAIL_ADDRESS')
gmail_password = os.environ.get('GMAIL_PASSWORD')

def get_time_left(id):
    # Scrape webdiplomacy url for the amount of time left in the season
    #
    # Returns: a datetime.timedelta object of the amount of time left
    game_url = "http://webdiplomacy.net/board.php?gameID=%s#gamePanel" % id
    r = requests.get(game_url)
    soup = BeautifulSoup(r.text)
    now = datetime.now()
    # timeremaining is the class of the diplomacy span
    # it includes the due date in epoch time
    due_time = datetime.fromtimestamp(
                    int(soup.find('span',
                                  {"class": "timeremaining"}).attrs['unixtime']
                        ))
    time_left = due_time - now
    return(time_left)


def send_email(group_address, time_left):
    # Send facebook group a reminder that there are only `time_left`
    # days remaining until next turn
    msg = 'DiploBot Reminder--There are %s day(s)' \
    	  'remaining until the next turn' % time_left
    print(msg)
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(gmail_address,gmail_password)
    server.sendmail(gmail_address, group_address, msg)
    server.quit()


@click.command()
@click.option('--days', default=1, help='How many days left before reminder')
@click.option('--email', help='What email should I send the reminder to?',
			  required=True)
@click.option('--id', help='Diplomacy game ID', required=True)
def reminder(days, email, id):
	# Send the reminder email if environment variables are set and the day
	# threshold has been met

	if gmail_address and gmail_password is not None:
		days_left = get_time_left(id).days
		
		if days_left <= days:
			send_email(email, days_left)
		else:
			print('Day threshold not yet met')
	
	else:
		raise KeyError('Environment variables not set!')
	


if __name__ == '__main__':
    reminder()