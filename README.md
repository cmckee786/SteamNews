# Steam News

- Uses Steam Web API to get news for a list of Steam game application IDs
    - At this time (2025) [api.steampowered.com/ISteamNews/GetNewsForApp/v2/](https://partner.steamgames.com/doc/webapi/isteamnews) does not require an API Key
- Sends news through a user provided Discord webhook in batches if there is a new announcement
- Updates DB accordingly to track updates, only attempts to track current posts
- Builds database and config if not found
- Edit config.json file accordingly with IDs and webhook URL
- Implements python built-in logging and log rotation
  
<img width="492" height="694" alt="image" src="https://github.com/user-attachments/assets/409a8b08-e9b9-4da0-98ba-172cc04ea502" />

> [!NOTE]
> Intended to be implemented as a cron job or scheduled task

The cron job may look something like this:
```bash
# ┌──────────── [optional] seconds (0 - 59)
# | ┌────────── minute (0 - 59)
# | | ┌──────── hour (0 - 23)
# | | | ┌────── day of month (1 - 31)
# | | | | ┌──── month (1 - 12) OR jan,feb,mar,apr ...
# | | | | | ┌── day of week (0 - 6, sunday=0) OR sun,mon ...
# | | | | | |
# * * * * * * command

# Every hour of the day
    0 * * * * /path/to/steamnews.py
    # 0 * * * * /path/to/steamnews.py >> /var/log/cronjob.log 2>&1
```
The commented command will append all stdout and stderr to a log file if you so desire.

## Build

```bash
git clone https://github.com/cmckee786/SteamNews && cd SteamNews
python3 -m venv venv/ && source "$PWD"venv/bin/activate
pip install -U pip && pip install -r requirements.txt
python3 steamnews.py
```
This will build the virtual python environment, install necessary dependencies and initialize
the user `config.json` file into a default state shown in the schema below. This config file is
built in this way to protect the user from exposing any IDs or unique Discord webhooks should they
fork or implement their own repo which may also unintentionally become public. The `.gitignore` file
is set to ignore `config.json` by default.

From here `config.json` should be configured with the appropriate user provided Discord Guild ID,
User ID, and desired games to be tracked. These can be derived via Discord developer mode found
[here](https://discord.com/developers/docs/activities/building-an-activity#step-0-enable-developer-mode).

After such the script should function as expected and Discord notifications should begin hitting the
configured Discord ID. **Note that the Steam Web API limits requests to 100,000 API calls every 24 hours.**

> [!CAUTION]
> This script implements threading! Rate limits may apply! USE WISELY!!

Schema
--------

```json
{
  "DISCORD_ID": "DISCORD SERVER ID HERE",
  "WH_URL": "WEBHOOK URL HERE",
  "USER_ID": "DISCORD USER ID HERE",
  "GAMES": [
    {
      "name": "Dyson Sphere Program",
      "appid": "1366540"
    },
    {
      "name": "Factorio",
      "appid": "427520"
    },
    {
      "name": "Metro 2033",
      "appid": "43110"
    },
    {
      "name": "Dead Space: Remastered",
      "appid": "1693980"
    }
  ]
}
```
