<p align="center">
    <img src="images/photo_2020-12-08_13-26-48.jpg" width=450 height=450 align=center>
</p>
<h1 align="center">Jilebi Bot</h1>

![Travis (.com)](https://img.shields.io/travis/com/mhdzumair/Jilebi-Bot)
[![codecov](https://codecov.io/gh/mhdzumair/Jilebi-Bot/branch/main/graph/badge.svg?token=P8BDN38VQ6)](https://codecov.io/gh/mhdzumair/Jilebi-Bot)

<h4 align="center">An Interactive Telegram bot for managing the Events of Moodle (LMS) Students.</h4>

### Features
* View the schedule as a beautiful Image based or text-based results
* View other university students modules, events (if they volunteer to give details)
* Get Reminder for events within 30 minutes of time period.<p color="red"> Note: The event should be created at least before half an hour by your module lecturer, in order to get Reminder</p>
* Send Queries / Feedbacks to Me

### Requirement for Jilebi bot
In order to get your own events, You need to setup the calendar link first.
You can watch the tutorial by sending `/tutorial`
However, you can still view other's events.

### Requirements for Development
    pyTelegramBotAPI
    mongoengine
    pymongo[srv]
    arrow
    APScheduler
    httplib2
    Flask
    Pillow
    icalevents
NOTE: for getting Moodle module code you need to get categories type from icalendar.
      Original version of [icalevents](https://github.com/irgangla/icalevents) is not support `event.categories` so I created patch for it.
      download it from [mhdzumair/icalevents](https://github.com/mhdzumair/icalevents.git)

### Useful Link
* [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
* [mongoengine](http://docs.mongoengine.org/tutorial.html)
* [DuttyBot](https://github.com/dmytrostriletskyi/DuttyBot.git)
* [Rutetider](https://github.com/dmytrostriletskyi/Rutetider)
* [python-telegram-bot-heroku](https://github.com/liuhh02/python-telegram-bot-heroku)
* Fonts are got from [Google Fonts](https://fonts.google.com/)
* images from [unsplash](https://unsplash.com/s/photos/paper-and-laptop) & [pexels](https://www.pexels.com/search/paper%20and%20pen/) 
