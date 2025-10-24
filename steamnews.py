#!/bin/python3

# v1.3.5
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


def process_game(game, input_json):
    """Process game; fetch news, check DB, post to Discord if new or updated"""
    try:
        news_item = utils.get_news(game)
        discord_post = utils.check_news_db(news_item, input_json)
        if discord_post:
            requests.post(url=discord_post[0], json=discord_post[1], timeout=3)
    except Exception as e:
        log.error(e, exc_info=True)


def main():
    utils.log_rotate()
    utils.db_startup()
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            input_json = json.load(f)

        games = input_json.get("GAMES", [])
        print(f"📰 STEAM NEWS: Processing {len(games)} games...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(process_game, game, input_json) for game in games
            ]

            for future in concurrent.futures.as_completed(futures):
                future.result()

        print("\U0001f4f0 STEAM NEWS: Finished")
    except (OSError, json.JSONDecodeError) as e:
        print(e)
        log.error(e, exc_info=True)


if __name__ == "__main__":
    main()
