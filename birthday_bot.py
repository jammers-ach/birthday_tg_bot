#!/usr/bin/env python3
import gspread
import argparse
import os
import asyncio

from datetime import datetime
from telegram import Bot


config = None

def read_config(file_path="~/.birthday_bot_config"):
    # Expand the tilde (~) to the user's home directory
    file_path = os.path.expanduser(file_path)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Config file not found: {file_path}")

    # Parse the configuration values
    config_values = {}

    with open(file_path) as config_file:
        for line in config_file.readlines():
            key, value = map(str.strip, line.split('=', 1))
            config_values[key] = value

    # Check if required keys are present
    required_keys = ['BOT_TOKEN', 'SHEET_URL', 'CHAT_IDS']
    for key in required_keys:
        if key not in config_values:
            raise ValueError(f"Missing required key in config file: {key}")

    # Access configuration values
    bot_token = config_values['BOT_TOKEN']
    sheet_url = config_values['SHEET_URL']
    chat_ids = [chat_id.strip() for chat_id in config_values['CHAT_IDS'].split(',')]

    return {
        'bot_token': bot_token,
        'sheet_url': sheet_url,
        'chat_ids': chat_ids,
    }


today = datetime.now()

default_norm_msg="{day}.{month} {dow} - {name}"
default_present_msg="{day}.{month} {dow} - {name}, {present} maybe?"



def get_birthdays(gc, sheet_url):
    sh = gc.open_by_url(sheet_url)
    list_of_dicts = sh.sheet1.get_all_records()
    for entry in list_of_dicts:
        parsed_dob = datetime.strptime(entry["DOB"], "%d.%m.%Y")
        entry["date"] = parsed_dob.replace(year=today.year)

    return list_of_dicts

def filter_birthdays(birthdays, filter_func):
    '''filter the birthdays by the filter function.

    The filter function has one paramater, a datetime object (the DOB)
    and returns true if it needs to stay'''
    true_filter = lambda x: filter_func(x['date'])
    return filter(true_filter, birthdays)


def days_until_same_day(d1, d2):
    """
    Calculate the number of days until the same day of the year for two given dates.

    Parameters:
    - d1: datetime object representing the first date
    - d2: datetime object representing the second date

    Returns:
    - The number of days until the same day of the year for the two dates
    """

    # Calculate the day of the year for both dates
    day_of_year_d1 = d1.timetuple().tm_yday
    day_of_year_d2 = d2.timetuple().tm_yday

    days_until_same_day = day_of_year_d2 - day_of_year_d1
    return days_until_same_day



def make_message(birthdays, present_msg=None, norm_msg=None):
    if not present_msg:
        present_msg = default_present_msg
    if not norm_msg:
        norm_msg = default_norm_msg

    message = []
    for birthday in birthdays:
        key = {
            'month': birthday['date'].month,
            'day': birthday['date'].day,
            'dow': birthday['date'].strftime("%a"),
            'name': birthday['Who'],
            'present': birthday['Present']
        }

        if key['present'] == '':
            msg = norm_msg.format(**key)
        else:
            msg = present_msg.format(**key)

        message.append(msg)


    return '\n'.join(message)



async def send_to_tg(intro_msg, birthday_msg, bot_token, chat_ids):
    bot = Bot(token=bot_token)
    for chat_id in chat_ids:
        msg_txt = f"{intro_msg}\n{birthday_msg}"
        await bot.send_message(chat_id=chat_id, text=msg_txt)

def main():

    parser = argparse.ArgumentParser(description="Birthday Bot")

    parser.add_argument('-check_creds', action='store_true', help='Try to connect to the bot and Google Sheets. Use this to test your config')
    parser.add_argument('-dry_run', action='store_true', help='Output the text to the console and not a message to receivers')
    parser.add_argument('-todays', action='store_true', help='List who has birthdays today')
    parser.add_argument('-birthdays', type=int, metavar='weeks', help='List all people with birthdays in the next <weeks> number of weeks')
    parser.add_argument('-presents', type=int, metavar='weeks', help='List all people and their presents in the next <weeks> number of weeks')
    parser.add_argument('-months', action='store_true', help='List all people who have a birthday in the month this is run')

    args = parser.parse_args()

    global config
    config = read_config()

    gc = gspread.service_account()
    if args.check_creds:
        print("Login to service_account: Ok")
        print("Login to telegram: ok")
        print("sending TG message")
        return


    birthdays = get_birthdays(gc, config['sheet_url'])

    # Now you can use the arguments in your code
    if args.todays:
        intro_msg = "Todays birthdays"
        birthdays = filter_birthdays(birthdays,lambda x: days_until_same_day(today, x) == 0)
    elif args.birthdays:
        intro_msg = f"Birthdays in the next {args.birthdays} weeks:"
        birthdays = filter_birthdays(birthdays,lambda x: days_until_same_day(today, x) < args.birthdays * 7)
    elif args.presents:
        intro_msg = f"Birthdays with presents for the next {args.presents} weeks"
        birthdays = filter_birthdays(birthdays,lambda x: days_until_same_day(today, x) < args.presents* 7)
        birthdays = filter(lambda x: x['Present'] != '', birthdays)
    elif args.months:
        intro_msg = "Birthdays this month"
        birthdays = filter_birthdays(birthdays,lambda x: x.month == today.month)
    else:
        parser.print_help()
        return

    birthdays = sorted(birthdays, key=lambda x: x['date'])

    if len(birthdays) > 0:

        if args.dry_run:
            print(intro_msg)
            print(make_message(birthdays))
        else:
            asyncio.run(send_to_tg(intro_msg, make_message(birthdays), config['bot_token'], config['chat_ids']))
    else:
        print(f"No {intro_msg}")

if __name__ == '__main__':
    main()
