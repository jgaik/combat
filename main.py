#import vlc
import os
import shutil
import random
from time import sleep
from threading import Thread
#from pynput import keyboard
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import ttk
import ttkwidgets

TRACKS = 10

def getNumbers(path):
    return sorted([int(x) for x in os.listdir(path) if os.path.isdir(path + os.sep + x) and x.isdigit()])


def randomChoreo(numbers):
    return random.choices(numbers, k=TRACKS)


def prepareList(path, choreoNumbers):
    playlist = []
    images = []
    imageList = Image.new('1', (1920, 1080))
    listDraw = ImageDraw.Draw(imageList)
    listFont = ImageFont.truetype(path + os.sep + 'font.ttf', 50)
    listText = "Randomized Body Combat choreography playlist:" + os.linesep
    for x in range(TRACKS):
        imgTemp = Image.new('1', (1920, 1080))
        tempDraw = ImageDraw.Draw(imgTemp)
        trackText = f" -> Track {x} - BodyCombat {choreoNumbers[x]}"
        tempFont = ImageFont.truetype(path + os.sep + 'font.ttf', 100)
        tempDraw.text((20, 20), "Next:" + os.linesep +
                      trackText, fill='white', font=tempFont, spacing=30)
        listText = listText + trackText + os.linesep
        file = next(y for y in
                    os.listdir(path + os.sep + str(choreoNumbers[x])) if y[0] == str(x))
        playlist.append(os.path.abspath(path) + os.sep +
                        str(choreoNumbers[x]) + os.sep + file)
        imgTemp.save(path + os.sep + "temp" + os.sep + f"{x}.png")
        images.append(path + os.sep + "temp" + os.sep + f"{x}.png")
    listDraw.text((20, 20), listText, fill='white', font=listFont, spacing=30)
    imageList.save(path + os.sep + "temp" + os.sep + "list.png")
    return {'playlist': playlist,
            'list': path + os.sep + "temp" + os.sep + "list.png",
            'images': images}

'''
class Player:

    def __init__(self, playlist):
        self.playlist = playlist
        self.player = vlc.MediaPlayer()
        self.idx_playing = 0
        self._listener = keyboard.Listener(on_release=self.thread_key)
        self._active = False
        self._playing = False

    def play(self):
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

'''
class App:

    def __init__(self, master, path):
        self.master = master
        self.path = path
        self.master.protocol("WM_DELETE_WINDOW", self.end)
        os.mkdir(path + os.sep + "temp")
        icon = Image.open(path + os.sep + "icon.png")
        icon = icon.resize((20, 20))
        self.image_icon = ImageTk.PhotoImage(icon)

        self.frame_choreo = tk.Frame(self.master)
        self.frame_track = tk.Frame(self.master)
        self.frame_random = tk.Frame(self.master)
        self.frame_player = tk.Frame(self.master)
        self.frame_choreo.grid(row=0,column=0)
        self.frame_track.grid(row=0,column=1)
        self.frame_random.grid(row=0,column=2)
        self.frame_player.grid(row=1,column=0,columnspan=3)


        #choreo list
        ttk.Label(self.frame_choreo, text="Choreographies:").grid(sticky="W")
        self.var_all_choreo = tk.BooleanVar()
        self.var_all_choreo.set(True)
        self.check_all_choreo = ttk.Checkbutton(self.frame_choreo, text="Include all", variable=self.var_all_choreo, command=self.event_choreo_all)
        self.list_choreo = {}
        self.tree_include_choreo = ttkwidgets.CheckboxTreeview(self.frame_choreo, show="tree")
        self.tree_include_choreo.bind("<<TreeviewSelect>>", self.event_choreo_check)
        for item in getNumbers(self.path):
            self.list_choreo[item] = self.tree_include_choreo.insert(
                "", "end", text=item)
            self.tree_include_choreo.change_state(
                self.list_choreo[item], "checked")
        self.tree_include_choreo.grid(sticky="WE")
        self.check_all_choreo.grid(sticky="W")

        #track list
        ttk.Label(self.frame_track, text="Tracks:").grid(sticky="W")
        self.var_all_track = tk.BooleanVar()
        self.var_all_track.set(True)
        self.check_all_track = ttk.Checkbutton(self.frame_track, text="Include all", variable=self.var_all_track)
        self.list_track = {}
        self.tree_include_track = ttkwidgets.CheckboxTreeview(self.frame_track, show="tree")
        self.tree_include_track.bind("<<TreeviewSelect>>", self.event_track_check)
        for item in range(TRACKS):
            self.list_track[item] = self.tree_include_track.insert(
                "", "end", text=f"Track {item}")
            self.tree_include_track.change_state(
                self.list_track[item], "checked")
        self.tree_include_track.grid(sticky="WE")
        self.check_all_track.grid(sticky="W")
        
        #random list
        self.button_random = ttk.Button(self.frame_random, text="Randomize", command=self.event_random)
        self.button_random.grid()
        self.tree_random = ttkwidgets.CheckboxTreeview(self.frame_random, show="tree")
        self.tree_random.grid()
        self.button_reroll = ttk.Button(
            self.frame_random, text="Reroll selected", image=self.image_icon, compound=tk.LEFT, command=self.event_reroll)
        self.button_reroll.grid()

        #player
        self.button_end = ttk.Button(self.frame_player, text="End", command=self.end)
        self.button_end.grid(sticky="W")

    def event_choreo_check(self, event):
      self.var_all_choreo.set(len(self.tree_include_choreo.get_checked()) == len(self.list_choreo))

    def event_choreo_all(self):
      if self.var_all_choreo.get():
        for item in self.list_choreo.values():
          self.tree_include_choreo.change_state(item, "checked")
      else:
        for item in self.list_choreo.values():
          self.tree_include_choreo.change_state(item, "unchecked")

    def event_track_check(self, event):
      self.var_all_track.set(len(self.tree_include_track.get_checked()) == len(self.list_track))

    def event_track_all(self):
      if self.var_all_track.get():
        for item in self.list_track.values():
          self.tree_include_track.change_state(item, "checked")
      else:
        for item in self.list_track.values():
          self.tree_include_track.change_state(item, "unchecked")

    def event_random(self):
      self.tree_random.delete(*self.tree_random.get_children())
      list_include_choreo = self.tree_include_choreo.get_checked()
      list_random = randomChoreo([x for x in self.list_choreo.keys() if self.list_choreo[x] in list_include_choreo])
      list_include_track = self.tree_include_track.get_checked()
      self.list_randow_choreo = {}
      for item in self.list_track.keys():
        if self.list_track[item] in list_include_track:
          self.list_randow_choreo[item] = [
            self.tree_random.insert("", "end", text=f"Track {item} - BodyCombat {list_random[item]}"),
            item,
            list_random[item]]

    def event_reroll(self):
      list_include_random = self.tree_random.get_checked()
      list_include_track = self.tree_include_track.get_checked()

      list_track = [x for x in self.list_track.keys() if self.list_track[x] in list_include_track]
      for item in self.list_random_choreo.keys():
        pass
        

    def end(self):
        shutil.rmtree(self.path + os.sep + "temp")
        self.master.destroy()


if __name__ == "__main__":
    path = os.getcwd() + os.sep + "random"
    """
    try:
        choreo = randomChoreo(getNumbers(path))
        os.mkdir(path + os.sep + "temp")
        playlist = prepareList(path, choreo)
        player = Player(playlist)
        player.play()
    finally:
        shutil.rmtree(path + os.sep + "temp")
    """
    root = tk.Tk()
    app = App(root, path)
    root.mainloop()