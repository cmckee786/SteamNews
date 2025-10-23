# Steam News

- Uses Steam Web API to get news for a list of Steam game application IDs
- Edit config.json file accordingly with keys and webhook urls
- Sends news through a user provided Discord webhook if there is a new announcement
- Updates DB accordingly
- Builds database if not found
- Implements python built-in logging and log rotation

> [!NOTE]
> Intended to be implemented as a cron job or scheduled task

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
python3 app.py
```

