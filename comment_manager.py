import json
import os
import tkinter as tk

from setting import COMMENT_FOLDER, COMMENT_DISPLAY_RANGE


def add_comment(self):

    text = self.comment_entry.get().strip()

    if not text:
        return

    time = self.player.get_time() / 1000

    tag = self.tag_var.get()

    comment = {
        "time": time,
        "text": text,
        "tag": tag,
        "pinned": False
    }

    self.comments.append(comment)

    # 時間順ソート（重要）
    self.comments.sort(key=lambda c: c["time"])

    self.save_comments()

    self.refresh_comment_listbox()

    self.comment_entry.delete(0, "end")


def save_comments(self):

    if not self.music_file:
        return

    base = os.path.splitext(os.path.basename(self.music_file))[0]

    os.makedirs(COMMENT_FOLDER, exist_ok=True)

    path = os.path.join(COMMENT_FOLDER, base + "_comments.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(self.comments, f, ensure_ascii=False, indent=2)


def auto_load_comments(self):

    if not self.music_file:
        return

    base = os.path.splitext(os.path.basename(self.music_file))[0]

    path = os.path.join(COMMENT_FOLDER, base + "_comments.json")

    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        try:
            self.comments = json.load(f)
        except:
            self.comments = []

    # 時間順ソート
    self.comments.sort(key=lambda c: c["time"])

    self.refresh_comment_listbox()
    self.update_pinned_display()


def schedule_comments(self):

    self.clear_scheduled_comments()

    current = self.player.get_time() / 1000

    for comment in self.comments:

        delay = (comment["time"] - current) * 1000

        if delay < -COMMENT_DISPLAY_RANGE * 1000:
            continue

        job = self.root.after(
            max(0, int(delay)),
            lambda c=comment: self.show_comment(c)
        )

        self.scheduled_jobs.append(job)


def clear_scheduled_comments(self):

    for job in self.scheduled_jobs:
        try:
            self.root.after_cancel(job)
        except:
            pass

    self.scheduled_jobs.clear()


def pause_scheduled_comments(self):

    self.clear_scheduled_comments()


def resume_scheduled_comments(self):

    self.schedule_comments()


def show_comment(self, comment):

    text = f"[{self.format_comment_time(comment['time'])}] {comment['text']}"

    y = 20 + len(self.active_comments) * 30

    item = self.canvas.create_text(
        10,
        y,
        anchor="nw",
        text=text,
        fill="white",
        font=("Arial", 14, "bold")
    )

    self.active_comments.append(item)

    # 区間コメント対応
    if "end_time" in comment:

        duration = max(
            1000,
            int((comment["end_time"] - comment["time"]) * 1000)
        )

        self.root.after(
            duration,
            lambda i=item: self.remove_comment(i)
        )

    else:

        self.root.after(
            self.comment_display_time,
            lambda i=item: self.remove_comment(i)
        )


def remove_comment(self, item):

    self.canvas.delete(item)

    if item in self.active_comments:
        self.active_comments.remove(item)


def clear_comments_display(self):

    self.canvas.delete("all")

    self.active_comments.clear()


def format_comment_time(self, seconds):

    m = int(seconds) // 60

    s = int(seconds) % 60

    return f"{m:02}:{s:02}"


def refresh_comment_listbox(self):

    self.comment_listbox.delete(0, "end")

    self.displayed_comments = list(self.comments)

    for c in self.displayed_comments:

        time = self.format_comment_time(c["time"])

        if "end_time" in c:

            end = self.format_comment_time(c["end_time"])

            text = f"{time}-{end} [{c['tag']}] {c['text']}"

        else:

            text = f"{time} [{c['tag']}] {c['text']}"

        self.comment_listbox.insert("end", text)


def delete_selected_comment(self):

    selection = self.comment_listbox.curselection()

    if not selection:
        return

    index = selection[0]

    comment = self.displayed_comments[index]

    if comment in self.comments:

        self.comments.remove(comment)

    self.save_comments()

    self.refresh_comment_listbox()

    self.update_pinned_display()


def pin_selected_comment(self):

    selection = self.comment_listbox.curselection()

    if not selection:
        return

    index = selection[0]

    comment = self.displayed_comments[index]

    comment["pinned"] = True

    self.save_comments()

    self.update_pinned_display()


def unpin_selected_comment(self):

    selection = self.comment_listbox.curselection()

    if not selection:
        return

    index = selection[0]

    comment = self.displayed_comments[index]

    comment["pinned"] = False

    self.save_comments()

    self.update_pinned_display()


def update_pinned_display(self):

    for widget in self.pinned_frame.winfo_children():
        widget.destroy()

    for c in self.comments:

        if not c.get("pinned"):
            continue

        frame = tk.Frame(self.pinned_frame)

        frame.pack(anchor="w", fill="x")

        text = f"{self.format_comment_time(c['time'])} {c['text']}"

        label = tk.Label(frame, text=text)
        label.pack(side="left")

        # クリックジャンプ
        label.bind(
            "<Button-1>",
            lambda e, t=c["time"]: self.seek_music(t)
        )

        btn = tk.Button(
            frame,
            text="×",
            command=lambda com=c: self.unpin_comment_direct(com)
        )

        btn.pack(side="right")


def unpin_comment_direct(self, comment):

    comment["pinned"] = False

    self.save_comments()

    self.update_pinned_display()


def set_section_start(self):

    self.section_start = self.player.get_time() / 1000


def set_section_end(self):

    if self.section_start is None:
        return

    end = self.player.get_time() / 1000

    text = self.comment_entry.get()

    tag = self.tag_var.get()

    comment = {
        "time": self.section_start,
        "end_time": end,
        "text": text,
        "tag": tag,
        "pinned": False
    }

    self.comments.append(comment)

    self.comments.sort(key=lambda c: c["time"])

    self.section_start = None

    self.save_comments()

    self.refresh_comment_listbox()
