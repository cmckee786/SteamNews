# pylint: disable=wrong-import-order, missing-module-docstring, missing-function-docstring
import hashlib
import json
import logging as log
import logging.handlers
import requests as req
import sqlite3
import sys
from pathlib import Path
from time import localtime, strftime



def log_rotate():
    log.basicConfig(
        level=log.INFO,
        encoding="utf-8",
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="steamnews.log",
        filemode="a",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    rotate = logging.handlers.RotatingFileHandler(
        filename="steamnews.log", maxBytes=20000000, backupCount=5, encoding="utf-8"
    )

    news_logger = log.getLogger("news_logger")
    news_logger.addHandler(rotate)


def db_config_startup():
    if not Path("steam_news.db").exists():
        print("📰 STEAM NEWS: steam_news.db not found, initializing...")
        try:
            with sqlite3.connect("steam_news.db", autocommit=True) as c:
                c.execute(
                    """
                    CREATE TABLE IF NOT EXISTS news (
                        appid INTEGER PRIMARY KEY,
                        title TEXT,
                        url TEXT,
                        date TEXT
                    )
                """
                )
                c.execute("CREATE INDEX IF NOT EXISTS idx_appid ON news (appid)")
            c.close()
        except (sqlite3.Error, OSError) as e:
            print(e)
            log.error("Database setup failed", exc_info=True)

    try:
        if Path("config.json").exists():
            config_hash = "7a141d5d82b9d3675532b599f2c69f6fc4a3b163b80635a995ade08cc56bd6b8"
            with open("config.json", "rb") as f:
                digest = hashlib.file_digest(f, "sha256")
            if digest.hexdigest() == config_hash:
                print(
                    "📰 STEAM NEWS: config.json does not appear to be configured, hash matches build value",
                    "📰 STEAM NEWS: config.json requires a proper Discord ID, USER ID, and Webhook URL",
                    "📰 STEAM NEWS: Exiting...",
                    sep="\n"
                )
                sys.exit(0)
        else:
            print("📰 STEAM NEWS: config.json not found, initializing...")
            data = {
                "DISCORD_ID": "DISCORD SERVER ID HERE",
                "WH_URL": "WEBHOOK URL HERE",
                "USER_ID": "DISCORD USER ID HERE",
                "GAMES": [
                    {"name": "Dyson Sphere Program", "appid": "1366540"},
                    {"name": "Factorio", "appid": "427520"},
                    {"name": "Metro 2033", "appid": "43110"},
                    {"name": "Dead Space: Remastered", "appid": "1693980"},
                ],
            }
            with open("config.json", "w", encoding="utf-8") as config:
                json.dump(data, config, indent=2)
            print(
                "📰 STEAM NEWS: config.json built and waiting for configuration",
                "📰 STEAM NEWS: Script will fail until valid URL and ID's provided",
                "📰 STEAM NEWS: Exiting...",
                sep="\n",
            )
            sys.exit(0)
    except (OSError, IOError, BlockingIOError) as e:
        print(e)
        log.error("Config setup failed", exc_info=True)


def get_news(game_item: dict):
    req_data = {}
    try:
        fetch = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?"
        p = {
            "appid": game_item["appid"],
            "maxlength": 10,
            "count": 1,
            "feeds": "steam_community_announcements",
        }
        req_data = req.request("GET", fetch, params=p, timeout=5).json()

    except req.RequestException as e:
        print(e)
        log.error(e, exc_info=True)

    return req_data["appnews"]["newsitems"][0], game_item["name"]


def check_news_db(req_data, input_json: dict):
    hook_post = ()
    if req_data:
        try:
            record_item = req_data[0]
            app_name = req_data[1]
            time_stamp = strftime("%Y-%m-%d %H:%M")
            post_date = strftime("%Y-%m-%d %H:%M", localtime(record_item["date"]))
            title_new = record_item["title"]
            url_new = record_item["url"]
            appid = int(record_item["appid"])
            wh_url = input_json["WH_URL"]
            user_id = input_json["USER_ID"]

            with sqlite3.connect("steam_news.db", autocommit=True) as c:
                check = c.execute(
                    "SELECT appid FROM news WHERE appid = ?", (appid,)
                ).fetchone()
                if check:
                    check = c.execute(
                        "SELECT title, url FROM news WHERE appid = ?", (appid,)
                    ).fetchone()
                    title_db, url_db = check[0], check[1]
                    if title_new != title_db or url_new != url_db:
                        c.execute(
                            "UPDATE news SET title = ?, url = ?, date = ? WHERE appid = ?",
                            (title_new, url_new, time_stamp, appid),
                        )
                        log.info(f"Updated {app_name} - {title_new} - {url_new}")
                        hook_post = (
                            wh_url,
                            {
                                "content": f"<@{user_id}>\nInitial Release - "
                                f"{post_date}\n{title_new}\n{url_new}"
                            },
                        )
                        print(
                            f"{time_stamp} Updated - NAME: {app_name} - APPID: {appid}"
                        )
                else:
                    c.execute(
                        "INSERT INTO news(appid, title, url, date) VALUES (?, ?, ?, ?)",
                        (appid, title_new, url_new, time_stamp),
                    )
                    log.info(f"New record {app_name} - {title_new} - {url_new}")
                    hook_post = (
                        wh_url,
                        {
                            "content": f"<@{user_id}>\nInitial Release - "
                            f"{post_date}\n{title_new}\n{url_new}"
                        },
                    )
                    print(
                        f"{time_stamp} New record - NAME: {app_name} - APPID: {appid}"
                    )
            c.close()
        except sqlite3.Error as e:
            print(e)
            log.error(e, exc_info=True)
    return hook_post
