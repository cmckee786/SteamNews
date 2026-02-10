#!/bin/python3

# v1.5.7
# Authored by Christian McKee cmckee786@github.com

# Uses Steam Web API to get news from a json formatted list of games
# Sends news through a Discord webhook if there is a new announcement
# Updates DB accordingly
# Logs errors and updates to a log file

# TODO:
#   - Implement frontend with search(?)
#       - jinja? django?

import concurrent.futures
import json
import logging as log
import requests
import utils

# If ThreadPoolExecutor max_workers is None or not given, it will
# default to the number of processors on the machine, multiplied by 5
WORKERS = None


def process_game(game: dict) -> str | None:
    discord_post = None
    try:
        news_item = utils.get_news(game)
        discord_post = utils.check_news_db(news_item)
    except requests.RequestException as e:
        log.error(e, exc_info=True)

    return discord_post


def main() -> None:
    staging: list[str] = []
    batch_message: str = ""
    utils.log_rotate()
    utils.db_config_startup()
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            input_json = json.load(f)

        wh_url = input_json.get("WH_URL", [])
        user_id = input_json.get("USER_ID", [])
        games = input_json.get("GAMES", [])
        print(f"📰 STEAM NEWS: Processing {len(games)} games...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = [executor.submit(process_game, game) for game in games]

            for future in concurrent.futures.as_completed(futures):
                msg = future.result()
                if msg:
                    staging.append(msg)

        if staging:
            for i in range(0, len(staging), 5):
                batch = staging[i : i + 5]
                batch_message = "\n\n".join(batch)

                requests.post(
                    url=wh_url,
                    json={"content": f"<@{user_id}>\n{batch_message}"},
                    timeout=3,
                )
            print("📰 STEAM NEWS: Batch messages sent...")
        else:
            print("📰 STEAM NEWS: No updates...")
        print("📰 STEAM NEWS: Finished")
    except (OSError, json.JSONDecodeError, Exception) as e:
        print(e)
        log.error(e, exc_info=True)


if __name__ == "__main__":
    main()
