import vlc
from time import sleep
import enum
from pynput import keyboard, mouse
import threading as th
import screeninfo


class Modes:
    NEXT = keyboard.Key.right
    PREVIOUS = keyboard.Key.left
    PAUSEPLAY = keyboard.Key.space
    END = keyboard.Key.esc


class Player:

    def press(self, modekey):
        if modekey in Modes.__dict__.values():
            self.control(modekey)

    def __init__(self, duration):
        self.idx_playing = -1
        self._autoplay = duration > 0
        self._active = False
        self._ended = th.Event()

        self.instance = vlc.Instance(
            '--no-xlib --fullscreen --image-duration=' + str(duration))
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

    def play(self):
        self._active = True
        self.listener = keyboard.Listener(on_release=self.press)
        self.keyboard = keyboard.Controller()
        self.mouse = mouse.Controller()
        self.player.play()
        sleep(0.5)
        self.player.pause()
        self.change_screen()
        self.listener.start()
        while self._active:
            if self.player.get_state() == vlc.State.Ended and self.idx_playing == self.media_len - 1:
                self.control(Modes.END)

    def change_screen(self):
        screens = screeninfo.get_monitors()
        if len(screens) > 1:
            if any(['HDMI' in x.name for x in screens]):
                idx = ['HDMI' in x.name for x in screens].index(True)
                monitor = screens[idx]
                self.keyboard.press(keyboard.Key.cmd)
                self.keyboard.press(keyboard.Key.shift_l)
                if monitor.x > 0:
                    self.keyboard.press(keyboard.Key.right)
                    self.keyboard.release(keyboard.Key.right)
                else:
                    self.keyboard.press(keyboard.Key.left)
                    self.keyboard.release(keyboard.Key.left)
                self.keyboard.release(keyboard.Key.cmd)
                self.keyboard.release(keyboard.Key.shift_l)
                sleep(0.5)
        else:
            monitor = screens[0]
        cur_pos = self.mouse.position
        self.mouse.position = (
            (monitor.x + monitor.width)/2, (monitor.y + monitor.height) / 2)
        self.mouse.click(mouse.Button.left, 2)
        self.mouse.position = cur_pos

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
            if (not self._autoplay and not self.idx_playing % 2 == 0) or self.idx_playing == 0:
                self.player.next()

        if mode == Modes.END:
            self.player.stop()
            self.listener.stop()
            self._active = False
            self._ended.set()

    def event_itemchange(self, event):
        self.idx_playing += 1

    def wait_end(self):
        self._ended.wait()

    def has_ended(self):
        return self._ended.is_set()
