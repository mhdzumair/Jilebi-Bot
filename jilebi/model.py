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
from random import choice
from textwrap import fill, shorten

from PIL import Image, ImageDraw, ImageFont, ImageOps
from arrow import now, get
from httplib2 import HttpLib2Error, Http
from icalevents.icalevents import events
from mongoengine import connect, DoesNotExist

from .db_structer import University, TeleUsers, DoubleEvent, SingleEvent

connect(
    "jilebi",
    host=environ.get("MONGO_HOST"),
    username=environ.get("MONGO_USER"),
    password=environ.get("MONGO_PASS"),
    authentication_source="admin",
)


def get_module_name(module_code):
    """
    Get the module name for the module_code
    :param module_code: code name of the module which is retrieved from event.categories[0]
    :return: if the module name was in the database then module name will return or else module_code will return
    """
    modules_list = University.objects.distinct("faculty.division.semester.modules")
    modules_list.append(*University.objects.distinct("faculty.semester.modules"))
    modules_dict = {}
    for module in modules_list:
        modules_dict.update(module)
    try:
        return modules_dict[module_code]
    except KeyError:
        return module_code


def get_semester(chat_id):
    """
    Get the semester data
    :param chat_id: telegram user id
    :return: Semester
    """
    select = TeleUsers.objects.only("selection").get(pk=chat_id).selection
    if select.division:
        semester = (
            University.objects.only(
                "faculty__name",
                "faculty__division__name",
                "faculty__division__semester",
            )
            .get(name=select.university)
            .faculty.get(name=select.faculty)
            .division.get(name=select.division)
            .semester.get(name=select.semester)
        )
    else:
        semester = (
            University.objects.only("faculty__name", "faculty__semester")
            .get(name=select.university)
            .faculty.get(name=select.faculty)
            .semester.get(name=select.semester)
        )
    return semester


def format_events(response):
    """
    Format calendar events properties to string
    :param response: calendar events (icalevents.icalparser.Event)
    :return: formatted result (string)
    """
    result = ""
    if response:
        for event in response:
            start = get(event.start).to("Asia/Colombo")
            end = get(event.end).to("Asia/Colombo")
            result += "Date: " + start.format("Do of MMMM") + "\r\n"
            try:
                result += "Module: " + get_module_name(event.categories[0]) + "\r\n"
            except TypeError:
                pass

            result += "Name: " + event.summary.strip().replace("&amp;", "&") + "\r\n"
            if event.start == event.end:
                result += "Submission End at: " + end.format("hh:mm A") + "\r\n\r\n"
            else:
                result += "Start at: " + start.format("hh:mm A") + "\r\n"
                result += "End at: " + end.format("hh:mm A") + "\r\n\r\n"
    else:
        result += (
            "Congratulation! You dont have any work to do. \nEnjoy your self. Cheers!"
        )
    return result


def get_events(chat_id, period, is_user, start=None, end=None):
    """
    Get the events from Moodle calendar API
    :param chat_id: Telegram user id
    :param period: Moodle calendar preset_time ["weeknow", "weeknext", "monthnow", "monthnext"]
    :param is_user: check if this get_events for user's events or other's events
    :param start: events start datetime / date
    :param end: evets end datetime / date
    :return: calendar events (icalevents.icalparser.Event)
    """
    if is_user:
        calendar = TeleUsers.objects.only("calendar").get(pk=chat_id).calendar
    else:
        calendar = get_semester(chat_id).donor_calendar

    url = (
        f"{calendar.domain}/calendar/export_execute.php?userid={calendar.userid}&authtoken="
        f"{calendar.token}&preset_what=all&preset_time={period}"
    )
    response = None
    try:
        http = Http(".cache", timeout=20)
    except PermissionError:
        http = Http(timeout=20)
    try:
        response = events(url, http=http, start=start, end=end)
    except (HttpLib2Error, ValueError, TimeoutError, ConnectionRefusedError):
        pass
    finally:
        http.close()
    return response


def is_calendar_present(message):
    """
    check whether user setup the calendar link
    :param message: message from user
    :return: (boolean)
    """
    try:
        if TeleUsers.objects.only("calendar").get(pk=message.chat.id).calendar:
            return True
    except DoesNotExist:
        create_user(message)
    return False


def create_user(message):
    """
    Create a new user data
    :param message: message from user
    """
    try:
        TeleUsers.objects.only("pk").get(pk=message.chat.id)
    except DoesNotExist:
        if message.chat.username:
            TeleUsers(chat_id=message.chat.id, username=message.chat.username).save()
        else:
            TeleUsers(
                chat_id=message.chat.id,
                username=f"{message.chat.first_name} {message.chat.last_name}",
            ).save()


def place_text(image, place, event, size, fonts, rotate):
    """
    Function for placing event details in given image

    :param event: ical event object
    :param image: PIL image object
    :param place: text image placement coordination (tuple)
    :param size: text image size (tuple)
    :param fonts: two fonts for writing
    :param rotate: angel of rotate
    """
    text_image = Image.new("L", size)
    start = get(event.start).to("Asia/Colombo")
    end = get(event.end).to("Asia/Colombo")
    date = start.format("Do of MMMM")
    if start == end:
        period = f"Submission end at {end.format('hh:mm A')}"
    else:
        period = f"{start.format('hh:mm A')}    to    {end.format('hh:mm A')}"
    summary = fill(
        shorten(event.summary.replace("&amp;", "&"), 100, placeholder="..."), 30
    )
    try:
        title = fill(
            shorten(get_module_name(event.categories[0]), 50, placeholder="..."), 25
        )
    except TypeError:
        title = ""

    font1, font2 = fonts
    period_width, period_height = font2.getsize(period)
    title_width, title_height = font2.getsize_multiline(title)
    date_width, date_height = font1.getsize(date)
    margin = 10
    spacing = 40

    draw = ImageDraw.Draw(text_image)
    draw.text((size[0] - date_width - margin, margin), date, 255, font1)
    draw.multiline_text(
        ((size[0] - title_width) / 2, date_height + spacing),
        title,
        "#fff",
        font2,
        align="center",
    )
    draw.multiline_text(
        (margin, date_height + title_height + spacing * 2), summary, 255, font1
    )
    draw.text(
        ((size[0] - period_width) / 2, size[1] - period_height - spacing),
        period,
        255,
        font2,
        align="center",
    )
    text_image = text_image.rotate(rotate, expand=True)
    image.paste(ImageOps.colorize(text_image, (0, 0, 0), (0, 0, 0)), place, text_image)
    text_image.close()


def create_image(event):
    """
    Create image for users events
    :param event: single event or double event (event / [event, event])
    :return: Image file with placed events
    """
    if isinstance(event, list):
        photo = DoubleEvent.objects.get(pk=choice(DoubleEvent.objects.distinct("pk")))
    else:
        photo = SingleEvent.objects.get(pk=choice(SingleEvent.objects.distinct("pk")))

    image = Image.open(photo.name)
    font1 = ImageFont.truetype(photo.font1.name, photo.font1.size)
    font2 = ImageFont.truetype(photo.font2.name, photo.font2.size)
    fonts = (font1, font2)
    if isinstance(event, list):
        place_text(
            image,
            photo.image1.place,
            event[0],
            photo.image1.size,
            fonts,
            photo.image1.angle,
        )
        place_text(
            image,
            photo.image2.place,
            event[1],
            photo.image2.size,
            fonts,
            photo.image2.angle,
        )
    else:
        place_text(
            image,
            photo.image.place,
            event,
            photo.image.size,
            (font1, font2),
            photo.image.angle,
        )
    return image


def format_notification(event):
    """
    Format the Reminder notification
    :param event: events to be held within half an hour
    :return: formatted events string
    """
    string = "You have "
    string += event.summary.strip().replace("&amp;", "&") + "\r\n"
    try:
        string += "Module: " + get_module_name(event.categories[0]) + "\r\n"
    except TypeError:
        pass
    end = get(event.end).to("Asia/Colombo")
    if event.start == event.end:
        string += "Submission will end " + end.humanize() + "\r\n\r\n"
    else:
        start = get(event.start).to("Asia/Colombo")
        string += "Start " + start.humanize() + "\r\n"
        string += (
            "Duration "
            + end.humanize(start, granularity=["hour", "minute"], only_distance=True)
            + "\r\n\r\n"
        )
    return string


def find_half_hour_events(chat_id):
    """
    Find events to be held within half an hour
    :param chat_id: telegram user id
    :return: notification (string) / None
    """
    now_time = now("Asia/Colombo")
    half_hour = now_time.shift(minutes=30)
    response = get_events(
        chat_id, "weeknow", True, now_time.datetime, half_hour.datetime
    )
    if response:
        notification = "\t\tREMINDER\r\n"
        event_exist = False
        for event in response:
            if now_time < get(event.start).to("Asia/Colombo") < half_hour:
                notification += format_notification(event)
                event_exist = True

        if event_exist:
            return notification

    return None


def find_today_events(chat_id, is_user):
    """
    Find user's & other's today events
    :param chat_id: telegram user id (int / string)
    :param is_user: (Boolean)
    :return: Today events
    """
    today = now("Asia/Colombo")
    return get_events(
        chat_id,
        "weeknow",
        is_user,
        today.floor("day").datetime,
        today.ceil("day").datetime,
    )


def find_tomorrow_events(chat_id, is_user):
    """
    Find user's & other's tomorrow events
    :param chat_id: telegram user id (int / string)
    :param is_user: (Boolean)
    :return: Tomorrow events
    """
    tomorrow = now("Asia/Colombo").shift(days=1)
    if tomorrow.weekday():
        period = "weeknow"
    else:
        period = "weeknext"

    return get_events(
        chat_id,
        period,
        is_user,
        tomorrow.floor("day").datetime,
        tomorrow.ceil("day").datetime,
    )


def find_week_events(chat_id, is_user):
    """
    Find user's & other's week events
    :param chat_id: telegram user id (int / string)
    :param is_user: (Boolean)
    :return: Week events
    """
    week_start = now("Asia/Colombo").floor("week")
    week_end = week_start.ceil("week")
    return get_events(
        chat_id, "weeknow", is_user, week_start.datetime, week_end.datetime
    )


def find_month_events(chat_id, is_user):
    """
    Find user's & other's month events
    :param chat_id: telegram user id (int / string)
    :param is_user: (Boolean)
    :return: Month events
    """
    month_start = now("Asia/Colombo").floor("month")
    month_end = month_start.ceil("month")
    return get_events(
        chat_id, "monthnow", is_user, month_start.datetime, month_end.datetime
    )


def get_modules(chat_id):
    """
    Get the modules list
    :param chat_id: (int / String)
    :return: formatted modules list (String)
    """
    modules = get_semester(chat_id).modules

    result = "List of Modules\r\n"
    for module in modules.values():
        result += f"★ {module}  \n\n"
    return result
