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

self.top_frame = tk.Frame(root, pady=10)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.lbl_steps = tk.Label(self.top_frame, text="步數: 0", font=("Arial", 12))
        self.lbl_steps.pack(side=tk.LEFT, padx=20)

        self.lbl_heads = tk.Label(
            self.top_frame,
            text="剩餘機頭: 0",
            font=("Arial", 12, "bold"),
            fg="red"
        )
        self.lbl_heads.pack(side=tk.LEFT, padx=20)

        self.btn_restart = tk.Button(
            self.top_frame,
            text="重新開始",
            command=self.ask_start_game
        )
        self.btn_restart.pack(side=tk.RIGHT, padx=20)

        self.btn_bomb = tk.Button(
            self.top_frame,
            text="使用炸彈 (1)",
            command=self.use_bomb
        )
        self.btn_bomb.pack(side=tk.RIGHT, padx=20)
