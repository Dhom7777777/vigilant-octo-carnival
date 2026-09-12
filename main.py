"""
DivaTouch - a Project Diva style touch overlay video player.

This version plays video using ANDROID'S OWN built-in video player
(android.widget.VideoView, via pyjnius) instead of Kivy's ffpyplayer-based
VideoPlayer. This sidesteps a currently-broken FFmpeg/ffpyplayer
incompatibility in python-for-android and needs zero native C compilation
for video support.
"""

import os

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock

ASSETS = os.path.join(os.path.dirname(__file__), "assets")


def asset(name):
    return os.path.join(ASSETS, name)


IS_ANDROID = platform == "android"

if IS_ANDROID:
    from jnius import autoclass, PythonJavaClass, java_method
    from android.runnable import run_on_ui_thread
    from android.permissions import request_permissions, Permission

    perms = [Permission.READ_EXTERNAL_STORAGE]
    if hasattr(Permission, "READ_MEDIA_VIDEO"):
        perms.append(Permission.READ_MEDIA_VIDEO)
    request_permissions(perms)

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    VideoView = autoclass("android.widget.VideoView")
    FrameLayout = autoclass("android.widget.FrameLayout")
    FrameLayoutParams = autoclass("android.widget.FrameLayout$LayoutParams")
    ViewGroupLayoutParams = autoclass("android.view.ViewGroup$LayoutParams")

    class _OnPreparedListener(PythonJavaClass):
        __javainterfaces__ = ["android/media/MediaPlayer$OnPreparedListener"]
        __javacontext__ = "app"

        def __init__(self, callback):
            super().__init__()
            self.callback = callback

        @java_method("(Landroid/media/MediaPlayer;)V")
        def onPrepared(self, mp):
            self.callback()

    class AndroidVideoHolder(Widget):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.video_view = None
            self._on_ready_callback = None
            self.bind(pos=self._sync, size=self._sync)
            Clock.schedule_once(lambda dt: self._create_view(), 0)

        @run_on_ui_thread
        def _create_view(self):
            activity = PythonActivity.mActivity
            self.video_view = VideoView(activity)
            layout_params = FrameLayoutParams(
                ViewGroupLayoutParams.MATCH_PARENT,
                ViewGroupLayoutParams.MATCH_PARENT,
            )
            activity.addContentView(self.video_view, layout_params)
            Clock.schedule_once(lambda dt: self._sync(), 0)

        def _sync(self, *_args):
            if self.video_view is None:
                return
            density = Window._density if hasattr(Window, "_density") else 1
            scale = density if density else 1
            win_h = Window.height
            x_px = int(self.x * scale)
            y_px = int((win_h - self.top) * scale)
            w_px = max(1, int(self.width * scale))
            h_px = max(1, int(self.height * scale))
            self._apply_geometry(x_px, y_px, w_px, h_px)

        @run_on_ui_thread
        def _apply_geometry(self, x, y, w, h):
            if self.video_view is None:
                return
            params = self.video_view.getLayoutParams()
            if params is None:
                params = FrameLayoutParams(w, h)
            else:
                params.width = w
                params.height = h
            try:
                params.leftMargin = x
                params.topMargin = y
            except Exception:
                pass
            self.video_view.setLayoutParams(params)

        def load(self, path, on_ready=None):
            self._on_ready_callback = on_ready
            self._set_video_path(path)

        @run_on_ui_thread
        def _set_video_path(self, path):
            if self.video_view is None:
                return
            self.video_view.setVideoPath(path)
            listener = _OnPreparedListener(self._prepared)
            self._prepared_listener = listener
            self.video_view.setOnPreparedListener(listener)

        def _prepared(self):
            if self._on_ready_callback:
                Clock.schedule_once(lambda dt: self._on_ready_callback(), 0)

        @run_on_ui_thread
        def play(self):
            if self.video_view is not None:
                self.video_view.start()

        @run_on_ui_thread
        def pause(self):
            if self.video_view is not None:
                if self.video_view.isPlaying():
                    self.video_view.pause()
                else:
                    self.video_view.start()

else:
    class AndroidVideoHolder(Widget):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            with self.canvas:
                pass

        def load(self, path, on_ready=None):
            if on_ready:
                Clock.schedule_once(lambda dt: on_ready(), 0)

        def play(self):
            pass

        def pause(self):
            pass


class DivaButton(Image):
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
        self.title = "Select a video"
        self.size_hint = (0.9, 0.9)
        self.on_select = on_select

        root = BoxLayout(orientation="vertical")
        start_path = "/storage/emulated/0" if IS_ANDROID else os.path.expanduser("~")
        self.chooser = FileChooserListView(
            path=start_path,
            filters=["*.mp4", "*.mkv", "*.webm", "*.3gp"],
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


class DivaRoot(BoxLayout):
    def __init__(self, **kwargs):
        kwargs["orientation"] = "vertical"
        super().__init__(**kwargs)

        controls = BoxLayout(size_hint=(1, 0.12), spacing=8, padding=8)
        self.load_btn = Button(text="Load Video")
        self.load_btn.bind(on_release=self.open_file_chooser)
        self.play_btn = Button(text="Play/Pause")
        self.play_btn.bind(on_release=self.toggle_play)
        controls.add_widget(self.load_btn)
        controls.add_widget(self.play_btn)
        self.add_widget(controls)

        self.video = AndroidVideoHolder(size_hint=(1, 0.68))
        self.add_widget(self.video)

        button_row = FloatLayout(size_hint=(1, 0.20))
        button_defs = [
            ("BTN_SANKAKU_OFF.png", "BTN_SANKAKU_ON.png", 0.04, 0.05),
            ("BTN_SHIKAKU_OFF.png", "BTN_SHIKAKU_ON.png", 0.28, 0.02),
            ("BTN_BATSU_OFF.png", "BTN_BATSU_ON.png", 0.52, 0.05),
            ("BTN_MARU_OFF.png", "BTN_MARU_ON.png", 0.76, 0.10),
        ]
        for off_name, on_name, x, y in button_defs:
            btn = DivaButton(
                off_image=asset(off_name),
                on_image=asset(on_name),
                size_hint=(0.20, 0.85),
                pos_hint={"x": x, "y": y},
            )
            button_row.add_widget(btn)
        self.add_widget(button_row)

    def open_file_chooser(self, *_args):
        popup = LoadVideoPopup(on_select=self.load_video)
        popup.open()

    def load_video(self, path):
        self.video.load(path, on_ready=self.video.play)

    def toggle_play(self, *_args):
        self.video.pause()


class DivaTouchApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        return DivaRoot()


if __name__ == "__main__":
    DivaTouchApp().run()
