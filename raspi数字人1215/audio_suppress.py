# digital_human_code/audio_suppress.py

import os
import sys
from contextlib import contextmanager

@contextmanager
def suppress_stderr_alsa():
    """
    一个上下文管理器，用于临时抑制ALSA和其他底层库的stderr输出。
    """
    original_stderr_fd = sys.stderr.fileno()
    saved_stderr = os.dup(original_stderr_fd)
    try:
        # 将stderr重定向到/dev/null (一个丢弃所有写入数据的特殊文件)
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull_fd, original_stderr_fd)
        os.close(devnull_fd)
        yield
    finally:
        # 恢复原始的stderr
        os.dup2(saved_stderr, original_stderr_fd)
        os.close(saved_stderr)