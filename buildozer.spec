[app]
title = DivaTouch
package.name = divatouch
package.domain = org.divatouch
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3,kivy==2.3.0,pyjnius,android

orientation = landscape
fullscreen = 1

android.permissions = READ_EXTERNAL_STORAGE,READ_MEDIA_VIDEO
android.accept_sdk_license = True

android.api = 33
android.minapi = 21
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1 
