from common.constants import DEV_MODE


def dev_print(message):
    if DEV_MODE:
        print(message)