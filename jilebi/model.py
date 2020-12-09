from os import environ
from random import choice
from textwrap import fill, shorten

from PIL import Image, ImageDraw, ImageFont, ImageOps
from arrow import now, get
from httplib2 import HttpLib2Error, Http
from icalevents.icalevents import events
from mongoengine import connect, DoesNotExist

from .db_structer import University, TeleUsers, DoubleEvent, SingleEvent

connect("jilebi", host=environ.get("MONGO_HOST"),
        username=environ.get("MONGO_USER"), password=environ.get("MONGO_PASS"),
        authentication_source='admin')


def get_module_name(module_code):
    modules_list = University.objects.distinct("faculty.division.semester.modules")
    modules_list.append(University.objects.distinct("faculty.semester.modules"))
    modules_dict = {}
    for module in modules_list:
        modules_dict.update(module)
    try:
        return modules_dict[module_code]
    except KeyError:
        return module_code


def format_events(response):
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
        result += "Congratulation! You dont have any work to do. \nEnjoy your self. Cheers!"
    return result


def get_events(chat_id, period, is_user, start=None, end=None):
    if is_user:
        calendar = TeleUsers.objects.only("calendar").get(pk=chat_id).calendar
    else:
        select = TeleUsers.objects.only("selection").get(pk=chat_id).selection
        if select.division:
            calendar = University.objects.only("faculty__name", "faculty__division__name",
                                               "faculty__division__semester").get(
                name=select.university, faculty__name=select.faculty, faculty__division__name=select.division,
                faculty__division__semester__name=select.semester).faculty.get(name=select.faculty).division.get(
                name=select.division).semester.get(name=select.semester).donor_calendar
        else:
            calendar = University.objects.only("faculty__name", "faculty__semester").get(
                name=select.university, faculty__name=select.faculty,
                faculty__semester__name=select.semester).faculty.get(name=select.faculty).semester.get(
                name=select.semester).donor_calendar

    url = f"https://{calendar.domain}/calendar/export_execute.php?userid={calendar.userid}&authtoken=" \
          f"{calendar.token}&preset_what=all&preset_time={period}"
    response = None
    try:
        http = Http('.cache')
    except PermissionError:
        http = Http()
    try:
        response = events(url, http=http, start=start, end=end)
    except (HttpLib2Error, ValueError) as e:
        print("get event error: ", e)
    finally:
        http.close()
    return response


def is_calendar_present(message):
    try:
        if TeleUsers.objects.only("calendar").get(pk=message.chat.id).calendar:
            return True
    except DoesNotExist:
        create_user(message)
    return False


def create_user(message):
    try:
        TeleUsers.objects.only("pk").get(pk=message.chat.id)
    except DoesNotExist:
        if message.chat.username:
            TeleUsers(chat_id=message.chat.id, username=message.chat.username).save()
        else:
            TeleUsers(chat_id=message.chat.id, username=f"{message.chat.first_name} {message.chat.last_name}").save()


def create_double_event(double_events):
    double = DoubleEvent.objects.get(pk=choice(DoubleEvent.objects.distinct("pk")))
    image = Image.open(double.name)
    font1 = ImageFont.truetype(double.font1.name, double.font1.size)
    font2 = ImageFont.truetype(double.font2.name, double.font2.size)
    fonts = (font1, font2)
    place_text(image, double.image1.place, double_events[0], double.image1.size, fonts, double.image1.angle)
    place_text(image, double.image2.place, double_events[1], double.image2.size, fonts, double.image2.angle)
    return image


def create_single_event(event):
    single = SingleEvent.objects.get(pk=choice(SingleEvent.objects.distinct("pk")))
    image = Image.open(single.name)
    font1 = ImageFont.truetype(single.font1.name, single.font1.size)
    font2 = ImageFont.truetype(single.font2.name, single.font2.size)
    place_text(image, single.image.place, event, single.image.size, (font1, font2), single.image.angle)
    return image


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
    text_image = Image.new('L', size)
    start = get(event.start).to("Asia/Colombo")
    end = get(event.end).to("Asia/Colombo")
    date = start.format("Do of MMMM")
    if start == end:
        period = f"Submission end at {end.format('hh:mm A')}"
    else:
        period = f"{start.format('hh:mm A')}    to    {end.format('hh:mm A')}"
    summary = fill(shorten(event.summary.replace("&amp;", "&"), 100, placeholder="..."), 30)
    try:
        title = fill(shorten(get_module_name(event.categories[0]), 50, placeholder="..."), 25)
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
    draw.multiline_text(((size[0] - title_width) / 2, date_height + spacing), title, "#fff", font2, align="center")
    draw.multiline_text((margin, date_height + title_height + spacing * 2), summary, 255, font1)
    draw.text(((size[0] - period_width) / 2, size[1] - period_height - spacing), period, 255, font2, align="center")
    text_image = text_image.rotate(rotate, expand=True)
    image.paste(ImageOps.colorize(text_image, (0, 0, 0), (0, 0, 0)), place, text_image)
    text_image.close()


def format_notification(event):
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
        string += "Duration " + end.humanize(start, granularity=["hour", "minute"], only_distance=True) + "\r\n\r\n"
    return string


def find_half_hour_events(chat_id):
    now_time = now("Asia/Colombo")
    half_hour = now_time.shift(minutes=30)
    response = get_events(chat_id, "weeknow", True, now_time.datetime, half_hour.datetime)
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
    today = now("Asia/Colombo")
    return get_events(chat_id, "weeknow", is_user, today.floor("day").datetime, today.ceil("day").datetime)


def find_tomorrow_events(chat_id, is_user):
    tomorrow = now("Asia/Colombo").shift(days=1)
    if tomorrow.weekday():
        period = "weeknow"
    else:
        period = "weeknext"

    return get_events(chat_id, period, is_user, tomorrow.floor("day").datetime, tomorrow.ceil("day").datetime)


def find_week_events(chat_id, is_user):
    week_start = now("Asia/Colombo").floor("week")
    week_end = week_start.ceil("week")
    return get_events(chat_id, "weeknow", is_user, week_start.datetime, week_end.datetime)


def find_month_events(chat_id, is_user):
    month_start = now("Asia/Colombo").floor("month")
    month_end = month_start.ceil("month")
    return get_events(chat_id, "monthnow", is_user, month_start.datetime, month_end.datetime)


def get_modules(chat_id):
    select = TeleUsers.objects.only("selection").get(pk=chat_id).selection
    if select.division:
        modules = University.objects.only("faculty__name", "faculty__division__name",
                                          "faculty__division__semester").get(
            name=select.university, faculty__name=select.faculty, faculty__division__name=select.division,
            faculty__division__semester__name=select.semester).faculty.get(name=select.faculty).division.get(
            name=select.division).semester.get(name=select.semester).modules
    else:
        modules = University.objects.only("faculty__name", "faculty__semester").get(
            name=select.university, faculty__name=select.faculty,
            faculty__semester__name=select.semester).faculty.get(name=select.faculty).semester.get(
            name=select.semester).modules

    result = "List of Modules\r\n"
    for module in modules.values():
        result += f"★ {module}  \n\n"
    return result
