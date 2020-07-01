import vlc
from time import sleep
from threading import Thread
from pynput import keyboard


class Player:

    def __init__(self):
        self.idx_playing = 0
        self._th_listener = keyboard.Listener(on_release=self.thread_key)
        self._active = False

        self.instance = vlc.Instance()
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

    def play(self, delay=None):
        self._active = True
        self._th_listener.start()
        self.player.set_fullscreen(True)
        self.player.play()
        self.wait(None)
        while self._active:
            self.player.play_item(self.idx_playing)
            if self.idx_playing % 2 == 0:
                while not self.player.get_state() == 6:
                    pass
            else:
                self.wait(delay)
            self.idx_playing += 1
        self.player.stop()

    def thread_key(self, key):
        if key == keyboard.Key.space:
            self.player.pause()
            self._await_key = False
        if key == keyboard.Key.esc:
            self._active = False
        if key == keyboard.Key.left:
            self.player.previous()
            self.idx_playing -= 1  # add checking idx
        if key == keyboard.Key.right:
            self.player.next()
            self.idx_playing += 1  # add checking idx

    def wait(self, time):
        sleep(1)
        self.player.pause()
        if time is None:
            self._await_key = True
            while self._await_key:
                pass
        else:
            sleep(time)
            self.player.pause()

    def play2(self, delay):
        self._active = True
        self._th_listener.start()
        self.player.set_fullscreen(True)
        self.player.play()
        self.wait(None)
        while self._active:
            self.player.next()
            self.idx_playing += 1
            if self.idx_playing % 2 == 0:
                while not self.player.get_state() == 6:
                    if not self._active:
                        break
            else:
                self.wait(delay)
        self.player.stop()


'''
        while self._active:
            self.wait()
            self.player.set_mrl(self.playlist['images'][self.idx_playing])
            self.player.play()
            self._playing = False
            sleep(1)
            self.player.pause()
            self.wait()
            self.player.set_mrl(self.playlist['playlist'][self.idx_playing])
            self.player.play()
            while not self.player.get_state() == 6:
                if not self._active:
                    break
            if self.idx_playing < len(self.playlist):
                self.idx_playing = self.idx_playing + 1
            else:
                self._active = False
        self.player.stop()
        self.player.release()
'''
