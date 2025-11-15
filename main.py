import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np
import vlc
import json
import sys

class MediaPlayerGUI:
    def __init__(self, root, episodes_json_path):
        self.root = root
        self.root.configure(bg="black")

        # Load episode data from JSON
        with open(episodes_json_path, 'r') as file:
            self.episodes = json.load(file)

        self.current_episode_index = 0

        # Initialize VLC player
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Top bar for thumbnails
        self.top_bar = tk.Frame(self.root, bg="black", height=160)
        self.top_bar.pack(side="top", fill="x")

        # Video area
        self.video_area = tk.Label(self.root, bg="black", text="Video Player Area")
        self.video_area.pack(fill="both", expand=True)

        # CRASH FIX: Set the VLC video output handle based on the OS.
        if sys.platform.startswith('win'):
            self.player.set_hwnd(self.video_area.winfo_id())
        elif sys.platform.startswith('linux'):
            self.player.set_xwindow(self.video_area.winfo_id())
        elif sys.platform.startswith('darwin'):  # macOS
            self.player.set_nsobject(int(self.video_area.winfo_id()))

        # Load and display thumbnails
        self.thumbnail_labels = []
        self.display_thumbnails()

        # Start playback and updates
        self.load_episode(self.episodes[self.current_episode_index])
        self.update_playback_time()

    def create_thumbnail_with_overlay(self, title, start_time, elapsed_time, remaining_time):
        thumb_image = Image.new('RGB', (220, 140), color='darkgray')
        img_array = np.array(thumb_image)
        luminance = np.mean(img_array[:, :, :3] * [0.299, 0.587, 0.114])

        title_color = 'yellow' if luminance < 128 else 'white'
        time_color = 'white' if luminance < 128 else 'black'

        draw = ImageDraw.Draw(thumb_image)
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()

        draw.text((10, 10), title.upper(), fill=title_color, font=font)
        draw.text((10, 30), start_time, fill=time_color, font=font)
        draw.text((10, 50), f"{elapsed_time} / {remaining_time}", fill=time_color, font=font)

        return thumb_image

    def display_thumbnails(self):
        for episode in self.episodes:
            thumb_image = self.create_thumbnail_with_overlay(
                title=episode["title"],
                start_time=episode["start_time"],
                elapsed_time="00:00:00",
                remaining_time=f"-{episode['duration']//3600:02d}:{(episode['duration']%3600)//60:02d}:{episode['duration']%60:02d}"
            )
            thumb_photo = ImageTk.PhotoImage(thumb_image)

            thumb_label = tk.Label(self.top_bar, image=thumb_photo, bg="black")
            thumb_label.image = thumb_photo
            thumb_label.pack(side="left", padx=10, pady=10)
            self.thumbnail_labels.append(thumb_label)

    def load_episode(self, episode):
        media = self.instance.media_new(episode["media_path"])
        self.player.set_media(media)
        self.player.play()

    def update_playback_time(self):
        current_time = self.player.get_time() // 1000
        total_time = self.player.get_length() // 1000

        if current_time >= 0 and total_time > 0:
            elapsed_str = f"{current_time // 3600:02d}:{(current_time % 3600) // 60:02d}:{current_time % 60:02d}"
            remaining_str = f"-{(total_time - current_time) // 3600:02d}:{(total_time - current_time) % 3600 // 60:02d}:{(total_time - current_time) % 60:02d}"

            for i, episode in enumerate(self.episodes):
                if i == self.current_episode_index:
                    for widget in self.top_bar.winfo_children():
                        widget.destroy()
                    self.display_thumbnails()
                    self.thumbnail_labels[i].config(text=f"{episode['title']}\n{elapsed_str} / {remaining_str}")

        self.root.after(1000, self.update_playback_time)

# Run the application
root = tk.Tk()
app = MediaPlayerGUI(root, 'odd_couple_complete.json')
root.mainloop()
