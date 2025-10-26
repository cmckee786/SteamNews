# Steam News

- Uses Steam Web API to get news for a list of Steam game application IDs
    - At this time (2025) (api.steampowered.com/ISteamNews/GetNewsForApp/v2/)[https://partner.steamgames.com/doc/webapi/isteamnews] does not require an API Key
- Edit config.json file accordingly with keys and webhook urls
- Sends news through a user provided Discord webhook if there is a new announcement
- Updates DB accordingly to track updates, only tracks latest news
- Builds database if not found
- Implements python built-in logging and log rotation

<img width="519" height="554" alt="Screenshot 2025-10-23 180313" src="https://github.com/user-attachments/assets/9682486e-643e-4235-b7e6-061b51fb8339" />

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
    0 * * * * /path/to/steamnews.py >> /var/log/cronjob.log 2>&1
```
This will append all stdout and stderr to a log file if you so desire. Otherwise output is thrown away.  
Other versions may begin supporting an easily configurable frontend.

## Build

```bash
# From root of repo
python3 -m venv . && source "$PWD"/bin/activate
pip install -U pip && pip install -r requirements.txt
```
From here you should configure `config.json` with your Discord IDs and games. After such,
execute the code below from the root of the repo.

```bash
python3 steamnews.py
```
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
