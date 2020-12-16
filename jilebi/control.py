from os import environ

from arrow import now
from telebot import TeleBot, apihelper
from telebot.util import split_string

from .db_structer import TeleUsers, Calendar, University, UserSelection
from .keyboard_keys import Keyboard, ReplyKeyboardRemove
from .model import (create_image, format_events, find_half_hour_events, create_user,
                    is_calendar_present, find_today_events, find_tomorrow_events, find_week_events, find_month_events,
                    get_modules)


class ExceptionHandler(Exception):
    def handle(self):
        print(f"Logging: {now('Asia/Colombo').format('hh:mm A Do of MMM ')} : {self.args[-1]}")
        return True


jilebi = TeleBot(environ.get("JILEBI_TOKEN"), exception_handler=ExceptionHandler)
keyboard = Keyboard(jilebi)


def send_image(result, chat_id):
    if result:
        for count in range(0, len(result) - 1, 2):
            jilebi.send_photo(chat_id, create_image(result[count:count + 2]))
        if len(result) % 2 == 1:
            jilebi.send_photo(chat_id, create_image(result[-1]))
    else:
        jilebi.send_message(chat_id, "Congratulation! You dont have any work to do. \nEnjoy your self. Cheers!")


def send_message(response, chat_id):
    for text in split_string(format_events(response), 3000):
        jilebi.send_message(chat_id, text)


def send_notification():
    print("check auto notification time: ", now().format('hh:mm A'))
    subscribers = TeleUsers.objects(is_subscriber=True).distinct("pk")
    for subscriber in subscribers:
        notification = find_half_hour_events(subscriber)
        if notification:
            try:
                jilebi.send_message(subscriber, notification)
            except apihelper.ApiTelegramException as e:
                if e.error_code == 403:
                    TeleUsers.objects(pk=subscriber).delete()


def handle_all_results(result, chat_id):
    if isinstance(result, list):
        if TeleUsers.objects.only("is_image_result").get(pk=chat_id).is_image_result:
            send_image(result, chat_id)
        else:
            send_message(result, chat_id)
    else:
        jilebi.reply_to(chat_id,
                        "We are extremely sorry!\nAt the moment we cannot get your calendar.\nplease try again...")


@jilebi.message_handler(commands=["start", "reset", "restart"])
def send_welcome(message):
    create_user(message)
    text = f"""
Hey {message.chat.last_name if message.chat.last_name else message.chat.first_name}, Welcome to Jilebi Bot.
This bot is for viewing Universities schedules.


            Features
* View schedule by period of days(today, tomorrow, etc...).

* Subscribe to Auto Notification to get reminder on event within half hour.

* Get image based of text based result.

* if you don't know what is calender link, please enter /tutorial to see the tutorial.

* If you have any doubt or feedback or feature implementation ideas, please feel free to DM
"""

    jilebi.send_message(message.chat.id, text)
    cancel_process(message)


@jilebi.message_handler(commands=["tutorial"])
def send_tutorial(message):
    jilebi.send_video(message.chat.id, "BAACAgUAAxkBAAICxF_IZo9v1LxfzBSGpj5Ytk1n_WDuAAI8AgACOYNIVvzCpN04fH0rHgQ",
                      52, "tutorial for parsing calendar link")


@jilebi.message_handler(commands=["cancel"])
def cancel_process(message):
    user = TeleUsers.objects.get(pk=message.chat.id)
    if user.submit:
        jilebi.send_message(message.chat.id, "successfully cancel the module submission.")
    elif user.feedback:
        jilebi.send_message(message.chat.id, "successfully cancel the feedback.")

    user.update(unset__user_submit=1, unset__submit_position=1, submit=False, feedback=False)
    keyboard.send_home(message)


@jilebi.message_handler(func=lambda message: message.text == "Get Today Events")
def send_user_today_event(message):
    if not is_calendar_present(message):
        jilebi.send_message(message.chat.id, "Sorry you need to setup calendar link first")
        return

    result = find_today_events(message.chat.id, True)
    handle_all_results(result, message.chat.id)


@jilebi.message_handler(func=lambda message: message.text == "Get Tomorrow events")
def send_user_tomorrow_event(message):
    if not is_calendar_present(message):
        jilebi.send_message(message.chat.id, "Sorry you need to setup calendar link first")
        return

    handle_all_results(find_tomorrow_events(message.chat.id, True), message.chat.id)


@jilebi.message_handler(func=lambda message: message.text == "Get this week events")
def send_user_week_event(message):
    if not is_calendar_present(message):
        jilebi.send_message(message.chat.id, "Sorry you need to setup calendar link first")
        return

    handle_all_results(find_week_events(message.chat.id, True), message.chat.id)


@jilebi.message_handler(func=lambda message: message.text == "Get this month events")
def send_user_month_event(message):
    if not is_calendar_present(message):
        jilebi.send_message(message.chat.id, "Sorry you need to setup calendar link first")
        return

    handle_all_results(find_month_events(message.chat.id, True), message.chat.id)


@jilebi.message_handler(func=lambda message: message.text == "Settings")
def send_setting(message):
    keyboard.send_settings(message)


@jilebi.message_handler(func=lambda message: message.text == "Setup moodle calender link")
def setup_link(message):
    send_tutorial(message)
    jilebi.send_message(message.chat.id, "Type Your University calendar url", reply_markup=ReplyKeyboardRemove())


@jilebi.message_handler(func=lambda message: message.text == "Send Queries/Feedbacks")
def get_feedback(message):
    markup = ReplyKeyboardRemove()
    jilebi.send_message(message.chat.id, "Enter your message now.\nThis message will send to @Mohamed_Zumair",
                        reply_markup=markup)
    TeleUsers.objects(pk=message.chat.id).update(feedback=True)


@jilebi.message_handler(func=lambda message: message.text == "Check my moodle calendar link")
def check_link(message):
    calendar = TeleUsers.objects.only("calendar").get(pk=message.chat.id).calendar
    if calendar:
        url = f"https://{calendar.domain}/calendar/export_execute.php?userid={calendar.userid}&authtoken=" \
              f"{calendar.token}&preset_what=all&preset_time=monthnow"
        jilebi.send_message(message.chat.id, "Your URL: \n" + url)
    else:
        jilebi.send_message(message.chat.id, "Sorry you dont have calendar link")


@jilebi.message_handler(func=lambda message: message.text == "Subscribe auto Notification")
def set_subscribe(message):
    if not is_calendar_present(message):
        jilebi.send_message(message.chat.id, "Sorry you need to setup calendar link first")
        return

    TeleUsers.objects(pk=message.chat.id).update(is_subscriber=True)
    jilebi.reply_to(message, "successfully subscribe to get notification before 30 of an event")
    keyboard.send_settings(message)


@jilebi.message_handler(func=lambda message: message.text == "Unsubscribe Notification")
def set_unsubscribe(message):
    TeleUsers.objects(pk=message.chat.id).update(is_subscriber=False)
    jilebi.reply_to(message, "successfully unsubscribe the notification")
    keyboard.send_settings(message)


@jilebi.message_handler(func=lambda message: message.text is not None and (
        "https://" and "userid" and "authtoken") in message.text)
def link_parser(message):
    url = message.text
    try:
        queries = url.split("?")[1]
        calendar = Calendar()
        calendar.domain = url.split("/")[2]
        calendar.userid = queries.split("&")[0].split("=")[1]
        calendar.token = queries.split("&")[1].split("=")[1]
        TeleUsers.objects.only("calendar").get(pk=message.chat.id).update(calendar=calendar)
        jilebi.reply_to(message, "Successfully saved your link")
        set_subscribe(message)
        send_setting(message)
    except [IndexError, TypeError]:
        jilebi.reply_to(message, f"sorry, i can't understand you url: {url}\nplease your problem to admin")


@jilebi.message_handler(func=lambda message: message.text == "See Other University Students Events")
def send_university(message):
    keyboard.send_university(message)


@jilebi.message_handler(func=lambda message: message.text in University.objects.distinct("name"))
def send_faculty(message):
    TeleUsers.objects(pk=message.chat.id).update(selection__university=message.text)
    keyboard.send_faculty(message)


@jilebi.message_handler(func=lambda message: message.text in University.objects.distinct("faculty.name"))
def send_division(message):
    user = TeleUsers.objects.get(pk=message.chat.id)
    user.update(selection__faculty=message.text)
    if University.objects(name=user.selection.university, faculty__name=user.selection.faculty).count:
        keyboard.send_division(message)
    else:
        send_semester(message)


@jilebi.message_handler(func=lambda message: message.text in University.objects.distinct("faculty.division.name"))
def send_semester(message):
    TeleUsers.objects(pk=message.chat.id).update(selection__division=message.text)
    keyboard.send_semester(message)


@jilebi.message_handler(func=lambda message: message.text in University.objects.distinct(
    "faculty.division.semester.name") or message.text in University.objects.distinct("faculty.semester.name"))
def send_others_menu(message):
    TeleUsers.objects(pk=message.chat.id).update(selection__semester=message.text)
    keyboard.send_others_menu(message)


@jilebi.message_handler(func=lambda message: message.text == "Today Events")
def send_today_event(message):
    handle_all_results(find_today_events(message.chat.id, False), message.chat.id)


@jilebi.message_handler(func=lambda message: message.text == "Tomorrow events")
def send_tomorrow_event(message):
    handle_all_results(find_tomorrow_events(message.chat.id, False), message.chat.id)


@jilebi.message_handler(func=lambda message: message.text == "This week events")
def send_week_event(message):
    handle_all_results(find_week_events(message.chat.id, False), message.chat.id)


@jilebi.message_handler(func=lambda message: message.text == "This month events")
def send_month_event(message):
    handle_all_results(find_month_events(message.chat.id, False), message.chat.id)


@jilebi.message_handler(func=lambda message: message.text == "Modules list")
def send_module_list(message):
    jilebi.send_message(message.chat.id, get_modules(message.chat.id))


@jilebi.message_handler(func=lambda message: message.text == "Get Text based result")
def set_text_based(message):
    TeleUsers.objects(pk=message.chat.id).update(is_image_result=False)
    jilebi.reply_to(message, "Successfully setup for Text based result.")
    send_setting(message)


@jilebi.message_handler(func=lambda message: message.text == "Get Image based result")
def set_image_based(message):
    TeleUsers.objects(pk=message.chat.id).update(is_image_result=True)
    jilebi.reply_to(message, "Successfully setup for Image based result.")
    send_setting(message)


@jilebi.message_handler(func=lambda message: message.text == "Main Menu")
def send_to_main(message):
    keyboard.send_home(message)


@jilebi.message_handler(func=lambda message: message.text == "Back")
def send_back(message):
    position = TeleUsers.objects.only("position").get(pk=message.chat.id).position
    if position == 1:
        keyboard.send_home(message)
        TeleUsers.objects(pk=message.chat.id).update(unset__selection=1)
    elif position == 2:
        keyboard.send_university(message)
        TeleUsers.objects(pk=message.chat.id).update(unset__selection__faculty=1)
    elif position == 3:
        keyboard.send_faculty(message)
        TeleUsers.objects(pk=message.chat.id).update(unset__selection__division=1)
    elif position == 4:
        if TeleUsers.objects.only("selection__division").get(pk=message.chat.id).selection.division:
            keyboard.send_division(message)
        else:
            keyboard.send_faculty(message)
        TeleUsers.objects(pk=message.chat.id).update(unset__selection__semester=1)
    elif position == 5:
        keyboard.send_semester(message)
    else:
        jilebi.send_message(message.chat.id, "Sorry, we lost the trace!\r\nRedirecting to Main Menu")
        keyboard.send_home(message)


@jilebi.message_handler(func=lambda message: message.text == "Extra")
def send_extra_menu(message):
    keyboard.send_extras(message)


@jilebi.message_handler(func=lambda message: message.text == "Submit your module details")
def submit_module_details(message):
    jilebi.send_message(message.chat.id, "What is your university name: \nexample: University of Moratuwa",
                        reply_markup=ReplyKeyboardRemove())
    TeleUsers.objects(pk=message.chat.id).update(submit=True, submit_position=0)


@jilebi.message_handler(func=lambda message: message.text == "Share Jilebi")
def share_jilebi(message):
    jilebi.send_message(message.chat.id, "Thanks for sharing Jilebi\n"
                                         "Share this URL: https://t.me/JilebiBot")


@jilebi.message_handler(func=lambda message: message.text == "Source Code")
def send_source_code(message):
    jilebi.send_message(message.chat.id, "Thanks for giving time to see my code!\nPlease give me support\n"
                                         "https://github.com/mhdzumair/Jilebi-Bot")


@jilebi.message_handler(func=lambda message: (message.text == "Yes" or message.text == "No") and TeleUsers.objects.only(
    "submit_position").get(pk=message.chat.id).submit_position == 1)
def get_answer(message):
    if message.text == "Yes":
        jilebi.send_message(message.chat.id, "What is your division / department name: \nExample: IT",
                            reply_markup=ReplyKeyboardRemove())
        TeleUsers.objects(pk=message.chat.id).update(submit_position=2)
    elif message.text == "No":
        jilebi.send_message(message.chat.id, "What is your Semester name:\nExample Semester 4",
                            reply_markup=ReplyKeyboardRemove())
        TeleUsers.objects(pk=message.chat.id).update(submit_position=3)


@jilebi.message_handler(content_types=["sticker"])
def handle_sticker(message):
    jilebi.send_sticker(message.chat.id, message.sticker.file_id)


@jilebi.message_handler(func=lambda message: True)
def handle_all(message):
    if TeleUsers.objects.only("submit").get(pk=message.chat.id).submit:
        handle_submission(message)
    elif TeleUsers.objects.only("feedback").get(pk=message.chat.id).feedback:
        jilebi.send_message("606319743", f"This message is from {message.chat.first_name} {message.chat.last_name}. "
                                         f"chat id: {message.chat.id}")
        jilebi.forward_message("606319743", message.chat.id, message.message_id)
        jilebi.reply_to(message, "Thanks for your valuable feedback. we will get back you soon!")
        keyboard.send_home(message)
        TeleUsers.objects(pk=message.chat.id).update(feedback=False)
    else:
        jilebi.reply_to(message, "Sorry wrong input!")


def handle_submission(message):
    user = TeleUsers.objects.only("submit_position", "user_submit").get(pk=message.chat.id)

    if user.submit_position == 0:
        jilebi.send_message(message.chat.id, "What is your faculty name: \nExample: NDT")
        submission = UserSelection()
        submission.university = message.text
        user.update(user_submit=submission, submit_position=1)
    elif user.submit_position == 1:
        keyboard.ask_division(message)
        user.update(user_submit__faculty=message.text)
    elif user.submit_position == 2:
        jilebi.send_message(message.chat.id, "What is your Semester name:\nExample Semester 4")
        user.update(user_submit__division=message.text, submit_position=3)
    elif user.submit_position == 3:
        text = """
What are the modules you have?

Example: send it like this

(Module Code) : (Module Name)
In19-S04-IT2401 : Business Intelligence and Analytics,
In19-S04-IT2402 : Cloud Computing,
In19-S04-IT2403 : Digital Marketing,
In19-S04-IT2404 : Intelligent Systems & Machine Learning,
In19-S04-IT2405 : Internet of Things,
In19-S04-IT2406 : Mobile Communication,
In19-S04-IT2407 : Project II,
In19-S04-IT2408 : Software Testing & Quality Controlling,
In19-S04-IS2401 : Communication Skills and Technical Writing,
In19-S04-IS2402 : Industrial Statistics and Modelling Computation

module code format:

In(Your university entered year)-(Your Semester number)-(Module code)
"""
        jilebi.send_message(message.chat.id, text)
        user.update(user_submit__semester=message.text, submit_position=6)
    else:
        jilebi.send_message(message.chat.id, "Thank you for submitting your module details.\n"
                                             "We will review and update our database ASAP!")
        keyboard.send_extras(message)
        jilebi.forward_message("606319743", message.chat.id, message.message_id)
        text = f"""
university: {user.user_submit.university}
faculty: {user.user_submit.faculty}
division: {user.user_submit.division}
semester: {user.user_submit.semester}
        """
        jilebi.send_message("606319743", text)
        user.update(unset__user_submit=1, unset__submit_position=1, submit=False)
