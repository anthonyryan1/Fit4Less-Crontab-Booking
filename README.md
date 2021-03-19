Adapted from [Gym-Booking-Discord-Bot](https://github.com/davepetrov/Gym-Booking-Discord-Bot) by [David Petrov](https://github.com/davepetrov).

Reworked for crontab usage, so I don't need to stay up late on work nights.

# Gentoo dependencies
* www-apps/chromedriver-bin
* dev-python/selenium

# Cron notes
* You'll need to specify `DISPLAY=:0` before the /path/to/fit4less/workout-booker.py on a machine with a desktop
* Check your system timezone, be aware that Fit4Less slots drop at 72 hours before the slot begins
    * To book for 10:30 on Monday, you should run the script at 10:31 on Friday 72 hours before
