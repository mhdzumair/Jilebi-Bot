from unittest import TestCase, main

from arrow import get
from icalevents.icalparser import Event
from PIL.Image import Image
from telebot.types import Message, Chat

from jilebi import TeleUsers, jilebi, get_events, get_module_name, create_image, Keyboard


class GeneralTest(TestCase):
    def test_db_connection(self):
        self.assertEqual(TeleUsers.objects.only("username").first().username, "Mohamed_Zumair",
                         "Failed to connect database")

    def test_telegram_bot(self):
        self.assertEqual(jilebi.get_me().username, "JilebiBot",
                         "Failed to get Telegram username")

    def test_webhook_info(self):
        self.assertIn("herokuapp.com", jilebi.get_webhook_info().url,
                      "Webhook address error")

    def test_get_events(self):
        self.assertIsInstance(get_events(606319743, "weeknow", True), list,
                              "Failed to get my Moodle events")

    def test_get_module_name(self):
        self.assertEqual(get_module_name("In19-S04-IT2408"), "Software Testing & Quality Controlling",
                         "failed to get module name")

    def test_create_image_events(self):

        def testing(event_s):
            self.assertIsInstance(create_image(event_s), Image, "Create image is failed")

        event = Event()
        event.start = get()
        event.end = get().shift(hours=2)
        event.categories = ["In19-S04-IT2408"]
        event.summary = "Test create image func"
        events = [event, event]
        testing(event)
        testing(events)


class TestKeyboards(TestCase):
    message = Message(None, None, [None], Chat(606319743, None), [], [], {})
    keyboard = Keyboard(jilebi)

    def test_send_home(self):
        self.assertIsNone(self.keyboard.send_home(self.message), "Error in sending home button")

    def test_send_university(self):
        self.assertIsNone(self.keyboard.send_university(self.message), "Error in sending university")

    def test_send_faculty(self):
        TeleUsers.objects(pk=self.message.chat.id).update(selection__university="University of Moratuwa")
        self.assertIsNone(self.keyboard.send_faculty(self.message), "Error in sending faculty")

    def test_send_division(self):
        TeleUsers.objects(pk=self.message.chat.id).update(selection__university="University of Moratuwa",
                                                          selection__faculty="NDT")
        self.assertIsNone(self.keyboard.send_division(self.message), "Error in sending division")

    def test_send_semester(self):
        TeleUsers.objects(pk=self.message.chat.id).update(selection__university="University of Moratuwa",
                                                          selection__faculty="NDT",
                                                          selection__division="IT")
        self.assertIsNone(self.keyboard.send_semester(self.message), "Error in sending semester")

    def test_send_others_menu(self):
        TeleUsers.objects(pk=self.message.chat.id).update(selection__university="University of Moratuwa",
                                                          selection__faculty="NDT",
                                                          selection__division="IT",
                                                          selection__semester="Semester 4")
        self.assertIsNone(self.keyboard.send_others_menu(self.message), "Error in sending others menu")


if __name__ == '__main__':
    main()
