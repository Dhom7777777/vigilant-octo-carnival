"""
Override for python-for-android's built-in ffmpeg recipe.

As of the ffmpeg 8.0.1 recipe bump in python-for-android, the
libavcodec/avfft.h header was removed upstream in FFmpeg. ffpyplayer
(the video backend Kivy uses on Android) still includes that header, so
building ffpyplayer against ffmpeg 8.0.1 fails with:

    fatal error: 'libavcodec/avfft.h' file not found

This subclasses the real, installed ffmpeg recipe (inheriting all of its
build logic, patches, and codec flags) and only overrides the version/url
to an older FFmpeg release that still ships avfft.h.

See: https://github.com/kivy/python-for-android/issues/3344
"""

from pythonforandroid.recipes.ffmpeg import FFMpegRecipe


class FFMpegRecipeCompat(FFMpegRecipe):
    version = '7.1'
    url = 'https://www.ffmpeg.org/releases/ffmpeg-{version}.tar.xz'


recipe = FFMpegRecipeCompat()
