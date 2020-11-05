# This file is used for declaring some of the classes for standardizing messagesi

class Chat():
    def __init__(self):
        self.messages = []

    def get_messages(self, start=0, end=20):
        pass

class Message():
    def __init__(self):
        self.text = ""
        self.author = None
        self.id = "0"
        self.thread_id = "0"

class User():
    pass
