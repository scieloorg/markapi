from django.utils.translation import gettext_lazy as _

DAYS = "days"
HOURS = "hours"
MINUTES = "minutes"
SECONDS = "seconds"
MICROSECONDS = "microseconds"

PERIOD_CHOICES = (
    (DAYS, _("Days")),
    (HOURS, _("Hours")),
    (MINUTES, _("Minutes")),
    (SECONDS, _("Seconds")),
    (MICROSECONDS, _("Microseconds")),
)

SINGULAR_PERIODS = (
    (DAYS, _("Day")),
    (HOURS, _("Hour")),
    (MINUTES, _("Minute")),
    (SECONDS, _("Second")),
    (MICROSECONDS, _("Microsecond")),
)

SOLAR_SCHEDULES = [
    ("dawn_astronomical", _("Astronomical dawn")),
    ("dawn_civil", _("Civil dawn")),
    ("dawn_nautical", _("Nautical dawn")),
    ("dusk_astronomical", _("Astronomical dusk")),
    ("dusk_civil", _("Civil dusk")),
    ("dusk_nautical", _("Nautical dusk")),
    ("solar_noon", _("Solar noon")),
    ("sunrise", _("Sunrise")),
    ("sunset", _("Sunset")),
]