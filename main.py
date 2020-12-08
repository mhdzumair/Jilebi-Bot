from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask, request
from jilebi import jilebi, send_notification, environ
from telebot.types import Update

server = Flask(__name__)


@server.route('/' + environ.get("JILEBI_TOKEN"), methods=['POST'])
def get_message():
    jilebi.process_new_updates([Update.de_json(request.stream.read().decode("utf-8"))])
    return "POST", 200


@server.route("/")
def web_hook():
    jilebi.remove_webhook()
    jilebi.set_webhook(url='https://jilebibot.herokuapp.com/' + environ.get("JILEBI_TOKEN"))
    return "CONNECTED", 200


def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_notification, IntervalTrigger(minutes=30, timezone="Asia/Colombo"))
    send_notification()
    scheduler.start()
    try:
        server.run(host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        print("Shutdown the bot...")


if __name__ == '__main__':
    main()
