import tkinter as tk
from setting import TAG_OPTIONS
from playlist_manager import (
    add_to_playlist,
    remove_from_playlist,
    play_selected_song,
    add_folder,
    save_playlist
)


def build_ui(self):

    # =====================================
    # メインレイアウト
    # =====================================

    main_frame = tk.Frame(self.root)
    main_frame.pack(fill="both", expand=True)

    # =====================================
    # プレイリストエリア（左）
    # =====================================

    playlist_frame = tk.Frame(main_frame)
    playlist_frame.pack(side="left", fill="y", padx=5, pady=5)

    tk.Label(
        playlist_frame,
        text="プレイリスト",
        font=("Arial", 12, "bold")
    ).pack(pady=5)

    self.playlist_listbox = tk.Listbox(
        playlist_frame,
        width=30,
        height=25
    )

    self.playlist_listbox.pack(fill="y")

    self.playlist_listbox.bind(
        "<Double-Button-1>",
        self.play_selected_song
    )

    playlist_button_frame = tk.Frame(playlist_frame)
    playlist_button_frame.pack(pady=5)

    tk.Button(
        playlist_button_frame,
        text="フォルダ追加",
        width=10,
        command=self.add_folder
    ).grid(row=1, column=0, padx=3, pady=3)

    tk.Button(
        playlist_button_frame,
        text="保存",
        width=10,
        command=self.save_playlist
    ).grid(row=1, column=1, padx=3, pady=3)

    tk.Button(
        playlist_button_frame,
        text="追加",
        width=10,
        command=self.add_to_playlist
    ).grid(row=0, column=0, padx=3)

    tk.Button(
        playlist_button_frame,
        text="削除",
        width=10,
        command=self.remove_from_playlist
    ).grid(row=0, column=1, padx=3)

    # =====================================
    # 右側プレイヤーエリア
    # =====================================

    player_frame = tk.Frame(main_frame)
    player_frame.pack(side="left", fill="both", expand=True)

    # ==============================
    # 音楽読み込み
    # ==============================

    tk.Button(
        player_frame,
        text="音楽を開く",
        command=self.load_music
    ).pack(pady=5)

    # ==============================
    # 再生コントロール
    # ==============================

    control_frame = tk.Frame(player_frame)
    control_frame.pack(pady=5)

    mode_frame = tk.Frame(player_frame)
    mode_frame.pack(pady=5)

    self.shuffle_button = tk.Button(
        mode_frame,
        text="🔀 シャッフル OFF",
        width=15,
        command=self.toggle_shuffle
    )

    self.shuffle_button.grid(row=0, column=0, padx=5)

    self.repeat_button = tk.Button(
        mode_frame,
        text="🔁 リピート OFF",
        width=15,
        command=self.toggle_repeat
    )

    self.repeat_button.grid(row=0, column=1, padx=5)

    tk.Button(
        control_frame,
        text="再生",
        width=10,
        command=self.play_music
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        control_frame,
        text="一時停止",
        width=10,
        command=self.pause_music
    ).grid(row=0, column=1, padx=5)

    tk.Button(
        control_frame,
        text="停止",
        width=10,
        command=self.stop_music
    ).grid(row=0, column=2, padx=5)

    # ==============================
    # ボリューム
    # ==============================

    volume_frame = tk.Frame(player_frame)
    volume_frame.pack(pady=5)

    tk.Label(
        volume_frame,
        text="音量"
    ).grid(row=0, column=0)

    self.volume_var = tk.DoubleVar(value=70)

    self.volume_scale = tk.Scale(
        volume_frame,
        from_=0,
        to=100,
        orient="horizontal",
        variable=self.volume_var,
        command=self.change_volume,
        length=200
    )

    self.volume_scale.grid(row=0, column=1)

    # ==============================
    # シークバー
    # ==============================

    self.seek_var = tk.DoubleVar()

    self.seek_scale = tk.Scale(
        player_frame,
        from_=0,
        to=100,
        orient="horizontal",
        variable=self.seek_var,
        length=600,
        command=self.seek_music
    )

    self.seek_scale.pack(pady=5)

    # ==============================
    # 再生時間
    # ==============================

    self.time_label = tk.Label(
        player_frame,
        text="00:00 / 00:00",
        font=("Arial", 12)
    )

    self.time_label.pack()

    # ==============================
    # A-Bループ
    # ==============================

    ab_frame = tk.Frame(player_frame)
    ab_frame.pack(pady=5)

    tk.Button(
        ab_frame,
        text="A地点",
        command=self.set_loop_a
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        ab_frame,
        text="B地点",
        command=self.set_loop_b
    ).grid(row=0, column=1, padx=5)

    tk.Button(
        ab_frame,
        text="ABループ",
        command=self.toggle_ab_loop
    ).grid(row=0, column=2, padx=5)

    # ==============================
    # コメント入力
    # ==============================

    comment_frame = tk.Frame(player_frame)
    comment_frame.pack(pady=10)

    tk.Label(
        comment_frame,
        text="コメント"
    ).grid(row=0, column=0)

    self.comment_entry = tk.Entry(
        comment_frame,
        width=40
    )

    self.comment_entry.grid(row=0, column=1)

    self.comment_entry.bind(
        "<Return>",
        lambda e: self.add_comment()
    )

    tk.Label(
        comment_frame,
        text="タグ"
    ).grid(row=0, column=2, padx=5)

    self.tag_var = tk.StringVar(value="メロディ")

    tag_menu = tk.OptionMenu(
        comment_frame,
        self.tag_var,
        *TAG_OPTIONS
    )

    tag_menu.grid(row=0, column=3)

    # ==============================
    # コメントボタン
    # ==============================

    button_frame = tk.Frame(player_frame)
    button_frame.pack(pady=5)

    tk.Button(
        button_frame,
        text="コメント追加",
        command=self.add_comment
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        button_frame,
        text="区間開始",
        command=self.set_section_start
    ).grid(row=0, column=1, padx=5)

    tk.Button(
        button_frame,
        text="区間終了",
        command=self.set_section_end
    ).grid(row=0, column=2, padx=5)

    # ==============================
    # コメント表示ウィンドウ
    # ==============================

    self.comment_window = tk.Toplevel(self.root)
    self.comment_window.title("コメント表示")

    self.comment_window.geometry("800x700")

    canvas_frame = tk.Frame(self.comment_window)
    canvas_frame.pack(fill="both", expand=True)

    self.canvas = tk.Canvas(
        canvas_frame,
        bg="black"
    )

    self.canvas.pack(fill="both", expand=True)

    # ==============================
    # 固定コメント
    # ==============================

    tk.Label(
        self.comment_window,
        text="★ 固定コメント",
        font=("Arial", 12, "bold")
    ).pack(pady=(5, 0))

    self.pinned_frame = tk.Frame(
        self.comment_window,
        bg="#222222"
    )

    self.pinned_frame.pack(
        fill="x",
        padx=5,
        pady=5
    )

    # ==============================
    # コメントリスト
    # ==============================

    self.comment_listbox = tk.Listbox(
        self.comment_window
    )

    self.comment_listbox.pack(
        fill="both",
        expand=True
    )

    self.comment_listbox.bind(
        "<Double-Button-1>",
        self.jump_to_comment
    )

    # ==============================
    # 右クリックメニュー
    # ==============================

    self.comment_menu = tk.Menu(
        self.comment_window,
        tearoff=0
    )

    self.comment_menu.add_command(
        label="★ 固定",
        command=self.pin_selected_comment
    )

    self.comment_menu.add_command(
        label="固定解除",
        command=self.unpin_selected_comment
    )

    self.comment_menu.add_separator()

    self.comment_menu.add_command(
        label="削除",
        command=self.delete_selected_comment
    )

    self.comment_listbox.bind(
        "<Button-3>",
        lambda e: self.comment_menu.post(e.x_root, e.y_root)
    )

    # ==============================
    # 初期音量
    # ==============================

    self.change_volume(70)


# ==============================
# Playlistメソッドをクラスに追加
# ==============================

def attach_playlist_methods(app):

    app.add_to_playlist = add_to_playlist.__get__(app)
    app.remove_from_playlist = remove_from_playlist.__get__(app)
    app.play_selected_song = play_selected_song.__get__(app)