import tkinter as tk                     # 建立視窗與按鈕
from tkinter import messagebox, simpledialog  # 提示視窗與輸入視窗
import random                            # 產生隨機飛機形狀與位置

GRID_SIZE = 10           # 棋盤大小為 10x10
CELL_SIZE = 40           # 主棋盤格子大小
PREVIEW_CELL_SIZE = 20   # 右側預覽飛機格子大小

COLOR_DEFAULT = "#DDDDDD"   # 未翻開格子
COLOR_MISS = "white"        # 點到空格
COLOR_BODY = "#5555FF"      # 飛機機身
COLOR_HEAD = "#FF4444"      # 飛機機頭
COLOR_TEXT = "black"
