Adapted from [Gym-Booking-Discord-Bot](https://github.com/davepetrov/Gym-Booking-Discord-Bot) by [David Petrov](https://github.com/davepetrov).

Reworked for crontab usage, so I don't need to stay up late on work nights.

# Gentoo dependencies
* www-apps/chromedriver-bin
* dev-python/selenium

# Cron notes
* You'll need to specify `DISPLAY=:0` before the /path/to/fit4less/workout-booker.py on a machine with a desktop
* Check your system timezone, be aware that Fit4Less slots drop at 00:00 Eastern time and design your cron as needed
* It seems best to schedule a couple of retries, since fit4less is often throwing 500s in the mad dash for a time slot
