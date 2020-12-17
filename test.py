from unittest import TestCase, main

from PIL.Image import Image
from arrow import get
from icalevents.icalparser import Event
from telebot.types import Message, Chat

from jilebi import control, TeleUsers, get_module_name, get_events, create_image, jilebi


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


class TestJilebi(TestCase):
    message = Message(
        None, None, [None], Chat(606319743, None, username="Mohamed_Zumair"), [], [], {}
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


if __name__ == "__main__":
    main()
