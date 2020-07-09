import vlc
from time import sleep
import threading as th
import enum
from pynput import keyboard


class Change(enum.Enum):
    NEXT = enum.auto()
    PREVIOUS = enum.auto()


class Player:

    def __init__(self):
        self.idx_playing = 0
        self._th_listener = keyboard.Listener(on_release=self.thread_key)
        self._active = False
        self._change_key = False
        self._change_mode = Change.NEXT
        self._lock_change = th.Lock()

        self.instance = vlc.Instance('--fullscreen')
        self.player = self.instance.media_list_player_new()

    def add_playlist(self, playlist):
        media_list = self.instance.media_list_new()
        media_list.add_media(self.instance.media_new(playlist['list']))
        self.media_len = 1
        for (image, track) in zip(playlist['images'], playlist['playlist']):
            media_list.add_media(self.instance.media_new(image))
            media_list.add_media(self.instance.media_new(track))
            self.media_len += 2
        self.player.set_media_list(media_list)

    def thread_key(self, key):
        if key == keyboard.Key.space:
            self.player.pause()
        if key == keyboard.Key.esc:
            self._active = False
        if key == keyboard.Key.left:
            with self._lock_change:
                self._change_mode = Change.PREVIOUS
                self._change_key = True
        if key == keyboard.Key.right:
            with self._lock_change:
                self._change_mode = Change.NEXT
                self._change_key = True
        self._await_key = False

    def wait(self, time):
        sleep(2)
        self.player.pause()
        if time is None:
            self._await_key = True
            while self._await_key:
                pass
        else:
            sleep(time)
            self.player.pause()

    def play(self, delay):
        self._active = True
        self._th_listener.start()
        # self.player.set_fullscreen(True)
        self.player.play()
        self.wait(None)
        while self._active:
            self.change_track()
            if self.idx_playing % 2 == 0:
                while not self.player.get_state() == 6:
                    if not self._active or self._change_key:
                        self.player.stop()
                        break
            else:
                self.wait(delay)
        self.player.stop()

    def change_track(self):
        if self._change_mode == Change.NEXT:
            if self._change_key:
                with self._lock_change:
                    self._change_key = False
                    if self.idx_playing % 2 == 0:
                        self.idx_playing += 1
                    else:
                        self.idx_playing += 2
                    if self.idx_playing > self.media_len:
                        self.idx_playing = self.media_len - 1
            else:
                self.idx_playing += 1
        if self._change_mode == Change.PREVIOUS:
            with self._lock_change:
                self._change_mode = Change.NEXT
                self._change_key = False
                if self.idx_playing % 2 == 0:
                    self.idx_playing -= 1
                else:
                    self.idx_playing -= 2
        if self.idx_playing < 0:
            self.idx_playing = 0
        if self.idx_playing == self.media_len:
            self._active = False
        else:
            self.player.play_item_at_index(self.idx_playing)
            print(self.idx_playing)
