# pylint: disable=wrong-import-order, missing-module-docstring, missing-function-docstring
import logging as log
import logging.handlers
import requests as req
import sqlite3
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


def db_startup():
    if not Path("steam_news.db").exists():
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
        print(f"STEAM NEWS: Fetching news - {game_item['appid']} - {game_item['name']}")
        req_data = req.request("GET", fetch, params=p, timeout=5).json()

    except req.RequestException as e:
        print(e)
        log.error(e, exc_info=True)

    return req_data


def check_news_db(req_data, input_json: dict):
    hook_post = ()
    if req_data:
        try:
            time_stamp = strftime("%Y-%m-%d %H:%M")
            post_date = strftime("%Y-%m-%d %H:%M", localtime(req_data["date"]))
            title_new = req_data["title"]
            url_new = req_data["url"]
            appid = int(req_data["appid"])
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
                        log.info(f"Updated {appid} - {title_new} - {url_new}")
                        hook_post = (
                            wh_url,
                            {
                                "content": f"<@{user_id}>\nInitial Release - "
                                f"{post_date}{title_new}\n{url_new}"
                            },
                        )
                else:
                    c.execute(
                        "INSERT INTO news(appid, title, url, date) VALUES (?, ?, ?, ?)",
                        (appid, title_new, url_new, time_stamp),
                    )
                    log.info(f"Added {appid} - {title_new} - {url_new}")
                    hook_post = (
                        wh_url,
                        {
                            "content": f"<@{user_id}>\nInitial Release - "
                            f"{post_date}\n{title_new}\n{url_new}"
                        },
                    )
            c.close()
        except sqlite3.Error as e:
            print(e)
            log.error(e, exc_info=True)
    return hook_post
