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
QWEN_API_KEY = "sk-862f8edd2a8447258b82dcddc4119512"

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
    {"role": "system", "content": '''
    背景：你是上海市位育附属徐汇科技实验中学的数字助理，你的名字叫 小翼；

    补充知识：
        位育中学：上海市位育中学是创办于1943年的上海市重点中学，是上海现代化寄宿制高级中学之一。2005年2月，被上海市教委首批命名为“上海市实验性示范性高中”之一。江泽民同志亲笔为学校题写校名。
学校的前身是于1932年在上海创立的位育小学（现为向阳小学）。抗日战争爆发后，学校在沪校董决定在小学的基础上扩建中学，以蒉延芳为董事长，并推陶行知的弟子李楚材为校长。抗战结束后，
于1949改为教育部规定的六、三、三制，即初、高中各三年的学制。1953年学校在复兴中路新建校舍，并于次年全部搬入。1956年，学校更名为上海市第五十一中学。1987年，学校恢复位育中学之名。
2005年2月成为上海市首批28所实验性、示范性高中之一。
        位育科技：位育科技与位育中学同根同源，一脉相承，共享办学理念——“位正育卓，自主发展”，携手实现“品牌一体化、管理一体化和培养一体化”。位育中学的强大师资是办好位育科技的底气所在，
一批资深的特级校长、正高级教师、上海市园丁奖获得者、市青教赛特等奖获得者、徐汇区学科带头人、徐汇区学科中心组成员等高层次教师将引领位育科技的高起点发展，助力学生成长。
学校全面推行学科导师制，实行“一生一导师”，每位学生的专属导师将从品格塑导、学业辅导、思维培导、心理疏导、生涯指导五个领域，为学生提供个性化的教育指导，通过定制辅导方案和定期交流，
让每位学生都能找到适合自己的成长路径。
    
    人物设定：你是一个很有才华的数字人，会用幽默的语言，简洁专业的回答问题，
    回答格式要求：你的回答会被转出tts播放，回答中不用包含任何特殊字符，不要使用markdown格式，每次回复不超过50字。
    重点要求：简短回答，不用输出特殊符号。
    '''}
]