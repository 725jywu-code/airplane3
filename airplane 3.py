# ============================================================
# 【第 1 段】匯入模組
# 目的：載入 GUI、對話框與隨機工具
# ============================================================
import tkinter as tk                     # 建立視窗與按鈕
from tkinter import messagebox, simpledialog  # 提示視窗與輸入視窗
import random                            # 產生隨機飛機形狀與位置


# ============================================================
# 【第 2 段】遊戲基本參數設定
# 目的：統一管理棋盤與格子大小
# ============================================================
GRID_SIZE = 10           # 棋盤大小為 10x10
CELL_SIZE = 40           # 主棋盤格子大小
PREVIEW_CELL_SIZE = 20   # 右側預覽飛機格子大小


# ============================================================
# 【第 3 段】顏色與視覺設定
# 目的：讓不同狀態有明確顏色區分
# ============================================================
COLOR_DEFAULT = "#DDDDDD"   # 未翻開格子
COLOR_MISS = "white"        # 點到空格
COLOR_BODY = "#5555FF"      # 飛機機身
COLOR_HEAD = "#FF4444"      # 飛機機頭
COLOR_TEXT = "black"


# ============================================================
# 【第 4 段】PlaneGame 類別（主遊戲架構）
# 目的：將整個遊戲封裝成一個物件
# ============================================================
class PlaneGame:
    def __init__(self, root):
        self.root = root
        self.root.title("尋找機頭 - 隨機變體版")

        # ====================================================
        # 【第 5 段】遊戲資料結構與狀態變數
        # 目的：記錄遊戲進度與棋盤內容
        # ====================================================
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


        # ====================================================
        # 【第 6 段】上方資訊列（步數、剩餘機頭、操作按鈕）
        # ====================================================
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


        # ====================================================
        # 【第 7 段】主畫面與右側飛機預覽區
        # ====================================================
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


    # ========================================================
    # 【第 8 段】建立棋盤按鈕與點擊事件
    # ========================================================
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


    # ========================================================
    # 【第 9 段】遊戲設定與初始化流程
    # ========================================================
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
        self.max_steps = max_steps
        self.steps = 0
        self.total_heads = num_planes
        self.found_heads = 0
        self.planes.clear()
        self.bomb_available = 1
        self.game_over = False
        
        self.is_bombing = False 
        self.lbl_steps.config(text=f"步數: 0 / 上限: {self.max_steps}")
        self.lbl_heads.config(text=f"剩餘機頭: {self.total_heads}")
    
        self.btn_bomb.config(text="使用炸彈 (1)", state=tk.NORMAL, bg="SystemButtonFace", relief="raised")
        
        self.preview_canvas.delete("all")

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.grid_data[r][c] = None
                self.buttons[r][c].config(bg=COLOR_DEFAULT, state=tk.NORMAL, text="", relief="raised")

        self.place_planes(num_planes)   # 放置飛機
        self.draw_plane_previews()      # 繪製預覽

    # ========================================================
    # 【第 10 段】飛機生成、旋轉與放置演算法
    # ========================================================
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


    # ========================================================
    # 【第 11 段】點擊翻格、步數計算與勝負判定
    # ========================================================
    def on_click(self, r, c):
        if self.game_over:
            return

        if self.is_bombing:
            self.execute_bomb_at(r, c)
            return

        if self.buttons[r][c]["state"] == tk.DISABLED:
            return

        self.steps += 1
        self.lbl_steps.config(text=f"步數: {self.steps} / 上限: {self.max_steps}")

        if self.steps > self.max_steps:
            self.game_over = True
            messagebox.showinfo("遊戲失敗", "超過最大步數")
            return

        self.reveal_cell(r, c)

    def reveal_cell(self, r, c):
        btn = self.buttons[r][c]
        if btn["state"] == tk.DISABLED:
            return

        cell = self.grid_data[r][c]
        if cell is None:
            btn.config(bg=COLOR_MISS)
        elif cell == 'B':
            btn.config(bg=COLOR_BODY)
        elif cell == 'H':
            btn.config(bg=COLOR_HEAD, text="X")
            self.found_heads += 1
            self.lbl_heads.config(
                text=f"剩餘機頭: {self.total_heads - self.found_heads}"
            )
            if self.found_heads == self.total_heads:
                messagebox.showinfo("勝利", "你找到了所有飛機！")
                self.game_over = True

        btn.config(state=tk.DISABLED)


    # ========================================================
    # 【第 12 段】飛機預覽繪製與炸彈玩法
    # ========================================================
    def draw_plane_previews(self):
        """繪製右側的飛機預覽 (修正負座標導致的重疊問題)"""
        self.preview_canvas.delete("all")
        
        y_current = 20 
        
        for idx, shape in enumerate(self.planes):
            self.preview_canvas.create_text(
                75, y_current, 
                text=f"飛機 {idx + 1}", 
                font=("Arial", 10, "bold"), 
                fill="#333333"
            )
            
            y_current += 20
            
            xs = [p[0] for p in shape]
            ys = [p[1] for p in shape]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            
            plane_height_px = (max_y - min_y + 1) * PREVIEW_CELL_SIZE
            plane_width_px = (max_x - min_x + 1) * PREVIEW_CELL_SIZE
            
            for i, (dx, dy) in enumerate(shape):
                norm_x = dx - min_x
                norm_y = dy - min_y
                
                cx = 75 - (plane_width_px / 2) + (norm_x * PREVIEW_CELL_SIZE) + (PREVIEW_CELL_SIZE / 2)
                
                cy = y_current + (norm_y * PREVIEW_CELL_SIZE) + (PREVIEW_CELL_SIZE / 2)
                
                color = COLOR_HEAD if i == 0 else COLOR_BODY
                self.preview_canvas.create_rectangle(
                    cx - PREVIEW_CELL_SIZE/2, cy - PREVIEW_CELL_SIZE/2,
                    cx + PREVIEW_CELL_SIZE/2, cy + PREVIEW_CELL_SIZE/2,
                    fill=color, outline="white"
                )
            
            y_current += plane_height_px + 30

    def use_bomb(self):
        """按下炸彈按鈕：切換『轟炸模式』開關"""
        if self.bomb_available <= 0 or self.game_over:
            return

        if not self.is_bombing:
            self.is_bombing = True
            self.btn_bomb.config(text="請點擊目標...", bg="#FFCCCC", relief="sunken") # 按鈕變粉紅色提示
        else:
            self.is_bombing = False
            self.btn_bomb.config(text="使用炸彈 (1)", bg="SystemButtonFace", relief="raised")

    def execute_bomb_at(self, r, c):
        """在指定座標執行轟炸 (九宮格)"""
        self.bomb_available = 0
        self.is_bombing = False
        self.btn_bomb.config(text="炸彈已耗盡", state=tk.DISABLED, bg="SystemButtonFace", relief="raised")
        
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    self.reveal_cell(nr, nc)


# ============================================================
# 【主程式入口】建立視窗並啟動遊戲
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x550")
    PlaneGame(root)
    root.mainloop()
