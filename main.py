import vlc
import os
import shutil
import random
from time import sleep
from threading import Thread
from pynput import keyboard
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import ttk
import ttkwidgets


def getNumbers(path):
    return sorted([int(x) for x in os.listdir(path) if os.path.isdir(path + os.sep + x) and x.isdigit()])


def randomChoreo(numbers):
    return random.choices(numbers, k=10)


def prepareList(path, choreoNumbers):
    playlist = []
    images = []
    imageList = Image.new('1', (1920, 1080))
    listDraw = ImageDraw.Draw(imageList)
    listFont = ImageFont.truetype(path + os.sep + 'font.ttf', 50)
    listText = "Randomized Body Combat choreography playlist:" + os.linesep
    for x in range(10):
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


class App:

    def __init__(self, master, path):
        self.master = master
        self.path = path
        self.master.protocol("WM_DELETE_WINDOW", self.end)
        os.mkdir(path + os.sep + "temp")
        icon = Image.open(path + os.sep + "icon.png")
        icon = icon.resize((20, 20))
        self.image_icon = ImageTk.PhotoImage(icon)

        self.list_choreo = {}
        self.tree_include_choreo = ttkwidgets.CheckboxTreeview(self.master)
        for item in getNumbers(self.path):
            self.list_choreo[item] = self.tree_include_choreo.insert(
                "", "end", text=item)
            self.tree_include_choreo.change_state(
                self.list_choreo[item], "checked")
        self.tree_include_choreo.pack()

        self.list_track = {}
        self.tree_include_track = ttkwidgets.CheckboxTreeview(self.master)
        for item in range(10):
            self.list_choreo[item] = self.tree_include_track.insert(
                "", "end", text=f"Track {item}")
            self.tree_include_track.change_state(
                self.list_choreo[item], "checked")
        self.tree_include_track.pack()

        self.check_all_choreo = ttk.Checkbutton(self.master, text="All")
        self.check_all_track = ttk.Checkbutton(self.master, text="All")

        self.button = ttk.Button(
            self.master, image=self.image_icon)
        self.button.pack()

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
