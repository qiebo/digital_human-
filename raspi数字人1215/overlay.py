# digital_human_code/overlay.py

from collections import deque
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time
import os
from typing import List, Tuple

class ChatOverlay:
    def __init__(self, width=800, height=600, font_path=None):
        self.width = width
        self.height = height
        self.font_path = font_path or os.path.join(os.path.dirname(__file__), "simhei.ttf")
        
        self.font_main = ImageFont.truetype(self.font_path, 48)
        self.font_ts = ImageFont.truetype(self.font_path, 28)
        
        self.messages = deque(maxlen=3)

        self._cache_img = None
        self._cache_sign = None

        self.margin = 40
        self.row_gap = 20
        self.pad_x = 30
        self.pad_y = 25
        self.max_ratio = 0.7
        self.radius = 30

        self.user_bg = (236, 236, 236, 220)
        self.bot_bg  = (94, 193, 94, 220)
        self.user_fg = (0, 0, 0, 255)
        self.bot_fg  = (255, 255, 255, 255)
        self.ts_fg   = (90, 90, 90, 255)

    def push(self, role, text, ts=None):
        ts = ts or time.strftime("%H:%M:%S")
        self.messages.append((role, str(text), ts))
        self._cache_sign = None

    def _measure_text(self, draw: ImageDraw.ImageDraw, text: str, font) -> Tuple[int, int]:
        try:
            l, t, r, b = draw.textbbox((0, 0), text, font=font)
            return (max(0, r - l), max(0, b - t))
        except Exception:
            try:
                l, t, r, b = font.getbbox(text)
                return (max(0, r - l), max(0, b - t))
            except Exception:
                return (0, 0)

    # --- 关键修复：恢复适合中文的“逐字换行”逻辑 ---
    def _text_wrap(self, draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> List[str]:
        """
        逐字测量宽度进行换行，确保能正确处理中文、英文和混合文本。
        """
        lines = []
        current_line = ""
        
        for char in text:
            # 处理显式换行符
            if char == '\n':
                lines.append(current_line)
                current_line = ""
                continue
            
            # 测量添加新字符后的行宽
            test_line = current_line + char
            w, _ = self._measure_text(draw, test_line, font)
            
            # 如果宽度超出限制，则将当前行存入列表，并用新字符开始新的一行
            if w > max_w:
                lines.append(current_line)
                current_line = char
            # 否则，将新字符添加到当前行
            else:
                current_line = test_line
        
        # 将最后一行添加到列表中
        if current_line:
            lines.append(current_line)
            
        # 如果文本为空，确保返回一个空行列表以避免错误
        if not lines:
            lines = [""]
            
        return lines

    def _bubble_dims(self, draw, text: str) -> Tuple[int, int, List[str]]:
        max_w = int(self.width * self.max_ratio)
        content_max_w = max_w - 2 * self.pad_x
        
        lines = self._text_wrap(draw, text, self.font_main, content_max_w)
        
        actual_max_line_w = 0
        for line in lines:
            line_w, _ = self._measure_text(draw, line, self.font_main)
            actual_max_line_w = max(actual_max_line_w, line_w)
        
        bubble_w = actual_max_line_w + 2 * self.pad_x
        bubble_w = min(bubble_w, max_w)

        line_h = self.font_main.getbbox("A")[3] - self.font_main.getbbox("A")[1] + 15
        content_h = line_h * len(lines)
        bubble_h = content_h + 2 * self.pad_y + 20

        return int(bubble_w), int(bubble_h), lines

    def _rounded_rect(self, draw, xy, r, fill):
        draw.rounded_rectangle(xy, radius=r, fill=fill)

    def _render_cache(self):
        sign = (tuple(self.messages), self.width, self.height)
        if sign == self._cache_sign and self._cache_img is not None:
            return self._cache_img

        from PIL import Image
        canvas = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        left_edge = self.margin
        right_edge = self.width - self.margin
        y_cursor = self.height - self.margin

        for role, text, ts in reversed(self.messages):
            bw, bh, lines = self._bubble_dims(draw, text)

            y1 = y_cursor - bh
            y2 = y_cursor
            if role == "assistant":
                x1 = left_edge
                x2 = left_edge + bw
                bg, fg = self.bot_bg, self.bot_fg
            else:
                x2 = right_edge
                x1 = right_edge - bw
                bg, fg = self.user_bg, self.user_fg

            self._rounded_rect(draw, (x1, y1, x2, y2), self.radius, bg)

            y_text = y1 + self.pad_y
            line_h = self.font_main.getbbox("A")[3] - self.font_main.getbbox("A")[1] + 15
            for ln in lines:
                draw.text((x1 + self.pad_x, y_text), ln, font=self.font_main, fill=fg)
                y_text += line_h

            ts_w, ts_h = self._measure_text(draw, ts, self.font_ts)
            draw.text((x2 - self.pad_x - ts_w, y2 - self.pad_y - ts_h), ts, font=self.font_ts, fill=self.ts_fg)

            y_cursor = y1 - self.row_gap

        arr = np.array(canvas, dtype=np.uint8)
        self._cache_img = arr
        self._cache_sign = sign
        return arr

    def get_overlay_rgba(self, width=None, height=None):
        if width and height and (self.width != width or self.height != height):
            self.width, self.height = int(width), int(height)
            self._cache_sign = None
        return self._render_cache()