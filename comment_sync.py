import time
import threading


class CommentSyncEngine:

    def __init__(self, player, comment_manager, callback):

        self.player = player
        self.comment_manager = comment_manager
        self.callback = callback

        self.running = False
        self.thread = None

        self.interval = 0.1

    def start(self):

        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self.loop)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):

        self.running = False

    def loop(self):

        while self.running:

            current_time = self.player.get_time()

            comments = self.comment_manager.get_comments()

            for comment in comments:

                if comment["displayed"]:
                    continue

                if comment["time"] <= current_time:

                    self.callback(comment)

                    comment["displayed"] = True

            time.sleep(self.interval)

    def reset(self):

        comments = self.comment_manager.get_comments()

        for c in comments:
            c["displayed"] = False