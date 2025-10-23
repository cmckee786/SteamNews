#!/bin/python3

# v1.2.5
# Authored by Christian McKee cmckee786@github.com

# Uses Steam Web API to get news from a json formatted list of games
# Sends news through a Discord webhook if there is a new announcement
# Updates DB accordingly
# Logs errors and updates to a log file

# TODO:
#   - Implement frontend with search(?)
#       - jinja? django?

import json
import logging as log
import requests
import utils


def main():
    utils.log_rotate()
    utils.db_startup()
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            input_json = json.load(f)
        if input_json:
            for game in input_json["GAMES"]:
                news_item = utils.get_news(game)
                discord_post = utils.check_news_db(news_item, input_json)
                if discord_post:
                    requests.post(url=discord_post[0], json=discord_post[1], timeout=3)
        print("STEAM NEWS: Finished")
    except (OSError, json.JSONDecodeError) as e:
        print(e)
        log.error(e, exc_info=True)


if __name__ == "__main__":
    main()
