import os
import json
from tkinter import filedialog

PLAYLIST_FILE = "playlist.json"

SUPPORTED = (".mp3", ".wav", ".ogg", ".flac", ".m4a")


def add_to_playlist(self):

    files = filedialog.askopenfilenames(
        filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac *.m4a")]
    )

    if not files:
        return

    for f in files:

        if f not in self.playlist:

            self.playlist.append(f)

            name = os.path.basename(f)

            self.playlist_listbox.insert("end", name)

    save_playlist(self)


def add_folder(self):

    folder = filedialog.askdirectory()

    if not folder:
        return

    for file in os.listdir(folder):

        path = os.path.join(folder, file)

        if path.lower().endswith(SUPPORTED):

            if path not in self.playlist:

                self.playlist.append(path)

                name = os.path.basename(path)

                self.playlist_listbox.insert("end", name)

    save_playlist(self)


def remove_from_playlist(self):

    selection = self.playlist_listbox.curselection()

    if not selection:
        return

    index = selection[0]

    self.playlist_listbox.delete(index)

    if index < len(self.playlist):
        self.playlist.pop(index)

    save_playlist(self)


def play_selected_song(self, event=None):

    selection = self.playlist_listbox.curselection()

    if not selection:
        return

    index = selection[0]

    path = self.playlist[index]

    self.load_music_from_playlist(path)

    self.play_music()


def next_song(self):

    if not self.playlist:
        return

    selection = self.playlist_listbox.curselection()

    if not selection:
        index = 0
    else:
        index = selection[0] + 1

    if index >= len(self.playlist):

        if getattr(self, "repeat_enabled", False):
            index = 0
        else:
            return

    self.playlist_listbox.selection_clear(0, "end")
    self.playlist_listbox.selection_set(index)
    self.playlist_listbox.activate(index)

    path = self.playlist[index]

    self.load_music_from_playlist(path)

    self.play_music()


def prev_song(self):

    if not self.playlist:
        return

    selection = self.playlist_listbox.curselection()

    if not selection:
        return

    index = selection[0] - 1

    if index < 0:
        return

    self.playlist_listbox.selection_clear(0, "end")
    self.playlist_listbox.selection_set(index)
    self.playlist_listbox.activate(index)

    path = self.playlist[index]

    self.load_music_from_playlist(path)

    self.play_music()


def load_music_from_playlist(self, file_path):

    if not file_path:
        return

    self.stop_music()

    self.music_file = file_path

    media = self.instance.media_new(file_path)

    self.player.set_media(media)

    self.get_music_length()

    self.comments = []

    self.auto_load_comments()

    self.refresh_comment_listbox()


# ==========================
# プレイリスト保存
# ==========================

def save_playlist(self):

    try:

        with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:

            json.dump(self.playlist, f, indent=2)

    except Exception as e:

        print("Playlist save error:", e)


# ==========================
# プレイリスト読み込み
# ==========================

def load_playlist(self):

    if not os.path.exists(PLAYLIST_FILE):
        return

    try:

        with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:

            self.playlist = json.load(f)

        self.playlist_listbox.delete(0, "end")

        for path in self.playlist:

            name = os.path.basename(path)

            self.playlist_listbox.insert("end", name)

    except Exception as e:

        print("Playlist load error:", e)


# ==========================
# ドラッグドロップ追加
# ==========================

def drop_files(self, event):

    files = self.root.tk.splitlist(event.data)

    for f in files:

        if os.path.isfile(f) and f.lower().endswith(SUPPORTED):

            if f not in self.playlist:

                self.playlist.append(f)

                name = os.path.basename(f)

                self.playlist_listbox.insert("end", name)

    save_playlist(self)