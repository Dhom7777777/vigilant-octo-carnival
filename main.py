"""
DivaTouch - a simple touch-button overlay video player
inspired by Project Diva's Sankaku/Maru/Batsu/Shikaku button layout.

- Pick an MP4 from the device.
- The video plays fullscreen in the background.
- Four buttons overlay the video. Pressing/holding a button swaps
  its image to the "ON" state; releasing swaps it back to "OFF".
"""

import os

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.videoplayer import VideoPlayer
from kivy.core.window import Window
from kivy.utils import platform

ASSETS = os.path.join(os.path.dirname(__file__), "assets")


def asset(name):
    return os.path.join(ASSETS, name)


# Request Android runtime permissions so we can read the user's video files.
if platform == "android":
    try:
        from android.permissions import request_permissions, Permission

        perms = [Permission.READ_EXTERNAL_STORAGE]
        # Android 13+ uses granular media permissions.
        if hasattr(Permission, "READ_MEDIA_VIDEO"):
            perms.append(Permission.READ_MEDIA_VIDEO)
        request_permissions(perms)
    except Exception:
        pass


class DivaButton(Image):
    """A button that swaps between an OFF and ON image while held."""

    def __init__(self, off_image, on_image, **kwargs):
        super().__init__(**kwargs)
        self.off_image = off_image
        self.on_image = on_image
        self.source = self.off_image
        self.allow_stretch = True
        self.keep_ratio = True
        self._active_touch = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self._active_touch is None:
            self._active_touch = touch.uid
            touch.grab(self)
            self.source = self.on_image
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._active_touch = None
            self.source = self.off_image
            return True
        return super().on_touch_up(touch)


class LoadVideoPopup(Popup):
    def __init__(self, on_select, **kwargs):
        super().__init__(**kwargs)
        self.title = "Select an MP4"
        self.size_hint = (0.9, 0.9)
        self.on_select = on_select

        root = BoxLayout(orientation="vertical")
        start_path = "/storage/emulated/0" if platform == "android" else os.path.expanduser("~")
        self.chooser = FileChooserListView(
            path=start_path,
            filters=["*.mp4", "*.mkv", "*.webm"],
        )
        root.add_widget(self.chooser)

        buttons = BoxLayout(size_hint_y=None, height="48dp", spacing=8, padding=8)
        select_btn = Button(text="Select")
        select_btn.bind(on_release=self._select)
        cancel_btn = Button(text="Cancel")
        cancel_btn.bind(on_release=self.dismiss)
        buttons.add_widget(select_btn)
        buttons.add_widget(cancel_btn)
        root.add_widget(buttons)

        self.content = root

    def _select(self, *_args):
        if self.chooser.selection:
            path = self.chooser.selection[0]
            self.dismiss()
            self.on_select(path)


class DivaRoot(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Background video player. No default source until the user picks one.
        self.video = VideoPlayer(
            source="",
            state="stop",
            options={"eos": "stop"},
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )
        # Hide VideoPlayer's own transport bar; we drive it ourselves.
        self.video.opacity = 1
        self.add_widget(self.video)

        # "Load Video" button, top-left corner.
        self.load_btn = Button(
            text="Load Video",
            size_hint=(0.22, 0.08),
            pos_hint={"x": 0.02, "top": 0.98},
        )
        self.load_btn.bind(on_release=self.open_file_chooser)
        self.add_widget(self.load_btn)

        # Play/Pause button, next to Load.
        self.play_btn = Button(
            text="Play/Pause",
            size_hint=(0.22, 0.08),
            pos_hint={"x": 0.26, "top": 0.98},
        )
        self.play_btn.bind(on_release=self.toggle_play)
        self.add_widget(self.play_btn)

        # The four Diva-style buttons, arranged left-to-right along the
        # bottom edge like the reference screenshot (Triangle, Square,
        # Cross, Circle).
        button_defs = [
            ("BTN_SANKAKU_OFF.png", "BTN_SANKAKU_ON.png", 0.06, 0.04),
            ("BTN_SHIKAKU_OFF.png", "BTN_SHIKAKU_ON.png", 0.28, 0.02),
            ("BTN_BATSU_OFF.png", "BTN_BATSU_ON.png", 0.50, 0.04),
            ("BTN_MARU_OFF.png", "BTN_MARU_ON.png", 0.72, 0.10),
        ]
        for off_name, on_name, x, y in button_defs:
            btn = DivaButton(
                off_image=asset(off_name),
                on_image=asset(on_name),
                size_hint=(0.22, 0.22),
                pos_hint={"x": x, "y": y},
            )
            self.add_widget(btn)

    def open_file_chooser(self, *_args):
        popup = LoadVideoPopup(on_select=self.load_video)
        popup.open()

    def load_video(self, path):
        self.video.source = path
        self.video.state = "play"

    def toggle_play(self, *_args):
        if not self.video.source:
            return
        self.video.state = "play" if self.video.state != "play" else "pause"


class DivaTouchApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        return DivaRoot()


if __name__ == "__main__":
    DivaTouchApp().run()
