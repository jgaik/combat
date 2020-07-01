import vlc
from time import sleep
from threading import Thread
from pynput import keyboard


class Player:

    def __init__(self, playlist):
        self.playlist = playlist
        self.player = vlc.MediaPlayer()
        self.idx_playing = 0
        self._listener = keyboard.Listener(on_release=self.thread_key)
        self._active = False
        self._playing = False

    def play(self, mode):
        self._active = True
        self._listener.start()
        self.player.set_fullscreen(True)
        self.player.set_mrl(self.playlist['list'])
        self.player.play()
        sleep(1)
        self.player.pause()
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

    def thread_key(self, key):
        if key == keyboard.Key.space:
            self.player.pause()
            self._playing = not self._playing
        if key == keyboard.Key.esc:
            self._active = False

    def wait(self):
        while not self._playing:
            if not self._active:
                return
