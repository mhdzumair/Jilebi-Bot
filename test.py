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
from unittest import TestCase

from PIL.Image import Image
from arrow import get
from icalevents.icalparser import Event
from telebot.types import Message, Chat, User

from jilebi import control, TeleUsers, get_module_name, get_events, create_image, jilebi
from main import server


class GeneralTest(TestCase):
    def test_db_connection(self):
        self.assertEqual(
            TeleUsers.objects.only("username").get(pk=606319743).username,
            "Mohamed_Zumair",
            "Failed to connect database",
        )

    def test_telegram_bot(self):
        self.assertEqual(
            jilebi.get_me().username, "JilebiBot", "Failed to get Telegram username"
        )

    def test_webhook_info(self):
        self.assertIn(
            "herokuapp.com", jilebi.get_webhook_info().url, "Webhook address error"
        )

    def test_get_events(self):
        self.assertTrue(
            isinstance(get_events(606319743, "weeknow", True), (list, type(None))),
            "Failed to get my Moodle events",
        )

    def test_get_module_name(self):
        self.assertEqual(
            get_module_name("In19-S04-IT2408"),
            "Software Testing & Quality Controlling",
            "failed to get module name",
        )
        self.assertEqual(get_module_name("Test"), "Test")

    def test_create_image_events(self):
        def testing(event_s):
            self.assertIsInstance(
                create_image(event_s), Image, "Create image is failed"
            )

        event = Event()
        event.start = get()
        event.end = get().shift(hours=2)
        event.categories = ["In19-S04-IT2408"]
        event.summary = "Test create image func"
        events = [event, event]
        testing(event)
        testing(events)

    def test_exception_handle(self):
        exception = control.ExceptionHandler()
        exception.args = [1, "testing"]
        self.assertTrue(exception.handle(), "Exception was not handled")


class TestJilebi(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.message = Message(
            None,
            None,
            [None],
            Chat(606319743, None, username="Mohamed_Zumair"),
            [],
            [],
            {},
        )

    def test_send_welcome(self):
        self.assertIsNone(control.send_welcome(self.message))

    def test_send_tutorial(self):
        self.assertIsNone(control.send_tutorial(self.message))

    def test_send_user_events(self):
        control.set_text_based(self.message)
        self.assertIsNone(control.send_user_today_event(self.message))
        self.assertIsNone(control.send_user_tomorrow_event(self.message))
        self.assertIsNone(control.send_user_week_event(self.message))
        self.assertIsNone(control.send_user_month_event(self.message))

    def test_calendar_link(self):
        self.assertIsNone(control.setup_link(self.message))
        self.message.text = (
            "https://lms.itum.mrt.ac.lk/calendar/export_execute.php?userid=729&authtoken"
            "=9c97a00bcfcd6cf0b5cc1144749a2dc4c43b4af1&preset_what=all&preset_time=weeknow "
        )
        self.assertIsNone(control.link_parser(self.message))
        self.assertIsNone(control.check_link(self.message))

    def test_subscribe(self):
        self.assertIsNone(control.set_unsubscribe(self.message))
        self.assertIsNone(control.set_subscribe(self.message))

    def test_others_events(self):
        control.set_text_based(self.message)
        self.assertIsNone(
            control.send_university(self.message), "Error in sending university"
        )
        self.message.text = "University of Moratuwa"
        self.assertIsNone(
            control.send_faculty(self.message), "Error in sending faculty"
        )
        self.message.text = "NDT"
        self.assertIsNone(
            control.send_division(self.message), "Error in sending division"
        )
        self.message.text = "IT"
        self.assertIsNone(
            control.send_semester(self.message), "Error in sending semester"
        )
        self.message.text = "Semester 4"
        self.assertIsNone(
            control.send_others_menu(self.message), "Error in sending others menu"
        )
        self.assertIsNone(
            control.send_today_event(self.message),
            "Error in Send Today event from  NDT IT S04",
        )
        self.assertIsNone(
            control.send_tomorrow_event(self.message),
            "Error in Send Tomorrow event from  NDT IT S04",
        )
        self.assertIsNone(
            control.send_week_event(self.message),
            "Error in Send week event from  NDT IT S04",
        )
        self.assertIsNone(
            control.send_month_event(self.message),
            "Error in Send month event from  NDT IT S04",
        )
        self.assertIsNone(
            control.send_module_list(self.message),
            "Error in Send module list  from  NDT IT S04",
        )
        self.assertIsNone(
            control.send_back(self.message), "Error in Send back from  NDT IT S04"
        )
        self.assertIsNone(
            control.send_back(self.message), "Error in Send back from  NDT IT"
        )
        self.assertIsNone(
            control.send_back(self.message), "Error in Send back from  NDT"
        )
        self.message.text = "IT"
        self.assertIsNone(
            control.send_division(self.message), "Error in sending division"
        )
        self.message.text = "Semester 2"
        self.assertIsNone(
            control.send_others_menu(self.message), "Error in sending others menu"
        )
        self.assertIsNone(
            control.send_today_event(self.message),
            "Error in Send Today event from IT S02",
        )
        self.assertIsNone(control.send_to_main(self.message), "Error in Send main menu")

    def test_text_based_result(self):
        self.assertIsNone(
            control.set_text_based(self.message), "cannot set to text based result"
        )
        self.assertIsNone(
            control.send_user_today_event(self.message),
            "cannot send today event as text based",
        )

    def test_image_based_result(self):
        self.assertIsNone(
            control.set_image_based(self.message), "cannot set to image based result"
        )
        self.assertIsNone(
            control.send_user_today_event(self.message),
            "cannot send today event as image based",
        )
        print(control.send_image(None, self.message.chat.id))

    def test_submit_module_detail(self):
        self.assertIsNone(control.submit_module_details(self.message))
        self.message.text = "University of Moratuwa"
        self.assertIsNone(control.handle_all(self.message))
        self.message.text = "NDT"
        self.assertIsNone(control.handle_all(self.message))
        self.message.text = "Yes"
        self.assertIsNone(control.get_answer(self.message))
        self.message.text = "IT"
        self.assertIsNone(control.handle_all(self.message))
        self.message.text = "Semester 4"
        self.assertIsNone(control.handle_all(self.message))
        self.message.text = """
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
"""
        message = jilebi.send_message(self.message.chat.id, self.message.text)
        self.assertIsInstance(message, Message, "couldn't get message instance")
        self.assertIsNone(control.handle_all(message))

    def test_feedback(self):
        self.assertIsNone(control.get_feedback(self.message))
        self.message.text = "Hi Mhd"
        message = jilebi.send_message(self.message.chat.id, self.message.text)
        self.assertIsInstance(message, Message, "couldn't get message instance")
        self.assertIsNone(control.handle_all(message))

    def test_extras(self):
        self.assertIsNone(control.share_jilebi(self.message))
        self.assertIsNone(control.send_source_code(self.message))

    def test_send_notification(self):
        self.assertIsNone(control.send_notification(), "Error in send notification")

    def test_send_admin_message(self):
        self.message.text = """/send 606319743
Hello, this is test message.
"""
        self.assertIsNone(control.send_admin_message(self.message), "Error in send admin without reply_to_message")
        self.message.reply_to_message = self.message
        self.message.reply_to_message.forward_from = User(606319743, False, "mohamed")
        self.assertIsNone(control.send_admin_message(self.message), "Error in send admin with reply_to_message")


class TestServer(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = server.test_client()

    def test_user_count(self):
        self.assertIsInstance(self.client.get("/get_user_count").json["count"], int)

    def test_get_message(self):
        self.assertEqual(
            self.client.get("/" + environ.get("JILEBI_TOKEN")).status_code, 405
        )

    def test_root(self):
        self.assertEqual(self.client.get("/").status_code, 200)
