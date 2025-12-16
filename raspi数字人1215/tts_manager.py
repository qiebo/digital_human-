# digital_human_code/tts_manager.py (Final Production Version)

import os
import re
import threading
import queue
import time
import hashlib
from pathlib import Path

import play
import config

_SENTENCE_SPLIT = re.compile(r"[。！？!?；;…\n]")

def _hash_key(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

class TTSManager:
    def __init__(self, azure_app=None, baidu_client=None,
                 prefer="azure", cache_dir=None):
        self.azure_app = azure_app
        self.baidu_client = baidu_client
        self.prefer = prefer
        self.cache_dir = Path(cache_dir or (Path.home()/".cache/digital_hum/tts"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _sentences(self, text: str):
        text = (text or "").strip()
        if not text: return []
        raw = _SENTENCE_SPLIT.split(text)
        sents = [s.strip() for s in raw if s.strip()]
        if not sents and text: sents = [text]
        return sents[:12]

    def _cache_path(self, provider: str, voice: str, text: str):
        key = _hash_key(f"{provider}|{voice}|{text}")
        return self.cache_dir/f"{key}.wav"

    def _synthesize_one(self, text: str, voice, speed):
        # 检查缓存时，会检查所有可能的provider
        # 优先检查首选provider的缓存
        preferred_cache = self._cache_path(self.prefer, voice, text)
        if preferred_cache.exists():
            return preferred_cache.read_bytes()
        
        # 检查备选provider的缓存
        backup_provider = "baidu" if self.prefer == "azure" else "azure"
        backup_cache = self._cache_path(backup_provider, voice, text)
        if backup_cache.exists():
            return backup_cache.read_bytes()

        # 如果缓存未命中，则进行合成
        wav, actual_provider = self._try_synthesize_with_providers(text, voice, speed)
        
        # 使用实际生成音频的provider来创建缓存，防止“缓存污染”
        if wav and actual_provider:
            try:
                correct_cache_path = self._cache_path(actual_provider, voice, text)
                correct_cache_path.write_bytes(wav)
            except Exception as e:
                print(f"Error writing to cache: {e}")
        return wav

    def _try_synthesize_with_providers(self, text, voice, speed):
        # 定义尝试顺序：首选服务在前，备选服务在后
        order = [self.prefer, "baidu" if self.prefer == "azure" else "azure"]
        for prov in order:
            try:
                if prov == "azure" and self.azure_app:
                    wav = self.azure_app.save_audio(text, voice_name=voice)
                    if wav:
                        print("Synthesis successful with Azure.")
                        return wav, "azure"  # 返回音频和实际的provider
                elif prov == "baidu" and self.baidu_client:
                    from baidu_api import run_tts
                    wav_bytes = run_tts(self.baidu_client, text)
                    if wav_bytes:
                        print("Synthesis successful with Baidu fallback.")
                        return wav_bytes, "baidu" # 返回音频和实际的provider
            except Exception as e:
                print(f"Synthesis with {prov} failed: {e}")
                continue
        return b"", None # 如果全部失败

    def stream_speak(self, text: str, voice=None, speed="0%"):
        if voice is None:
            voice = config.TTS_VOICE
        sents = self._sentences(text)
        if not sents:
            return

        audio_queue = queue.Queue()

        def synthesize_sentences_in_background():
            for sent in sents:
                wav_data = self._synthesize_one(sent, voice, speed)
                if wav_data:
                    audio_queue.put(wav_data)
            audio_queue.put(None)

        synthesis_thread = threading.Thread(target=synthesize_sentences_in_background, daemon=True)
        synthesis_thread.start()

        while True:
            wav_chunk = audio_queue.get()
            if wav_chunk is None:
                break
            yield wav_chunk