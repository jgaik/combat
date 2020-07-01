import os
import shutil
import random
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import ttk
import ttkwidgets

TRACKS = 10


def getNumbers(path):
    return sorted([int(x) for x in os.listdir(path) if os.path.isdir(path + os.sep + x) and x.isdigit()])


def randomChoreo(numbers):
    return random.choices(numbers, k=TRACKS)


def prepareList(path, tracklist):
    playlist = []
    images = []
    imageList = Image.new('1', (1920, 1080))
    listDraw = ImageDraw.Draw(imageList)
    listFont = ImageFont.truetype(path + os.sep + 'font.ttf', 50)
    listText = "Randomized Body Combat choreography playlist:" + os.linesep
    for track, choreo in tracklist:
        imgTemp = Image.new('1', (1920, 1080))
        tempDraw = ImageDraw.Draw(imgTemp)
        trackText = f" -> Track {track} - BodyCombat {choreo}"
        tempFont = ImageFont.truetype(path + os.sep + 'font.ttf', 100)
        tempDraw.text((20, 20), "Next:" + os.linesep +
                      trackText, fill='white', font=tempFont, spacing=30)
        listText = listText + trackText + os.linesep
        file = next(y for y in
                    os.listdir(path + os.sep + str(choreo)) if y[0] == str(track))
        playlist.append(os.path.abspath(path) + os.sep +
                        str(choreo) + os.sep + file)
        imgTemp.save(path + os.sep + "temp" + os.sep + f"{track}.png")
        images.append(path + os.sep + "temp" + os.sep + f"{track}.png")
    listDraw.text((20, 20), listText, fill='white', font=listFont, spacing=30)
    imageList.save(path + os.sep + "temp" + os.sep + "list.png")
    return {'playlist': playlist,
            'list': path + os.sep + "temp" + os.sep + "list.png",
            'images': images}


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
        self.frame_choreo.grid(row=0, column=0)
        self.frame_track.grid(row=0, column=1)
        self.frame_random.grid(row=0, column=2)
        self.frame_player.grid(row=1, column=0, columnspan=3)

        # choreo list
        ttk.Label(self.frame_choreo, text="Choreographies:").grid(sticky="W")
        self.var_choreo = tk.BooleanVar()
        self.var_choreo.set(True)
        self.check_choreo = ttk.Checkbutton(
            self.frame_choreo, text="Include all", variable=self.var_choreo, command=self.event_choreo_all)
        self.map_choreo = {}
        self.tree_choreo = ttkwidgets.CheckboxTreeview(
            self.frame_choreo, show="tree")
        self.tree_choreo.bind(
            "<<TreeviewSelect>>", self.event_choreo_check)
        self.list_choreo = []
        for item in getNumbers(self.path):
            id = self.tree_choreo.insert("", "end", text=item)
            self.map_choreo[id] = item
            self.tree_choreo.change_state(id, "checked")
            self.list_choreo.append(id)
        self.tree_choreo.grid(sticky="WE")
        self.check_choreo.grid(sticky="W")

        # track list
        ttk.Label(self.frame_track, text="Tracks:").grid(sticky="W")
        self.var_track = tk.BooleanVar()
        self.var_track.set(True)
        self.check_track = ttk.Checkbutton(
            self.frame_track, text="Include all", variable=self.var_track, command=self.event_track_all)
        self.map_track = {}
        self.tree_track = ttkwidgets.CheckboxTreeview(
            self.frame_track, show="tree")
        self.tree_track.bind(
            "<<TreeviewSelect>>", self.event_track_check)
        self.list_track = []
        for item in range(TRACKS):
            id = self.tree_track.insert("", "end", text=f"Track {item}")
            self.map_track[id] = item
            self.tree_track.change_state(id, "checked")
            self.list_track.append(id)
        self.tree_track.grid(sticky="WE")
        self.check_track.grid(sticky="W")

        # random list
        self.button_random = ttk.Button(
            self.frame_random, text="Randomize", command=self.event_random)
        self.button_random.grid()
        self.tree_random = ttkwidgets.CheckboxTreeview(
            self.frame_random, show="tree")
        self.tree_random.bind("<<TreeviewSelect>>", self.event_random_check)
        self.tree_random.grid()
        self.button_reroll = ttk.Button(
            self.frame_random, text="Reroll selected", image=self.image_icon, compound=tk.LEFT, command=self.event_reroll)
        self.button_reroll.grid()

        # player
        self.button_end = ttk.Button(
            self.frame_player, text="End", command=self.end)
        self.button_end.grid(sticky="W")

    def event_choreo_check(self, event):
        id = self.tree_choreo.focus()
        if id in self.list_choreo:
            self.tree_choreo.change_state(id, "unchecked")
            self.list_choreo.remove(id)
        else:
            self.tree_choreo.change_state(id, "checked")
            self.list_choreo.append(id)
        self.var_choreo.set(
            len(self.list_choreo) == len(self.map_choreo))

    def event_choreo_all(self):
        if self.var_choreo.get():
            for item in self.map_choreo:
                if not item in self.list_choreo:
                    self.tree_choreo.change_state(item, "checked")
                    self.list_choreo.append(item)
        else:
            for item in self.map_choreo:
                if item in self.list_choreo:
                    self.tree_choreo.change_state(item, "unchecked")
                    self.list_choreo.remove(item)

    def event_track_check(self, event):
        id = self.tree_track.focus()
        if id in self.list_track:
            self.tree_track.change_state(id, "unchecked")
            self.list_track.remove(id)
        else:
            self.tree_track.change_state(id, "checked")
            self.list_track.append(id)
        self.var_track.set(
            len(self.list_track) == len(self.map_track))

    def event_track_all(self):
        if self.var_track.get():
            for item in self.map_track:
                if not item in self.list_track:
                    self.tree_track.change_state(item, "checked")
                    self.list_track.append(item)
        else:
            for item in self.map_track:
                if item in self.list_track:
                    self.tree_track.change_state(item, "unchecked")
                    self.list_track.remove(item)

    def event_random(self):
        self.tree_random.delete(*self.tree_random.get_children())
        if self.list_track and self.list_choreo:
            list_choreo_random = randomChoreo(
                [self.map_choreo[id] for id in self.list_choreo])
            self.map_random = {}
            self.list_random = []
            for item in self.map_track:
                if item in self.list_track:
                    track = self.map_track[item]
                    choreo = list_choreo_random[track]
                    id = self.tree_random.insert(
                        "", "end", text=f"Track {track} - BodyCombat {choreo}")
                    self.map_random[id] = (track, choreo)

    def event_random_check(self, event):
        id = self.tree_random.focus()
        if id in self.list_random:
            self.tree_random.change_state(id, "unchecked")
            self.list_random.remove(id)
        else:
            self.tree_random.change_state(id, "checked")
            self.list_random.append(id)

    def event_reroll(self):
        list_choreo_number = [self.map_choreo[id] for id in self.list_choreo]
        if list_choreo_number:
            for item in self.list_random:
                track, choreo = self.map_random[item]
                list_choreo_copy = [
                    x for x in list_choreo_number if not x == choreo]
                if list_choreo_copy:
                    choreo = random.choice(list_choreo_copy)
                    self.tree_random.item(
                        item, **{'text': f"Track {track} - BodyCombat {choreo}"})

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
