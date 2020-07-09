import vlc
from time import sleep
import enum

class Modes(enum.Enum):
    NEXT = enum.auto()
    PREVIOUS = enum.auto()
    PAUSEPLAY = enum.auto()

class Player:

    def __init__(self):
        self.idx_playing = 0
        self._active = False

        self.instance = vlc.Instance()
        self.player = self.instance.media_list_player_new()
        self.manager = self.player.event_manager()
        self.manager.event_attach(vlc.EventType.MediaListPlayerNextItemSet, self.event_itemchange)


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
        self.player.play()
        self.wait(None)
        while self._active:
            pass

    def control(self, mode):
        if mode == Modes.NEXT:
            self.player.next()
        if mode == Modes.PREVIOUS:
            self.idx_playing -= 2
            self.player.play_item_at_idx(self.idx_playing)
        if mode == Modes.PAUSEPLAY:
            self.player.pause()

    def wait(self, time):
        sleep(1)
        self.player.pause()
        if time is None:
            pass
        else:
            sleep(time)
            self.player.pause()
      
    def event_itemchange(self, event):
        self.idx_playing += 1
        print(self.idx_playing)

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