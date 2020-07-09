import vlc
from time import sleep
import enum
from pynput import keyboard


class Modes:
    NEXT = keyboard.Key.right
    PREVIOUS = keyboard.Key.left
    PAUSEPLAY = keyboard.Key.space
    END = keyboard.Key.esc


class Player:

    def press(self, modekey):
        if modekey in Modes.__dict__.values():
            self.control(modekey)

    def __init__(self):
        self.idx_playing = -1
        self._active = False

        self.instance = vlc.Instance('--no-xlib --fullscreen')
        self.player = self.instance.media_list_player_new()
        self.manager = self.player.event_manager()
        self.manager.event_attach(
            vlc.EventType.MediaListPlayerNextItemSet, self.event_itemchange)

    def add_playlist(self, playlist):
        media_list = self.instance.media_list_new()
        media_list.add_media(self.instance.media_new(playlist['list']))
        self.media_len = 1
        for (image, track) in zip(playlist['images'], playlist['playlist']):
            media_list.add_media(self.instance.media_new(image))
            media_list.add_media(self.instance.media_new(track))
            self.media_len += 2
        self.player.set_media_list(media_list)

    def play(self, wait=False):
        self._active = True
        self.listener = keyboard.Listener(on_release=self.press)
        self.player.play()
        self.listener.start()
        while self._active:
            if self.player.get_state() == vlc.State.Ended and self.idx_playing == self.media_len - 1:
                self.control(Modes.END)

    def control(self, mode):
        if mode == Modes.NEXT:
            if self.idx_playing < self.media_len - 2:
                if self.idx_playing % 2 == 0:
                    self.player.next()
                else:
                    self.idx_playing += 1
                    self.player.play_item_at_index(self.idx_playing + 1)

        if mode == Modes.PREVIOUS:
            if self.idx_playing > 1:
                if self.idx_playing % 2 == 0:
                    self.idx_playing -= 2
                    self.player.previous()
                else:
                    self.idx_playing -= 3
                    self.player.play_item_at_index(self.idx_playing + 1)

        if mode == Modes.PAUSEPLAY:
            self.player.pause()

        if mode == Modes.END:
            self.player.stop()
            self.listener.stop()
            self._active = False

    def event_itemchange(self, event):
        self.idx_playing += 1
