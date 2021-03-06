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

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from .db_structer import TeleUsers, University
from .model import get_semester


class Keyboard:
    def __init__(self, bot):
        """
        Handle all telegram keyboard keys
        :param bot: telebot bot API
        attributes:
            back_btn : KeyboardMarkup Button for back
            main_menu: KeyboardMarkup Button for main menu
        """

        self.jilebi = bot
        self.back_btn = KeyboardButton("🔙 Back")
        self.main_menu = KeyboardButton("🔝 Main Menu")

    def send_home(self, message):
        reply_markup = ReplyKeyboardMarkup(True, False)
        reply_markup.row("Get Today Events", "Get Tomorrow events")
        reply_markup.row("Get this week events", "Get next week events")
        reply_markup.row("Get this month events", "Other's Events")
        reply_markup.row("Extra's", "⚙️ Settings")
        self.jilebi.send_message(
            message.chat.id, "Select Menu Item", reply_markup=reply_markup
        )
        TeleUsers.objects(pk=message.chat.id).update(unset__selection=1, position=0)

    def send_settings(self, message):
        reply_markup = ReplyKeyboardMarkup(row_width=2)
        user = TeleUsers.objects.only(
            "is_image_result", "calendar", "is_subscriber"
        ).get(pk=message.chat.id)
        buttons = ["🔗 Setup moodle calender link"]
        if user.calendar:
            buttons.append("🔗 Check my moodle calendar link")
        if user.is_subscriber:
            buttons.append("🔕 Unsubscribe Notification")
        else:
            buttons.append("🔔 Subscribe auto Notification")
        if user.is_image_result:
            buttons.append("📝 Get Text based result")
        else:
            buttons.append("🖼 Get Image based result")
        reply_markup.add(*[KeyboardButton(button) for button in buttons])
        reply_markup.row(self.main_menu)
        self.jilebi.send_message(
            message.chat.id, "Select Setting item", reply_markup=reply_markup
        )

    def send_university(self, message):
        reply_markup = ReplyKeyboardMarkup(True, False, row_width=2)
        reply_markup.add(
            *[KeyboardButton(uni) for uni in University.objects.distinct("name")]
        )
        reply_markup.add(self.back_btn)
        self.jilebi.send_message(
            message.chat.id, "Select a university", reply_markup=reply_markup
        )
        TeleUsers.objects(pk=message.chat.id).update(position=1)

    def send_faculty(self, message):
        user = TeleUsers.objects.only("selection").get(pk=message.chat.id)
        reply_markup = ReplyKeyboardMarkup(True, False, row_width=2)
        faculties = (
            University.objects.only("faculty__name")
            .get(name=user.selection.university)
            .faculty
        )
        reply_markup.add(*[KeyboardButton(faculty.name) for faculty in faculties])
        reply_markup.add(self.back_btn, self.main_menu)
        self.jilebi.send_message(
            message.chat.id, "Select the Faculty", reply_markup=reply_markup
        )
        user.update(position=2)

    def send_division(self, message):
        user = TeleUsers.objects.only("selection").get(pk=message.chat.id)
        reply_markup = ReplyKeyboardMarkup(True, False, row_width=2)
        divisions = (
            University.objects.only("faculty__name", "faculty__division__name")
            .get(name=user.selection.university)
            .faculty.get(name=user.selection.faculty)
            .division
        )
        reply_markup.add(*[KeyboardButton(division.name) for division in divisions])
        reply_markup.add(self.back_btn, self.main_menu)
        self.jilebi.send_message(
            message.chat.id, "Select the Division", reply_markup=reply_markup
        )
        user.update(position=3)

    def send_semester(self, message):
        user = TeleUsers.objects.only("selection").get(pk=message.chat.id)
        reply_markup = ReplyKeyboardMarkup(True, False, row_width=2)
        if user.selection.division:
            semesters = (
                University.objects.only(
                    "faculty__name",
                    "faculty__division__name",
                    "faculty__division__semester__name",
                )
                .get(name=user.selection.university)
                .faculty.get(name=user.selection.faculty)
                .division.get(name=user.selection.division)
                .semester
            )
        else:
            semesters = (
                University.objects.only("faculty__name", "faculty__semester__name")
                .get(name=user.selection.university)
                .faculty.get(name=user.selection.faculty)
                .semester
            )

        reply_markup.add(*[KeyboardButton(semester.name) for semester in semesters])
        reply_markup.add(self.back_btn, self.main_menu)
        self.jilebi.send_message(
            message.chat.id, "Select a semester", reply_markup=reply_markup
        )
        user.update(position=4)

    def send_others_menu(self, message):
        semester = get_semester(message.chat.id)
        reply_markup = ReplyKeyboardMarkup()
        buttons = []
        if semester.donor_calendar:
            buttons.extend(["Today Events", "Tomorrow events", "This week events", "Next week events",
                            "This month events"])
            self.jilebi.send_message(
                message.chat.id,
                f"Link Donate by: {semester.donor_name}",
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            self.jilebi.send_message(
                message.chat.id,
                "If you're a student of this course, please contact me to "
                "donate your link.",
            )
        buttons.append("Modules list")
        reply_markup.add(*[KeyboardButton(button) for button in buttons])
        reply_markup.row(self.back_btn, self.main_menu)
        self.jilebi.send_message(
            message.chat.id, "Select Item: ", reply_markup=reply_markup
        )
        TeleUsers.objects(pk=message.chat.id).update(position=5)

    def send_extras(self, message):
        reply_markup = ReplyKeyboardMarkup()
        reply_markup.row("Submit your module details", "Send Queries/Feedbacks")
        reply_markup.row("🎁 Share Jilebi", "👨🏻‍💻 Source Code", "Users Count")
        reply_markup.row(self.main_menu)
        self.jilebi.send_message(
            message.chat.id, "Select Item: ", reply_markup=reply_markup
        )

    def ask_division(self, message):
        reply_markup = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        reply_markup.row("Yes", "No")
        self.jilebi.send_message(
            message.chat.id,
            "Are you have Divisions / Department inside your faculty?",
            reply_markup=reply_markup,
        )
