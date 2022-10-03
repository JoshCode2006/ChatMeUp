from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.tab import MDTabsBase
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.uix.screenmanager import *
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast
from kivy.clock import Clock
import kivy

from kivy.graphics.texture import Texture
from kivymd.uix.list import TwoLineIconListItem

kivy.require("1.9.0")

import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send(message, nickname):
    client.send(f"{nickname}&*{message}".encode('utf-8'))


def unpackage_list(entry):
    if "&*" in entry:
        unpackaged = entry.split("&*")
        unpackaged.pop(-1)
        return unpackaged
    else:
        return None


class Tab(MDTabsBase, FloatLayout):
    pass


class MyChat(MDLabel):
    pass


class OtherChat(MDLabel):
    pass


class ChatScreen(Screen):
    lists = ObjectProperty()


class PostScreen(Screen):
    pass


class CameraScreen(Screen):
    pass


class ChatPage(Screen):
    pass


class SignUpScreen(Screen):
    pass


class Profile(TwoLineIconListItem):
    pass


class SplashScreen(Screen):
    def anim(self, widget):
        animate = Animation(
            opacity=1,
            duration=1
        )
        animate += Animation(
            opacity=0,
            duration=1
        )
        animate.start(widget)


class ChatMeUpApp(MDApp):
    text = ["camera", "chat", "post"]
    current = 0
    screen = "chat"
    message = ''
    len_names = 0
    messages = []
    name_list = ["emma"]
    connected = False

    def build(self):
        self.theme_cls.primary_palette = "Cyan"
        self.word = "Work still in  progress so this doesn't do anything"
        m_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Nothing",
                "on_release": lambda x="word": self.call(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Nothing",
                "on_press": lambda x="word": self.call(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Nothing",
                "on_press": lambda x="word": self.call(x)
            }
        ]
        self.drop = MDDropdownMenu(
            items=m_items,
            width_mult=4,
        )

        return Builder.load_file("main.kv")

    def on_start(self):
        try:
            client.connect(("localhost", 5555))
            self.connected = True
        except:
            self.connected = False
        self.sm = self.root.ids.sm
        for tab_name in self.text:
            if tab_name != "camera":
                self.root.ids.tabs.add_widget(Tab(text=tab_name))
            else:
                self.root.ids.tabs.add_widget(Tab(icon=tab_name, text=tab_name, title_is_capital=True))
        self.sm.current = "splash"
        self.sm.screens[0].anim(self.sm.screens[0])
        Clock.schedule_once(self.end_splash, 4)
        Clock.schedule_interval(self.post_recv, 1.0 / 180)

        self.root.children[0].pos_hint = {"x": 1}
        self.root.children[2].size_hint_y = 0

    def receive(self):
        stop = False
        while not stop:
            try:
                self.recv = client.recv(1024).decode('utf-8')
                unpackaged = unpackage_list(self.recv)
                if unpackaged != None:
                    self.name_list = unpackaged
                else:
                    self.message = self.recv

            except:
                print("ERROR")
                stop = True

    def send(self):
        self.entry = self.root.ids.sm.children[0].children[0].children[0].children[3].children[1].text
        empty = self.no_space(self.entry)
        if self.entry != "" and not empty:
            sent = MyChat(text=self.entry)
            animation = Animation(
                opacity=0,
                duration=.2
            )
            animation += Animation(
                opacity=1,
                duration=.1
            )
            animation.start(sent)
            recv = OtherChat(text=self.entry)
            animation1 = Animation(
                opacity=0,
                duration=.2
            )
            animation1 += Animation(
                opacity=1,
                duration=.1
            )

            animation1.start(recv)
            self.root.ids.sm.children[0].children[0].children[-1].children[0].add_widget(sent)

            self.root.ids.sm.children[0].children[0].children[0].children[3].children[1].text = ""
            self.root.ids.sm.children[0].children[0].children[-1].scroll_y = 0
            send(self.entry, self.nickname)

    def update_names(self, dt):
        old_names = []
        for item in self.sm.screens[3].lists.children:
            old_names.append(item.text)
        for name in self.name_list:
            if name not in old_names and name != self.nickname:
                self.sm.screens[3].lists.add_widget(Profile(text=name))

    def post_recv(self, dt):
        if self.message != "":
            self.messages.append(self.message)
            self.message = ""
        if self.sm.current == "chat_page" and len(self.messages) > 0:
            for message in self.messages:
                recv = OtherChat(text=message)
                animation1 = Animation(
                    opacity=0,
                    duration=.2
                )
                animation1 += Animation(
                    opacity=1,
                    duration=.1
                )

                animation1.start(recv)
                self.root.ids.sm.children[0].children[0].children[-1].children[0].add_widget(recv)
                self.messages.remove(message)

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        if tab_text != "":
            if tab_text == "chat" or tab_text == "post":
                self.sm.current = tab_text
            else:
                tab_text = "camera"
                self.sm.current = tab_text
            if self.text.index(tab_text) > self.current:
                self.current = self.text.index(tab_text)
                self.sm.transition.direction = "left"
            if self.text.index(tab_text) < self.current:
                self.current = self.text.index(tab_text)
                self.sm.transition.direction = "right"

    def end_splash(self, something):
        if self.connected:
            self.sm.current = "signup"
        else:
            self.switch_tab_by_name("chat")
            self.root.children[0].pos_hint = {"x": 0}
            self.root.children[2].size_hint_y = 0.17

    def switch_tab_by_name(self, screen):
        if screen == "chat" or screen == "post":
            search = "text"
        else:
            search = "icon"
        self.root.ids.tabs.switch_tab(screen, search_by=search)

    def no_space(self, statement):
        splits = []
        empty = False
        for letter in statement:
            if letter != "\n" and letter != " ":
                splits.append(letter)
        if len(splits) == 0:
            empty = True
        else:
            empty = False
        return empty

    def back(self):
        self.root.ids.top_bar.left_action_items = []
        self.root.ids.top_bar.right_actsion_items = [["magnify", lambda x: app.icon_toast()],
                                                     ["dots-vertical", lambda x: app.call_it(x)]]
        self.sm.current = "chat"
        self.sm.transition = SlideTransition()
        self.root.ids.top_bar.title = "ChatMeUp"
        self.root.ids.tabs.pos_hint = {"x": 0}
        self.root.ids.tabs.size_hint_y = 0.1

    def call(self, some):
        self.drop.dismiss()
        toast(text=self.word)

    def icon_toast(self):
        toast(text=self.word)

    def call_it(self, button):
        self.drop.caller = button
        self.drop.open()

    def signup(self, username, password):
        self.nickname = username.text
        if self.connected:
            message = client.recv(1024).decode('utf-8')
            if message == "NICK":

                client.send(self.nickname.encode('utf-8'))
                self.switch_tab_by_name("chat")
                self.root.children[0].pos_hint = {"x": 0}
                self.root.children[2].size_hint_y = 0.17
                self.thread = threading.Thread(target=self.receive)
                self.thread.daemon = True
                self.thread.start()

                Clock.schedule_interval(self.update_names, 1.0 / 180)

    def start_chat(self, text):
        self.sm.transition = NoTransition()
        self.sm.current = "chat_page"
        self.root.ids.tabs.pos_hint = {"x": 1}
        self.root.ids.tabs.size_hint_y = 0.0000000000000000000000000000000000001
        self.root.ids.top_bar.title = text
        self.root.ids.top_bar.left_action_items = [["arrow-left", lambda x: app.back()]]
        self.root.ids.top_bar.right_action_items = [["dots-vertical", lambda x: app.call_it(x)]]


app = ChatMeUpApp()

if __name__ == "__main__":
    app.run()
