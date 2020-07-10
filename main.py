import os
import shutil
import random
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import ttk
import ttkwidgets
#import player
TRACKS = 9


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

        # choreo list
        self.var_choreo = tk.BooleanVar()
        self.var_choreo.set(True)
        self.check_choreo = ttk.Checkbutton(
            self.master, text="Include all", variable=self.var_choreo, command=self.event_choreo_all)
        self.map_choreo = {}
        self.tree_choreo = ttkwidgets.CheckboxTreeview(
            self.master, show="tree", height=TRACKS)
        self.tree_choreo.column("#0", width=120)
        self.tree_choreo.bind(
            "<<TreeviewSelect>>", self.event_choreo_check)
        self.list_choreo = []
        for item in getNumbers(self.path):
            id = self.tree_choreo.insert("", "end", text=f"BC {item}")
            self.map_choreo[id] = item
            self.tree_choreo.change_state(id, "checked")
            self.list_choreo.append(id)

        ttk.Label(self.master, text="Choreographies:").grid(columnspan=2,sticky="W")
        self.tree_choreo.grid(column=0, columnspan=2, sticky="WE", pady=5)
        self.check_choreo.grid(column=0, columnspan=2, sticky="W", pady=5)

        # track list
        self.var_track = tk.BooleanVar()
        self.var_track.set(True)
        self.check_track = ttk.Checkbutton(
            self.master, text="Include all", variable=self.var_track, command=self.event_track_all)
        self.map_track = {}
        self.tree_track = ttkwidgets.CheckboxTreeview(
            self.master, show="tree", height=TRACKS)
        self.tree_track.column("#0", width=100)
        self.tree_track.bind(
            "<<TreeviewSelect>>", self.event_track_check)
        self.list_track = []
        for item in range(TRACKS):
            id = self.tree_track.insert("", "end", text=f"Track {item}")
            self.map_track[id] = item
            self.tree_track.change_state(id, "checked")
            self.list_track.append(id)
            
        ttk.Label(self.master, text="Tracks:").grid(row=0, column=2, sticky="W")
        self.tree_track.grid(row=1, column=2, sticky="WE", pady=5)
        self.check_track.grid(row=2, column=2,sticky="W", pady=5)

        # random list
        self.button_random = ttk.Button(
            self.master, text="Randomize", command=self.event_random)
        
        self.tree_random = ttkwidgets.CheckboxTreeview(
            self.master, show="tree", height=TRACKS)
        self.tree_random.bind("<<TreeviewSelect>>", self.event_random_check)
        self.tree_random.column("#0", width=150)
        self.button_reroll = ttk.Button(
            self.master, text="Reroll selected", image=self.image_icon, compound=tk.LEFT, command=self.event_reroll)

        self.button_random.grid(row=0, column=3)
        self.tree_random.grid(row=1, column=3,pady=3)
        self.button_reroll.grid(row=2, column=3,pady=2)

        # player
        self.var_autoplay = tk.BooleanVar()
        self.check_autoplay = ttk.Checkbutton(
            self.master, text="Autoplay", variable=self.var_autoplay,
            command=self.event_check_autoplay)
        self.spin_delay = ttk.Spinbox(
            self.master, from_=1, to=9, width=1)
        self.spin_delay.set(1)
        self.label_delay = ttk.Label(self.master, text="Delay[s]:")
        self.button_play = ttk.Button(
            self.master, text="Play", command=self.event_play)
        self.button_end = ttk.Button(
            self.master, text="End", command=self.end)

        self.check_autoplay.grid(row=3,column=0, columnspan=2, sticky="W")
        self.label_delay.grid(row=4,column=0)
        self.spin_delay.grid(row=4, column=1)
        self.button_play.grid(row=3, column=2, rowspan=2, pady=15, sticky="W")
        self.button_end.grid(row=3, column=3, rowspan=2, pady=15, padx=10, sticky="E")

        self.event_check_autoplay()
        self.event_random()
    
    def event_check_autoplay(self):
      if self.var_autoplay.get():
        self.spin_delay.grid()
        self.label_delay.grid()
        self.master.bind("<Key>", self.event_key_spin)
      else:
        self.spin_delay.grid_remove()
        self.label_delay.grid_remove()

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
                        "", "end", text=f"Track {track} - BC {choreo}")
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

    def event_play(self):
        self.master.withdraw()
        self.player = player.Player(1)
        self.player.add_playlist(prepareList(
            self.path, self.map_random.values()))
        self.player.play(True)
        self.player.wait_end()
        self.master.deiconify()

    def event_key_spin(self, event):
        if self.var_autoplay.get():
            if event.keysym == "Up":
                self.spin_delay.event_generate("<<Increment>>")
            if event.keysym == "Down":
                self.spin_delay.event_generate("<<Decrement>>")

    def end(self):
        shutil.rmtree(self.path + os.sep + "temp")
        self.master.destroy()


if __name__ == "__main__":
    path = os.getcwd() + os.sep + "random"
    root = tk.Tk()
    app = App(root, path)
    root.mainloop()
