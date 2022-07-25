from dataclasses import dataclass

from settings import settings


@dataclass
class Messages:
    welcome = (
        f" ::::::::       :::      :::::::::   :::::::::    :::::::: \n"
        f":+:    :+:    :+: :+:    :+:    :+:  :+:    :+:  :+:    :+:\n"
        f"+:+          +:+   +:+   +:+    +:+  +:+    +:+  +:+       \n"
        f"+#+         +#++:++#++:  +#++:++#:   +#+    +:+  +#++:++#++\n"
        f"+#+         +#+     +#+  +#+    +#+  +#+    +#+         +#+\n"
        f"#+#    #+#  #+#     #+#  #+#    #+#  #+#    #+#  #+#    #+#\n"
        f" ########   ###     ###  ###    ###  #########    ######## \n"
    )


class UserInterface:

    def get_welcome_message(self):
        ...

    def get_user_settings(self):
        ...

    def set_user_settings(self):
        ...

    def make_cards(self):
        ...

    def get_notification(self):
        ...

    def finish_work(self):
        ...


    def get_user_preferences(self):
        for setting in settings.__dict__:
            print(f"Input {setting}:")


def main():
    ui = UserInterface()
    ui.get_user_preferences()


if __name__ == "__main__":
    main()