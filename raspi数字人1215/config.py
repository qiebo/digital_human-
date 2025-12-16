# config.py - 针对树莓派优化的配置

# 显示配置
DISPLAY_WIDTH = 1440
DISPLAY_HEIGHT = 2560
FPS_LIMIT = 15

# 音频配置
CHUNK_SIZE = 2048
SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5
THRESHOLD = 2500  # 降低阈值，提高灵敏度
RECORDING_THRESHOLD = 2500  # 保持一致

# 文件路径配置
EMOJI_DIR = "emoji"
FONT_PATH = "simhei.ttf"

# 数字人动画文件
DIGITAL_HUMAN_VIDEO = "emoji/emoji.mp4"

# 对话配置
WAKE_WORDS = ("你好小翼", "你好小易", "你好小姨", "你好小一") # 你可以添加更多唤醒词，用逗号隔开
GREETING_MESSAGE = "你好，我是你的数字助理，有什么可以帮您？"

# API配置
API_TIMEOUT = 15
BAIDU_APP_ID = "26390099"
BAIDU_API_KEY = "ukIZ7YiotGyS6ExZK5mjPmti"
BAIDU_SECRET_KEY = "hacGAH3txw4gOlNWXmjaQoMXhlbqXS5Q"

# Microsoft Azure Speech Service
SPEECH_SERVICE_KEY = "41a66945f1814cd2a5874cdf8d8c55a0"
SPEECH_SERVICE_REGION = "eastus"
TTS_VOICE = "zh-CN-XiaoyiNeural"

# Wenxin
WENXIN_APPID = "55229788"
WENXIN_API_KEY = "KQ2vOFt4SBojabqTjiah35lm"
WENXIN_SECRET_KEY = "NxC8oDRBVvjDe5tJjhsYQDnHfPa8u3Yw"

# Kimi
MOONSHOT_API_KEY = "sk-fqpae6PNqOVMUWZTKop3e3b4pp2EEk3ctOz7yr6wWyL5AjCb"

# Qwen
# QWEN_API_KEY = "sk-862f8edd2a8447258b82dcddc4119512"
QWEN_API_KEY = "sk-81e2b1df6f0b4bfba39ad617a93cef3d" #远播千问api key

# Main settings
IDLE_TIMEOUT = 30
ASR_COOLDOWN = 0.6
TTS_PREFER = "azure"
BAIDU_DEV_PID = "1537"

# 性能优化配置
FRAME_SKIP = 2
CACHE_SIZE = 5
UPDATE_INTERVAL = 0.05  # 50ms
MEMORY_CLEANUP_INTERVAL = 5  # 每5次循环清理一次内存
FRAME_QUEUE_SIZE = 5
WINDOW_NAME = "Digital Human"

# 音频优化配置
PYGAME_BUFFER_SIZE = 2048  # 增大缓冲区，避免播放被截断
MAX_SILENCE_DURATION = 0.5  # 缩短静音时长，提高响应性
VOLUME_LOG_INTERVAL = 10  # 每10个chunk记录一次音量

# GUI优化配置
TEXT_MAX_LENGTH = 50
SINGLE_LINE_DISPLAY = True

# 对话配置
INITIAL_MESSAGES = [
    {"role": "system", "content": "你是小翼，一个很有才华的数字人，请用幽默的语言，简洁专业的回答问题，你的回答会被转出tts播放，回答中不用包含任何特殊字符，不要使用markdown格式，每次回复不超过50字。"}
]