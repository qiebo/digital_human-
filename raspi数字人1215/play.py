import os


import pygame
import threading
import time
from io import BytesIO
import config
from audio_suppress import suppress_stderr_alsa

class AudioPlayer:
    def __init__(self):
        self.is_playing = False
        self.mixer_initialized = False
        self.play_thread = None
        self._play_lock = threading.Lock()  # 添加播放锁，确保同步
        
    def _init_mixer(self):
        """延迟初始化pygame mixer"""
        if not self.mixer_initialized:
            try:
                with suppress_stderr_alsa():
                    pygame.mixer.pre_init(
                        frequency=22050, 
                        size=-16, 
                        channels=2, 
                        buffer=config.PYGAME_BUFFER_SIZE
                    )
                    pygame.mixer.init()
                    self.mixer_initialized = True
                    print("音频播放器初始化成功")
            except Exception as e:
                print(f"初始化音频播放器失败: {e}")
                return False
        return True

    def play_audio_data(self, audio_data):
        """播放音频数据，确保同步播放"""
        with self._play_lock:  # 使用锁确保播放同步
            if not self._init_mixer():
                return False
                
            try:
                # 等待当前音频完全播放完毕
                self._wait_for_completion()
                
                # 使用BytesIO进行内存流播放
                audio_stream = BytesIO(audio_data)
                
                # 直接在当前线程播放，避免多线程同步问题
                
                pygame.mixer.music.load(audio_stream)
                pygame.mixer.music.play()
                self.is_playing = True
                
                # 在当前线程等待播放完成
                while pygame.mixer.music.get_busy() and self.is_playing:
                    time.sleep(0.01)  # 10ms检查一次
                    
                self.is_playing = False
                return True
                
            except Exception as e:
                print(f"播放音频失败: {e}")
                self.is_playing = False
                return False

    def _wait_for_completion(self):
        """等待当前音频播放完成"""
        if not self.mixer_initialized:
            return
        # 使用 mixer busy 状态更可靠
        while pygame.mixer.music.get_busy():
            time.sleep(0.01)

    def _force_stop(self):
        """强制停止当前播放"""
        self.is_playing = False
        
        if self.mixer_initialized:
            try:
                pygame.mixer.music.stop()
            except:
                pass
        
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)  # 增加等待时间

    def play_file(self, filename):
        """播放音频文件"""
        with self._play_lock:
            if not self._init_mixer():
                return False
                
            try:
                # 等待当前音频完全播放完毕
                self._wait_for_completion()
                
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                self.is_playing = True
                
                # 启动监控线程
                self.play_thread = threading.Thread(target=self._monitor_playback)
                self.play_thread.start()
                return True
                
            except Exception as e:
                print(f"播放文件失败: {e}")
                return False

    def _monitor_playback(self):
        """监控播放状态"""
        while pygame.mixer.music.get_busy() and self.is_playing:
            time.sleep(0.01)
        self.is_playing = False

    def stop(self):
        """停止播放（对外接口）"""
        with self._play_lock:
            self._force_stop()

    def is_playing_audio(self):
        """检查是否正在播放"""
        return self.is_playing and pygame.mixer.music.get_busy() if self.mixer_initialized else False

    def cleanup(self):
        """清理资源"""
        with self._play_lock:
            self._force_stop()
            if self.mixer_initialized:
                try:
                    
                    pygame.mixer.quit()
                except:
                    pass
                self.mixer_initialized = False

# 全局播放器实例
player = AudioPlayer()

def play_audio_data(audio_data):
    """播放音频数据"""
    return player.play_audio_data(audio_data)

def play_file(filename):
    """播放音频文件"""
    return player.play_file(filename)

def stop_audio():
    """停止播放"""
    player.stop()

def is_playing():
    """检查是否正在播放"""
    return player.is_playing_audio()

def cleanup():
    """清理资源"""
    player.cleanup()