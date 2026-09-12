"""
Override for python-for-android's built-in ffmpeg recipe.

As of the ffmpeg 8.0.1 recipe bump in python-for-android, the
libavcodec/avfft.h header was removed upstream in FFmpeg. ffpyplayer
(the video backend Kivy uses on Android) still includes that header, so
building ffpyplayer against ffmpeg 8.0.1 fails with:

    fatal error: 'libavcodec/avfft.h' file not found

This subclasses the real, installed ffmpeg recipe (inheriting all of its
build logic and codec flags) and only overrides the version/url to an
older FFmpeg release that still ships avfft.h.

Recipe `patches` paths are resolved relative to the file that DEFINES the
recipe class. Since this subclass lives in our own local_recipes folder,
naively inheriting `patches = ['patches/configure.patch', ...]` would look
for those files next to *this* file (where they don't exist) instead of
next to python-for-android's original ffmpeg recipe. So we rebuild the
list as absolute paths pointing at the original recipe's own patches/
directory, wherever pip installed it.

See: https://github.com/kivy/python-for-android/issues/3344
"""

import os
import pythonforandroid.recipes.ffmpeg as _orig_ffmpeg_module
from pythonforandroid.recipes.ffmpeg import FFMpegRecipe

_orig_dir = os.path.dirname(os.path.abspath(_orig_ffmpeg_module.__file__))


class FFMpegRecipeCompat(FFMpegRecipe):
    version = '7.1'
    url = 'https://www.ffmpeg.org/releases/ffmpeg-{version}.tar.xz'
    patches = [os.path.join(_orig_dir, p) for p in FFMpegRecipe.patches]


recipe = FFMpegRecipeCompat()
