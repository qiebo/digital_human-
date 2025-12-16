import os
# 在 pyaudio 初始化前设置环境变量，避免 ALSA/JACK 警告
# os.environ.setdefault("SDL_AUDIODRIVER", "alsa")
# os.environ.setdefault("JACK_NO_START_SERVER", "1")
# os.environ.setdefault("AUDIODEV", "hw:0,0")  # 强制使用硬件设备

# 解决 /tmp 目录权限问题
os.environ.setdefault("TMPDIR", os.path.expanduser("~/.tmp"))
os.environ.setdefault("TEMP", os.path.expanduser("~/.tmp"))

import pyaudio
import numpy as np

from audio_suppress import suppress_stderr_alsa

def listen_for_utterance(
    threshold=2500,  # 降低启动阈值，更灵敏
    sample_rate=16000,
    channels=1,
    chunk_size=2048,
    max_record_seconds=12,
    start_trigger_ms=150,  # 缩短启动时间
    end_silence_ms=500,    # 缩短静音等待时间，提高响应性
    device_index=None,
):
    # 强化 ALSA 库警告输出抑制
    with suppress_stderr_alsa():
        pa = pyaudio.PyAudio()
    
    try:
        # 如果没有指定设备，强制使用默认输入设备
        if device_index is None:
            try:
                # 尝试获取默认输入设备
                device_index = pa.get_default_input_device_info()['index']
            except:
                device_index = 0  # 兜底使用设备0
        
        stream = pa.open(format=pyaudio.paInt16,
                            channels=channels,
                            rate=sample_rate,
                            input=True,
                            input_device_index=device_index,
                            frames_per_buffer=chunk_size)
    except Exception as e:
        print(f"麦克风初始化失败: {e}")
        pa.terminate()
        return None

    print("等待录音")
    started = False
    frames = []
    speech_hit = 0
    silence_hit = 0

    max_chunks = int(max_record_seconds * sample_rate / chunk_size)
    start_need = max(1, int((start_trigger_ms/1000)*sample_rate/chunk_size))
    end_need = max(1, int((end_silence_ms/1000)*sample_rate/chunk_size))

    # 动态阈值调整
    recent_peaks = []
    background_level = threshold * 0.3

    try:
        for chunk_idx in range(max_chunks):
            data = stream.read(chunk_size, exception_on_overflow=False)
            buf = np.frombuffer(data, dtype=np.int16)
            peak = int(np.max(np.abs(buf)))
            rms  = int(np.sqrt(np.mean(buf.astype(np.float32)**2)))
            
            # 维护最近的音量水平用于动态调整
            recent_peaks.append(peak)
            if len(recent_peaks) > 20:  # 只保留最近20个chunk
                recent_peaks.pop(0)
                avg_peak = sum(recent_peaks) / len(recent_peaks)
                # 动态调整背景噪声水平
                if not started and avg_peak < threshold * 0.8:
                    background_level = max(background_level * 0.95, avg_peak * 1.2)

            # 使用动态阈值判断
            effective_threshold = max(threshold, background_level * 2)

            if not started:
                if peak > effective_threshold or rms > int(effective_threshold * 0.6):
                    speech_hit += 1
                else:
                    speech_hit = max(0, speech_hit - 1)  # 渐进式衰减而非直接清零
                    
                if speech_hit >= start_need:
                    print("开始录音")
                    started = True
                    frames.clear()
                    frames.append(data)
                    silence_hit = 0
            else:
                frames.append(data)
                # 更严格的静音判断，提高结束响应性
                silence_threshold_peak = int(effective_threshold * 0.4)  # 更低的静音阈值
                silence_threshold_rms = int(effective_threshold * 0.25)
                
                if peak < silence_threshold_peak and rms < silence_threshold_rms:
                    silence_hit += 1
                else:
                    silence_hit = 0
                    
                if silence_hit >= end_need:
                    print("录音结束")
                    break
                    
                # 额外的快速结束条件：连续极低音量
                if silence_hit >= max(2, end_need // 2) and peak < background_level:
                    print("录音结束（快速检测）")
                    break
        else:
            if started:
                print("录音结束（超时）")
            else:
                print("未检测到语音")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

    if not started or not frames:
        return None

    import io, wave
    bio = io.BytesIO()
    wf = wave.open(bio, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(2)
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return bio.getvalue()
