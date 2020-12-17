"""
  Copyright (c) 2020 Mohamed Zumair <mhdzumair@gmail.com>.

  This file is part of Jilebi-Bot.

  Jilebi-Bot is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or any later version.

  Jilebi-Bot is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from os import environ

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask, request, jsonify
from telebot.types import Update

from jilebi import jilebi, send_notification, TeleUsers

server = Flask(__name__)


@server.route("/" + environ.get("JILEBI_TOKEN"), methods=["POST"])
def get_message():
    jilebi.process_new_updates([Update.de_json(request.stream.read().decode("utf-8"))])
    return "POST", 200


@server.route("/")
def web_hook():
    jilebi.remove_webhook()
    jilebi.set_webhook(
        url="https://jilebibot.herokuapp.com/" + environ.get("JILEBI_TOKEN")
    )
    return "CONNECTED", 200


@server.route("/get_user_count", methods=["GET"])
def get_user_count():
    return jsonify(count=TeleUsers.objects.count())


def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_notification, IntervalTrigger(minutes=30, timezone="Asia/Colombo")
    )
    send_notification()
    scheduler.start()
    try:
        server.run(host="0.0.0.0", port=environ.get("PORT", 5000))
    except KeyboardInterrupt:
        print("Shutdown the bot...")


if __name__ == "__main__":
    main()
