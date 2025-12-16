# digital_human_code/ui_gst.py

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GObject', '2.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject, Gtk, GLib, Gdk
import numpy as np
import threading
import time
import cairo

from overlay import ChatOverlay

# 初始化GStreamer和GTK
Gst.init(None)

class ChatBubbleWidget(Gtk.DrawingArea):
    def __init__(self, chat_overlay_instance):
        super().__init__()
        self.chat_overlay = chat_overlay_instance
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.connect("draw", self.on_draw)

    def on_draw(self, widget, cr):
        w = self.get_allocated_width()
        h = self.get_allocated_height()
        rgba_data = self.chat_overlay.get_overlay_rgba(width=w, height=h)
        if rgba_data is None or rgba_data.shape[0] == 0 or rgba_data.shape[1] == 0:
            return False
        surface = cairo.ImageSurface.create_for_data(
            rgba_data, cairo.FORMAT_ARGB32, w, h
        )
        cr.set_source_surface(surface, 0, 0)
        cr.paint()
        return False

    def refresh(self):
        self.queue_draw()

class GStreamerUI:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.overlay = ChatOverlay(width=self.width, height=self.height)

        self.pipeline = None
        self._lock = threading.Lock()
        self._current_source = None
        self._is_video_playing = False
        
        self.window = None
        self.video_container = None
        self.chat_widget = None

        def run_ui():
            Gtk.init(None)
            self.window = Gtk.Window()
            self.window.connect("destroy", Gtk.main_quit)
            main_overlay = Gtk.Overlay()
            self.window.add(main_overlay)
            self.video_container = Gtk.Box()
            main_overlay.add(self.video_container)
            self.chat_widget = ChatBubbleWidget(self.overlay)
            main_overlay.add_overlay(self.chat_widget)
            self.window.show_all()
            self.window.fullscreen()
            Gtk.main()

        self.ui_thread = threading.Thread(target=run_ui, daemon=True)
        self.ui_thread.start()
        time.sleep(1) 

    def _build_pipeline(self, src_desc):
        # --- 终极优化：加入videoscale进行降维处理 ---
        # 目标分辨率，对于竖屏设为 720x1280
        TARGET_WIDTH = 720
        TARGET_HEIGHT = 1280
        
        desc = (
            f"{src_desc} ! qtdemux ! h264parse ! v4l2h264dec ! "
            # 增加一个队列缓冲
            "queue ! "
            # 关键：在这里进行视频缩放
            "videoscale ! "
            # 指定缩放后的尺寸，capsfilter用于“强制”设定流的属性
            f"video/x-raw,width={TARGET_WIDTH},height={TARGET_HEIGHT} ! "
            # 再增加一个队列，确保后续流程顺畅
            "queue ! "
            # 将缩放后的、小尺寸的视频帧送入GTK
            "gtksink name=videosink"
        )
        
        pipeline = Gst.parse_launch(desc)
        bus = pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message::error", self._on_error)
        bus.connect("message::eos", self._on_eos)
        return pipeline

    def _on_error(self, bus, msg):
        err, debug = msg.parse_error()
        print("GStreamer error:", err, debug)
        if 'v4l2h264dec' in str(err):
            print("\n错误提示：找不到硬件解码器'v4l2h264dec'。")
            print("请确认您的系统已安装GStreamer的V4L2插件。")
            print("在树莓派OS/Debian上，请尝试运行：sudo apt-get install gstreamer1.0-plugins-good\n")
        
        with self._lock:
            if self.pipeline:
                self.pipeline.set_state(Gst.State.NULL)
                self.pipeline = None
                self._is_video_playing = False

    def _on_eos(self, bus, msg):
        with self._lock:
            if self.pipeline and self._is_video_playing:
                self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)

    def _set_pipeline(self, pipeline):
        with self._lock:
            old_pipeline = self.pipeline
            
            videosink = pipeline.get_by_name("videosink")
            # 确保禁用同步，让视频尽快渲染
            videosink.set_property("sync", False)
            videosink.set_property("force-aspect-ratio", False)
            widget = videosink.get_property("widget")

            if old_pipeline:
                old_sink = old_pipeline.get_by_name("videosink")
                if old_sink:
                    old_widget = old_sink.get_property("widget")
                    if old_widget and old_widget.get_parent():
                        GLib.idle_add(self.video_container.remove, old_widget)
            
            GLib.idle_add(self.video_container.pack_start, widget, True, True, 0)
            GLib.idle_add(widget.show)
            
            pipeline.set_state(Gst.State.PLAYING)
            self.pipeline = pipeline

            if old_pipeline:
                old_pipeline.set_state(Gst.State.NULL)

    def show_video_first_frame(self, video_path):
        with self._lock:
            if self._current_source == f"video_frame:{video_path}": return
        src = f'filesrc location="{video_path}"'
        pl = self._build_pipeline(src)
        self._set_pipeline(pl)
        pl.set_state(Gst.State.PAUSED)
        self._is_video_playing = False
        self._current_source = f"video_frame:{video_path}"

    def play_video(self, path, loop=True):
        with self._lock:
            if self.pipeline and self._current_source and path in self._current_source:
                self.pipeline.set_state(Gst.State.PLAYING)
                self._is_video_playing = loop
                self._current_source = f"video:{path}"
                return
        src = f'filesrc location="{path}"'
        pl = self._build_pipeline(src)
        self._set_pipeline(pl)
        self._current_source = f"video:{path}"
        self._is_video_playing = loop

    def stop_video_playback(self):
        with self._lock:
            if self.pipeline:
                self.pipeline.set_state(Gst.State.PAUSED)
                self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)
                if self._current_source and self._current_source.startswith("video:"):
                    video_path = self._current_source.replace("video:", "")
                    self._current_source = f"video_frame:{video_path}"
            self._is_video_playing = False

    def push_user(self, text):
        self.overlay.push("user", text)
        if self.chat_widget:
            GLib.idle_add(self.chat_widget.refresh)

    def push_assistant(self, text):
        self.overlay.push("assistant", text)
        if self.chat_widget:
            GLib.idle_add(self.chat_widget.refresh)

    def close(self):
        self.stop()
        if hasattr(self, 'window'):
            GLib.idle_add(Gtk.main_quit)
        if self.ui_thread.is_alive():
            self.ui_thread.join(timeout=1.0)
            
    def stop(self):
        with self._lock:
            if self.pipeline:
                self.pipeline.set_state(Gst.State.NULL)
                self.pipeline = None
                self._current_source = None
                self._is_video_playing = False