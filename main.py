from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from jilebi import jilebi, send_notification


def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_notification, IntervalTrigger(minutes=30, timezone="Asia/Colombo"))
    send_notification()
    scheduler.start()
    try:
        jilebi.polling(True)
    except KeyboardInterrupt:
        print("Shutdown the bot...")


if __name__ == '__main__':
    main()
