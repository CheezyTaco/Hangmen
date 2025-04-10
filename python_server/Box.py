import socket
import threading
import time
import random


class Box:
    TIMEOUT = 5.0

    def __init__(self, contents=""):
        self.contents = contents

        self.lock = threading.Lock()
        self.owner = None
        self.owned_at_time = 0
        self.correct_guesser = None

    def update_timeout(self):
        with self.lock:
            if time.monotonic() - self.owned_at_time > self.TIMEOUT:
                self.owner = None

    def request(self, player):
        self.update_timeout()
        with self.lock:
            if self.correct_guesser is None and self.owner is None:
                self.owned_at_time = time.monotonic()
                self.owner = player
                return True
            return False

    def submit_guess(self, player, guess):
        self.update_timeout()
        with self.lock:
            if (
                self.correct_guesser is None
                and self.owner is not None
                and self.owner == player
                and self.contents == guess
            ):
                self.owner = None
                self.correct_guesser = player
                return True
            
            self.owner = None
            return False
    
    def unlock(self, player):
        self.update_timeout()
        with self.lock:
            if self.owner is not None and self.owner == player:
                self.owner = None
    
    def is_owner(self, player):
        self.update_timeout()
        with self.lock:
            return self.owner is not None and self.owner == player
