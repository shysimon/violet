import datetime


def my_time_to_string(t):
    return datetime.datetime.strftime(t, "%Y-%m-%d %H:%M:%S")
