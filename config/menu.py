WAGTAIL_MENU_APPS_ORDER = [
    "django_celery_beat",
]


def get_menu_order(app_name):
    try:
        return WAGTAIL_MENU_APPS_ORDER.index(app_name) + 1
    except:
        return 9000
