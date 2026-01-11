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

        self.main_container = tk.Frame(root)
        self.main_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 左側：遊戲棋盤
        self.game_frame = tk.Frame(self.main_container)
        self.game_frame.pack(side=tk.LEFT, padx=10)

        self._init_grid_ui()  # 建立 10x10 棋盤按鈕

        # 右側：飛機資訊
        self.info_frame = tk.Frame(self.main_container, width=200)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(
            self.info_frame,
            text="本局敵機情報",
            font=("Arial", 11, "bold")
        ).pack(pady=5)

        self.preview_canvas = tk.Canvas(
            self.info_frame,
            width=150,
            height=400,
            bg="#F0F0F0"
        )
        self.preview_canvas.pack()

        self.ask_start_game()  # 啟動遊戲設定流程

def _init_grid_ui(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                btn = tk.Button(
                    self.game_frame,
                    width=4,
                    height=2,
                    bg=COLOR_DEFAULT,
                    command=lambda row=r, col=c: self.on_click(row, col)
                )
                btn.grid(row=r, column=c, padx=1, pady=1)
                self.buttons[r][c] = btn

def ask_start_game(self):
        num = simpledialog.askinteger(
            "遊戲設定",
            "請輸入飛機數量 (2 或 3):",
            minvalue=2,
            maxvalue=3
        )
        if num is None:
            return

        difficulty = simpledialog.askstring(
            "難度設定",
            "請輸入難度 (簡單/一般/困難):"
        )

        if difficulty == "一般":
            max_steps = 35
        elif difficulty == "困難":
            max_steps = 25
        else:
            max_steps = 50

        self.start_game(num, max_steps)

    def start_game(self, num_planes, max_steps):
        # 重置遊戲狀態
        self.max_steps = max_steps
        self.steps = 0
        self.total_heads = num_planes
        self.found_heads = 0
        self.planes.clear()
        self.bomb_available = 1
        self.game_over = False

        # 更新 UI
        self.lbl_steps.config(text=f"步數: 0 / 上限: {self.max_steps}")
        self.lbl_heads.config(text=f"剩餘機頭: {self.total_heads}")
        self.btn_bomb.config(text="使用炸彈 (1)", state=tk.NORMAL)
        self.preview_canvas.delete("all")

        # 清空棋盤
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.grid_data[r][c] = None
                self.buttons[r][c].config(bg=COLOR_DEFAULT, state=tk.NORMAL, text="")

        self.place_planes(num_planes)   # 放置飛機
        self.draw_plane_previews()      # 繪製預覽

 def generate_random_shape(self):
        shape = [(0, 0), (0, 1)]  # 機頭 + 第一節機身
        body_len = random.randint(2, 4)
        wing_len = random.randint(1, 3)

        for i in range(2, body_len + 1):
            shape.append((0, i))  # 機身延伸

        for i in range(1, wing_len + 1):
            shape.append((-i, 1))  # 左翅
            shape.append((i, 1))   # 右翅

        if random.choice([True, False]):
            shape.append((-1, body_len))
            shape.append((1, body_len))

        return shape

    def rotate_shape(self, shape, angle):
        rotated = []
        for x, y in shape:
            if angle == 90:
                rotated.append((-y, x))
            elif angle == 180:
                rotated.append((-x, -y))
            elif angle == 270:
                rotated.append((y, -x))
            else:
                rotated.append((x, y))
        return rotated

    def place_planes(self, count):
        placed = 0
        while placed < count:
            shape = self.rotate_shape(
                self.generate_random_shape(),
                random.choice([0, 90, 180, 270])
            )
            r = random.randint(0, GRID_SIZE - 1)
            c = random.randint(0, GRID_SIZE - 1)

            if self.is_valid_position(r, c, shape):
                self.add_plane_to_grid(r, c, shape)
                self.planes.append(shape)
                placed += 1

    def is_valid_position(self, r, c, shape):
        for dx, dy in shape:
            nr, nc = r + dy, c + dx
            if not (0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE):
                return False
            if self.grid_data[nr][nc] is not None:
                return False
        return True

    def add_plane_to_grid(self, r, c, shape):
        for i, (dx, dy) in enumerate(shape):
            nr, nc = r + dy, c + dx
            self.grid_data[nr][nc] = 'H' if i == 0 else 'B'
