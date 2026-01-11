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

class PlaneGame:
    def __init__(self, root):
        self.root = root
        self.root.title("尋找機頭 - 隨機變體版")
        self.grid_data = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        # None：空格，'B'：機身，'H'：機頭

        self.buttons = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        # 對應每一格的 Button 物件

        self.planes = []            # 存放每一台飛機的形狀（給右側預覽）
        self.total_heads = 0        # 本局飛機數量
        self.found_heads = 0        # 已找到的機頭數
        self.steps = 0              # 玩家目前步數
        self.max_steps = None       # 步數上限
        self.game_over = False      # 遊戲是否結束
        self.bomb_available = 1     # 炸彈只能用一次
