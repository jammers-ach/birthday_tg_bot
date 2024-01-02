# birthday_tg_bot


A telegram bot which reads a google sheet and sends you reminders for birthdays.

You create a google sheet with the date of birth, name and present idea for someone.


# Prerequesites

## Drive access
Setup a service account

https://docs.gspread.org/en/latest/oauth2.html#service-account


## Telegram bot

Go to the get_id_bot and get your chat id, create a new bot in botfather and the token

# installation

create a config file `~/.birthday_bot_config`

```
BOT_TOKEN=<telegram bot token>
SHEET_URL=<url of your google sheets>
CHAT_IDS=<comma seperated list of chat ids>
```

then install the python dependencies

you start the bot by running the script:
`./birthday_bot.py --help`


Options:
 * `-check_creds` will try to connect to the bot and google sheets. Use this to test your config
 * `-dry_run` will output the text to the console and not a message to reciveres
 * `-todays` will list who has birthdays today
 * `-bithdays <weeks>` will list all the people who have birthdays and presents in the next `<weeks>` number of weeks
 * `-presents <weeks>` will list all the people and their presents in the next `<weeks>` number of weeks
 * `-months` will list all the people who have a birthday in the month this is run


you can then setup a cronjob for whatever option you want:
```
# remind me at 8am of who has a birthday today
0 8 * * * /path/to/bot/birthday_bot.py -todays

# remind me on sunday evening who has birthdays in the next 2 weeks
20 0 * * 0 /path/to/bot/birthday_bot.py -birthdays 2

# remind me on sunday who I need to get a present for in the next 4 weeks
20 0 * * 0 /path/to/bot/birthday_bot.py -presents 4
```


## Customising your notification

The default notification is:
`{month}.{day} - birthday: {name}` - if there's no present
`{month}.{day} - birthday: {name}, {present} maybe?` - if there's a present

you can create a file `~/.birthday_bot_messages` if you want to customise.
The first line is if there's no present, the second line if there is a present

the following customisation variables are available:
* `{month}`
* `{day}`
* `{dow}` - mon, tue, wed
* `{name}`
* `{present}`

