# DivaTouch

A simple Project Diva-style touch overlay: pick an MP4, it plays fullscreen,
and four buttons (Sankaku/Shikaku/Batsu/Maru) sit on top. Press or hold a
button and it swaps to its glowing "ON" image; release and it goes back to
"OFF".

## Build the APK with GitHub Actions (no local Android setup needed)

1. Create a new **public or private GitHub repo** and push this entire
   folder to it (the `.github/workflows/build.yml` file must stay at that
   exact path — don't rename or move it).

   ```bash
   cd divatouch
   git init
   git add .
   git commit -m "Initial DivaTouch app"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

2. Go to your repo on GitHub → the **Actions** tab. You should see a
   "Build APK" workflow run start automatically (it also triggers on every
   push to `main`, or you can click **Run workflow** to trigger it by hand).

3. Wait for the run to finish (first build takes 15–25 minutes since it
   downloads and compiles the Android SDK/NDK — later builds are faster
   thanks to caching).

4. Open the finished run → scroll to **Artifacts** → download
   `DivaTouch-debug-apk`. Unzip it to get `divatouch-0.1-arm64-v8a_armeabi-v7a-debug.apk`
   (exact filename may vary slightly).

5. Copy the `.apk` to your Android device and install it (you'll need to
   allow "install unknown apps" for whichever app you use to open the file).

## Using the app

- Tap **Load Video** → browse to an `.mp4` file on your device → **Select**.
- Tap **Play/Pause** to start/stop playback.
- Press and hold any of the four buttons — it lights up (ON image) while
  held, and reverts (OFF image) when released.

## Known limitations / things you may want to tweak

- **Video playback backend**: this uses Kivy's `VideoPlayer` with the
  `ffpyplayer` provider (set in `buildozer.spec`). It's the most reliable
  pure-Python option for Android, but very high-resolution video can be
  demanding on lower-end phones. If you hit performance issues, try
  lower-resolution/bitrate MP4s.
- **File picker**: uses Kivy's built-in file chooser rather than Android's
  native picker, so on newer Android versions (scoped storage) you may
  need to browse to `/storage/emulated/0/...` manually to find your videos.
  A more robust picker (Android's `Intent.ACTION_OPEN_DOCUMENT` via
  `pyjnius`) is possible as a follow-up if this becomes annoying.
- **Button layout**: positions are set with `pos_hint` in `main.py` in the
  `button_defs` list inside `DivaRoot.__init__`. Tweak the `x`/`y` fractions
  there to nudge button placement, and `size_hint` to resize them.
- **No scoring/timing logic yet**: this is just a video player with
  responsive hold-buttons overlaid — no note charts, hit judgment, or
  scoring. That would be a separate feature to add on top of this base.

## Project structure

```
divatouch/
├── main.py                  # App logic (Kivy)
├── buildozer.spec           # Android build configuration
├── assets/                  # Your 8 button PNGs (ON/OFF x 4 buttons)
└── .github/workflows/build.yml   # CI job that builds the APK
```
