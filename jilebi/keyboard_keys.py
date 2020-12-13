from telebot.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           ReplyKeyboardRemove,
                           InlineKeyboardButton,
                           InlineKeyboardMarkup)

from .db_structer import TeleUsers, University
from .model import get_semester


class Keyboard:
    def __init__(self, bot):
        """
        Handle all telegram keyboard keys
        :param bot: telebot bot API
        """
        self.jilebi = bot
        self.back_btn = KeyboardButton("Back")
        self.main_menu = KeyboardButton("Main Menu")

    def send_home(self, message):
        reply_markup = ReplyKeyboardMarkup(True, False)
        reply_markup.row("Get Today Events", "Get Tomorrow events")
        reply_markup.row("Get this week events", "Get this month events")
        reply_markup.row("See Other University Students Events")
        reply_markup.row("Extra", "Settings")
        self.jilebi.send_message(message.chat.id, "Select Menu Item", reply_markup=reply_markup)
        TeleUsers.objects(pk=message.chat.id).update(unset__selection=1, position=0)

    def send_settings(self, message):
        reply_markup = ReplyKeyboardMarkup()
        user = TeleUsers.objects.only("is_image_result", "calendar", "is_subscriber").get(pk=message.chat.id)
        reply_markup.row("Setup moodle calender link")
        if user.calendar:
            reply_markup.add("Check my moodle calendar link")
        if user.is_subscriber:
            reply_markup.row("Unsubscribe Notification")
        else:
            reply_markup.row("Subscribe auto Notification")
        if user.is_image_result:
            reply_markup.row("Get Text based result")
        else:
            reply_markup.row("Get Image based result")
        reply_markup.add(self.main_menu)
        self.jilebi.send_message(message.chat.id, "Select Setting item", reply_markup=reply_markup)

    def send_university(self, message):
        reply_markup = ReplyKeyboardMarkup(True, False, row_width=2)
        reply_markup.add(*[KeyboardButton(uni) for uni in University.objects.distinct("name")])
        reply_markup.add(self.back_btn)
        self.jilebi.send_message(message.chat.id, "Select a university", reply_markup=reply_markup)
        TeleUsers.objects(pk=message.chat.id).update(position=1)

    def send_faculty(self, message):
        user = TeleUsers.objects.only("selection").get(pk=message.chat.id)
        reply_markup = ReplyKeyboardMarkup(True, False, row_width=2)
        faculties = University.objects.only("faculty__name").get(name=user.selection.university).faculty
        reply_markup.add(*[KeyboardButton(faculty.name) for faculty in faculties])
        reply_markup.add(self.back_btn, self.main_menu)
        self.jilebi.send_message(message.chat.id, "Select the Faculty", reply_markup=reply_markup)
        user.update(position=2)

    def send_division(self, message):
        user = TeleUsers.objects.only("selection").get(pk=message.chat.id)
        reply_markup = ReplyKeyboardMarkup(True, False, row_width=2)
        divisions = University.objects.only("faculty__name", "faculty__division__name").get(
            name=user.selection.university, faculty__name=user.selection.faculty).faculty.get(
            name=user.selection.faculty).division
        reply_markup.add(*[KeyboardButton(division.name) for division in divisions])
        reply_markup.add(self.back_btn, self.main_menu)
        self.jilebi.send_message(message.chat.id, "Select the Division", reply_markup=reply_markup)
        user.update(position=3)

    def send_semester(self, message):
        user = TeleUsers.objects.only("selection").get(pk=message.chat.id)
        reply_markup = ReplyKeyboardMarkup(True, False, row_width=2)
        if user.selection.division:
            semesters = University.objects.only("faculty__name", "faculty__division__name",
                                                "faculty__division__semester__name").get(
                name=user.selection.university, faculty__name=user.selection.faculty,
                faculty__division__name=user.selection.division).faculty.get(
                name=user.selection.faculty).division.get(name=user.selection.division).semester
        else:
            semesters = University.objects.only("faculty__name", "faculty__division__name").get(
                name=user.selection.university, faculty__name=user.selection.faculty).faculty.get(
                name=user.selection.faculty).semester

        reply_markup.add(*[KeyboardButton(semester.name) for semester in semesters])
        reply_markup.add(self.back_btn, self.main_menu)
        self.jilebi.send_message(message.chat.id, "Select a semester", reply_markup=reply_markup)
        user.update(position=4)

    def send_others_menu(self, message):
        semester = get_semester(message.chat.id)
        reply_markup = ReplyKeyboardMarkup()
        if semester.donor_calendar:
            reply_markup.row("Today Events", "Tomorrow events")
            reply_markup.row("This week events", "This month events")
            self.jilebi.send_message(message.chat.id, f"Link Donate by: {semester.donor_name}",
                                     reply_markup=ReplyKeyboardRemove())
        else:
            self.jilebi.send_message(message.chat.id, "If you're a student of this course, please contact me to "
                                                      "donate your link.")
        reply_markup.row("Modules list")
        reply_markup.row(self.back_btn, self.main_menu)
        self.jilebi.send_message(message.chat.id, "Select Item: ", reply_markup=reply_markup)
        TeleUsers.objects(pk=message.chat.id).update(position=5)

    def send_extras(self, message):
        reply_markup = ReplyKeyboardMarkup()
        reply_markup.row("Submit your module details")
        reply_markup.row("Send Queries/Feedbacks", "Source Code")
        reply_markup.row("Share Jilebi", self.main_menu)
        self.jilebi.send_message(message.chat.id, "Select Item: ", reply_markup=reply_markup)

    def ask_division(self, message):
        reply_markup = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        reply_markup.row("Yes", "No")
        self.jilebi.send_message(message.chat.id, "Are you have Divisions / Department inside your faculty?",
                                 reply_markup=reply_markup)
