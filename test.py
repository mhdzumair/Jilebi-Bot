from unittest import TestCase, main

from jilebi import TeleUsers, jilebi, get_events, get_module_name


class Test(TestCase):
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


if __name__ == '__main__':
    main()
