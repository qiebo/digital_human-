# digital_human_code/main_gst.py

import time
import threading
import gc
import config

try:
    import audio_suppress  # noqa: F401
except Exception:
    pass

from baidu_api import login
from mstts import TextToSpeech
from answer import kimi_answer
import play

try:
    from tts_manager import TTSManager
except Exception:
    # TTSManager = None
    # --- 以下是新增的调试代码 ---
    print("--- 致命错误：无法导入 TTSManager 模块 ---")
    import traceback
    traceback.print_exc()
    print("-------------------------------------------")
    # --- 调试代码结束 ---
    TTSManager = None

from ui_gst import GStreamerUI
from vad_recorder import listen_for_utterance

def cleanup_memory():
    gc.collect()

def main():
    client = login()
    app = TextToSpeech(config.SPEECH_SERVICE_KEY)
    app.get_token()

    ui = GStreamerUI(width=config.DISPLAY_WIDTH, height=config.DISPLAY_HEIGHT)
    
    # 保持启动时显示第一帧的逻辑
    ui.show_video_first_frame(config.DIGITAL_HUMAN_VIDEO)
    
    awakened = False
    last_activity_time = time.time()
    messages = list(config.INITIAL_MESSAGES)

    tts_manager = TTSManager(azure_app=app, baidu_client=client, prefer=config.TTS_PREFER)

    try:
        while True:
            # 等待音频播放结束
            while play.is_playing():
                time.sleep(0.05)

            # --- 唤醒逻辑 (保持不变) ---
            if not awakened:
                # ... (此处省略未修改的唤醒监听代码)
                wav_bytes = listen_for_utterance()
                if not wav_bytes: continue
                try:
                    ask = client.asr(wav_bytes, 'wav', 16000, {'dev_pid': config.BAIDU_DEV_PID}).get('result', [None])[0]
                except Exception: ask = None
                if not ask: continue
                print("识别结果:", ask)
                ui.push_user(ask)
                norm = ''.join(ch for ch in ask.strip().lower() if ch not in " ，,。.!！?？、；;:：")
                if any(p in norm for p in config.WAKE_WORDS):
                    awakened = True
                    last_activity_time = time.time()
                    messages = list(config.INITIAL_MESSAGES)
                    greeting = config.GREETING_MESSAGE
                    ui.push_assistant(greeting)
                    
                    # 使用新的TTS流程播放欢迎语
                    audio_generator = tts_manager.stream_speak(greeting)
                    first_chunk = next(audio_generator, None)
                    if first_chunk:
                        ui.play_video(config.DIGITAL_HUMAN_VIDEO, loop=True)
                        play.play_audio_data(first_chunk)
                        for chunk in audio_generator:
                            play.play_audio_data(chunk)
                    
                    ui.stop_video_playback()
                    last_activity_time = time.time()
                continue
            
            # --- 对话逻辑 ---
            if time.time() - last_activity_time > config.IDLE_TIMEOUT:
                print("超时，返回待机状态")
                awakened = False
                ui.stop_video_playback()
                continue
            
            wav_bytes = listen_for_utterance()
            if not wav_bytes: continue
            
            try:
                ask = client.asr(wav_bytes, 'wav', 16000, {'dev_pid': config.BAIDU_DEV_PID}).get('result', [None])[0]
            except Exception: ask = None

            if not ask:
                ui.push_assistant("我没有听清，请再说一次吧！")
                last_activity_time = time.time()
                continue

            print("识别结果:", ask)
            ui.push_user(ask)
            last_activity_time = time.time()

            if ask.strip() in ("退下", "再见", "拜拜"):
                ui.push_assistant("再见")
                awakened = False
                ui.stop_video_playback()
                continue

            messages.append({"role":"user","content":ask})
            answer = kimi_answer(messages) or "我再想一想，请再说一次"
            messages.append({"role":"assistant","content":answer})
            

            # --- 核心改动：使用新的TTS流程播放回答 ---
            try:
                # 1. 获取音频生成器
                audio_generator = tts_manager.stream_speak(answer)
                
                # 2. 预先获取第一个音频块，这是消除延迟的关键
                #    程序会在这里等待，直到第一句语音合成完毕
                first_chunk = next(audio_generator, None)

                if first_chunk:
                    # 3. 当获取到第一块音频后，立刻开始播放视频和音频
                    ui.push_assistant(answer)
                    ui.play_video(config.DIGITAL_HUMAN_VIDEO, loop=True)
                    play.play_audio_data(first_chunk)
                    
                    # 4. 依次播放剩余的音频块
                    #    play.play_audio_data 是阻塞的，会自动一句接一句播放
                    for chunk in audio_generator:
                        play.play_audio_data(chunk)
            finally:
                    ui.stop_video_playback()
                    last_activity_time = time.time()
                    time.sleep(config.ASR_COOLDOWN)

            cleanup_memory()

    except KeyboardInterrupt:
        pass
    finally:
        ui.close()
        cleanup_memory()

if __name__ == "__main__":
    main()