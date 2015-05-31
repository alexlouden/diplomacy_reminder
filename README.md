## Diplomacy Reminder

A python 3 script to send a reminder to an email that a webdiplomacy round is about to end.

### Example

This will send an email to group_email@gmail.com when there is 1 day to go in game ID 12345.

`python3 dip_reminder.py --mail group_email@gmail.com --game_id 12345 --days 1`

#### Usage

```
Usage: dip_reminder.py [OPTIONS]

  Send the reminder email if environment variables are set and the day
  threshold has been met

Options:
  --days INTEGER   How many days left before reminder
  --phase INTEGER  How many days per phase?
  --email TEXT     What email should I send the reminder to?  [required]
  --game_id TEXT   Diplomacy game ID  [required]
  --help           Show this message and exit.
```

#### Install

This script runs on Python 3. You'll need the following dependencies for it to run.

```
beautifulsoup4==4.3.2
click==4.0
requests==2.7.0
```