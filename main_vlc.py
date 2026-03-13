import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD
import vlc

from setting import TAG_COLORS, TAG_OPTIONS, COMMENT_DISPLAY_TIME

from comment_sync import CommentSyncEngine

from comment_manager import (
    add_comment,
    schedule_comments,
    clear_scheduled_comments,
    pause_scheduled_comments,
    resume_scheduled_comments,
    show_comment,
    format_comment_time,
    remove_comment,
    clear_comments_display,
    auto_load_comments,
    save_comments,
    delete_selected_comment,
    refresh_comment_listbox,
    update_pinned_display,
    pin_selected_comment,
    unpin_selected_comment,
    set_section_start,
    set_section_end
)

from playlist_manager import (
    add_to_playlist,
    remove_from_playlist,
    play_selected_song,
    next_song,
    prev_song,
    load_music_from_playlist,
    add_folder,
    save_playlist,
    load_playlist,
    drop_files
)


class MusicCommentApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Music Comment App v1.1")

        self.music_file = None

        # プレイリスト
        self.playlist = []

        self.comments = []
        self.displayed_comments = []
        self.active_comments = []

        self.comment_display_time = COMMENT_DISPLAY_TIME

        self.is_playing = False
        self.scheduled_jobs = []

        self.section_start = None

        # VLC
        self.instance = vlc.Instance(
            "--no-xlib",
            "--quiet",
            "--no-video-title-show"
        )

        self.player = self.instance.media_player_new()

        self.music_length = 0

        self.loop_a = None
        self.loop_b = None
        self.loop_enabled = False

        from ui_builder import build_ui
        build_ui(self)

        # プレイリスト読み込み
        self.load_playlist()

        # シャッフル / リピート
        self.shuffle_enabled = False
        self.repeat_enabled = False

        # コメント同期エンジン
        self.comment_sync = CommentSyncEngine(
            self.player,
            self,
            self.show_comment
        )

        # 曲終了監視
        self.root.after(1000, self.check_song_end)

        # DnD
        self.root.drop_target_register('*')
        self.root.dnd_bind('<<Drop>>', self.drop_files)

    # ==================================
    # 音楽読み込み
    # ==================================

    def load_music(self):

        file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac *.m4a")]
        )

        if not file_path:
            return

        self.load_music_from_playlist(file_path)

    # ==================================
    # 再生
    # ==================================

    def play_music(self):

        if not self.music_file:
            return

        self.player.play()

        self.is_playing = True

        self.root.after(200, self.schedule_comments)

        self.update_seek_bar()

        # 同期エンジン開始
        self.comment_sync.start()

    def pause_music(self):

        if self.is_playing:

            self.player.pause()

            self.is_playing = False

            self.pause_scheduled_comments()

            self.comment_sync.stop()

    def stop_music(self):

        self.player.stop()

        self.is_playing = False

        self.seek_var.set(0)

        self.clear_scheduled_comments()

        self.clear_comments_display()

        self.comment_sync.stop()

    # ==================================
    # 曲終了
    # ==================================

    def check_song_end(self):

        state = self.player.get_state()

        if state == vlc.State.Ended:

            if self.shuffle_enabled:

                import random

                index = random.randint(0, len(self.playlist) - 1)

                self.playlist_listbox.selection_clear(0, "end")

                self.playlist_listbox.selection_set(index)

                path = self.playlist[index]

                self.load_music_from_playlist(path)

                self.play_music()

            else:

                self.next_song()

        self.root.after(1000, self.check_song_end)

    # ==================================
    # シャッフル
    # ==================================

    def toggle_shuffle(self):

        self.shuffle_enabled = not self.shuffle_enabled

        if self.shuffle_enabled:

            self.shuffle_button.config(text=" シャッフル ON")

        else:

            self.shuffle_button.config(text=" シャッフル OFF")

    def toggle_repeat(self):

        self.repeat_enabled = not self.repeat_enabled

        if self.repeat_enabled:

            self.repeat_button.config(text=" リピート ON")

        else:

            self.repeat_button.config(text=" リピート OFF")

    # ==================================
    # 音量
    # ==================================

    def change_volume(self, value):

        volume = int(float(value))

        self.player.audio_set_volume(volume)

    # ==================================
    # シーク
    # ==================================

    def seek_music(self, value):

        if not self.music_file:
            return

        ms = int(float(value) * 1000)

        self.player.set_time(ms)

        self.clear_scheduled_comments()

        self.clear_comments_display()

        self.schedule_comments()

        # 同期リセット
        self.comment_sync.reset()

    def seek_forward_5(self):

        t = self.player.get_time() + 5000

        self.player.set_time(t)

    def seek_back_5(self):

        t = max(0, self.player.get_time() - 5000)

        self.player.set_time(t)

    # ==================================
    # 再生バー更新
    # ==================================

    def update_seek_bar(self):

        if not self.is_playing:
            return

        pos = self.player.get_time() / 1000

        self.seek_var.set(pos)

        current = self.format_time(pos)

        total = self.format_time(self.music_length)

        self.time_label.config(text=f"{current} / {total}")

        self.check_ab_loop()

        self.root.after(500, self.update_seek_bar)

    # ==================================
    # ABループ
    # ==================================

    def set_loop_a(self):

        self.loop_a = self.player.get_time() / 1000

    def set_loop_b(self):

        self.loop_b = self.player.get_time() / 1000

    def toggle_ab_loop(self):

        self.loop_enabled = not self.loop_enabled

    def check_ab_loop(self):

        if not self.loop_enabled:
            return

        if self.loop_a is None or self.loop_b is None:
            return

        pos = self.player.get_time() / 1000

        if pos >= self.loop_b:

            self.player.set_time(int(self.loop_a * 1000))

    # ==================================
    # コメント表示時間変更
    # ==================================

    def change_comment_display_time(self, value):

        self.comment_display_time = int(value) * 1000

    # ==================================
    # 曲長取得
    # ==================================

    def get_music_length(self):

        media = self.instance.media_new(self.music_file)

        media.parse()

        length = media.get_duration()

        self.music_length = length / 1000 if length > 0 else 180

        self.seek_scale.config(to=self.music_length)

    # ==================================
    # 時刻フォーマット
    # ==================================

    def format_time(self, seconds):

        seconds = int(seconds)

        m = seconds // 60

        s = seconds % 60

        return f"{m:02}:{s:02}"

    # ==================================
    # コメントジャンプ
    # ==================================

    def jump_to_comment(self, event):

        selection = self.comment_listbox.curselection()

        if not selection:
            return

        index = selection[0]

        comment = self.displayed_comments[index]

        self.seek_music(comment["time"])


# ==================================
# comment_manager メソッド登録
# ==================================

MusicCommentApp.add_comment = add_comment
MusicCommentApp.schedule_comments = schedule_comments
MusicCommentApp.clear_scheduled_comments = clear_scheduled_comments
MusicCommentApp.pause_scheduled_comments = pause_scheduled_comments
MusicCommentApp.resume_scheduled_comments = resume_scheduled_comments
MusicCommentApp.show_comment = show_comment
MusicCommentApp.format_comment_time = format_comment_time
MusicCommentApp.remove_comment = remove_comment
MusicCommentApp.clear_comments_display = clear_comments_display
MusicCommentApp.auto_load_comments = auto_load_comments
MusicCommentApp.save_comments = save_comments
MusicCommentApp.delete_selected_comment = delete_selected_comment
MusicCommentApp.refresh_comment_listbox = refresh_comment_listbox
MusicCommentApp.update_pinned_display = update_pinned_display
MusicCommentApp.pin_selected_comment = pin_selected_comment
MusicCommentApp.unpin_selected_comment = unpin_selected_comment
MusicCommentApp.set_section_start = set_section_start
MusicCommentApp.set_section_end = set_section_end


# ==================================
# playlist_manager メソッド登録
# ==================================

MusicCommentApp.add_to_playlist = add_to_playlist
MusicCommentApp.remove_from_playlist = remove_from_playlist
MusicCommentApp.play_selected_song = play_selected_song
MusicCommentApp.next_song = next_song
MusicCommentApp.prev_song = prev_song
MusicCommentApp.load_music_from_playlist = load_music_from_playlist
MusicCommentApp.add_folder = add_folder
MusicCommentApp.save_playlist = save_playlist
MusicCommentApp.load_playlist = load_playlist
MusicCommentApp.drop_files = drop_files


# ==================================
# 起動
# ==================================

if __name__ == "__main__":

    root = TkinterDnD.Tk()

    app = MusicCommentApp(root)

    root.mainloop()
