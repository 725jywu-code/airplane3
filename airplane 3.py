import tkinter as tk                     # 匯入 tkinter 模組，用於建立 GUI
from tkinter import messagebox, simpledialog  # 匯入對話框模組
import random                            # 匯入 random 模組，用於隨機生成飛機

# =============================
# 基本設定
# =============================
GRID_SIZE = 10                           # 遊戲格子數量 (10x10)
CELL_SIZE = 40                            # 遊戲格大小
PREVIEW_CELL_SIZE = 20                    # 右側預覽格大小

# 顏色定義
COLOR_DEFAULT = "#DDDDDD"                 # 未翻開的格子顏色 (灰色)
COLOR_MISS = "white"                      # 點擊空格 (沒打中) 顯示白色
COLOR_BODY = "#5555FF"                    # 機身顏色 (藍色)
COLOR_HEAD = "#FF4444"                    # 機頭顏色 (紅色)
COLOR_TEXT = "black"                      # 文字顏色

# =============================
# 遊戲主程式
# =============================
class PlaneGame:
    def __init__(self, root):
        self.root = root
        self.root.title("尋找機頭 - 隨機變體版")  # 視窗標題
        
        # --- 遊戲數據 ---
        self.grid_data = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # 存放格子內容 (None/機身/B/機頭/H)
        self.buttons = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]    # 存放按鈕物件
        self.planes = []                  # 存放所有飛機形狀
        self.total_heads = 0              # 飛機總數量
        self.found_heads = 0              # 已找到機頭數量
        self.steps = 0                     # 玩家已使用步數
        self.max_steps = None              # 最大步數限制
        self.game_over = False             # 遊戲是否結束

        # --- 炸彈玩法 ---
        self.bomb_available = 1            # 炸彈可使用次數 (一次)
        self.steps_per_bomb = 5            # 可保留步數概念，未來擴展用

        # --- 介面佈局 ---
        self.top_frame = tk.Frame(root, pady=10)   # 上方框架，用於顯示步數、機頭數、按鈕
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        
        # 顯示步數
        self.lbl_steps = tk.Label(self.top_frame, text="步數: 0", font=("Arial", 12))
        self.lbl_steps.pack(side=tk.LEFT, padx=20)
        
        # 顯示剩餘機頭數
        self.lbl_heads = tk.Label(self.top_frame, text="剩餘機頭: 0", font=("Arial", 12, "bold"), fg="red")
        self.lbl_heads.pack(side=tk.LEFT, padx=20)
        
        # 重新開始按鈕
        self.btn_restart = tk.Button(self.top_frame, text="重新開始", command=self.ask_start_game)
        self.btn_restart.pack(side=tk.RIGHT, padx=20)

        # 炸彈按鈕
        self.btn_bomb = tk.Button(self.top_frame, text=f"使用炸彈 ({self.bomb_available})", 
                                  command=self.use_bomb)
        self.btn_bomb.pack(side=tk.RIGHT, padx=20)

        # 下方主要容器
        self.main_container = tk.Frame(root)
        self.main_container.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 左側遊戲格子框架
        self.game_frame = tk.Frame(self.main_container)
        self.game_frame.pack(side=tk.LEFT, padx=10)
        
        self._init_grid_ui()  # 建立格子按鈕

        # 右側資訊框架
        self.info_frame = tk.Frame(self.main_container, width=200)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        self.lbl_info_title = tk.Label(self.info_frame, text="本局敵機情報", font=("Arial", 11, "bold"))
        self.lbl_info_title.pack(pady=5)
        
        # 預覽 Canvas
        self.preview_canvas = tk.Canvas(self.info_frame, width=150, height=400, bg="#F0F0F0")
        self.preview_canvas.pack(expand=True, fill=tk.BOTH)

        # 啟動遊戲
        self.ask_start_game()

    # ----------------------------
    # 建立遊戲格子 UI
    # ----------------------------
    def _init_grid_ui(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                # 建立每個格子按鈕
                btn = tk.Button(self.game_frame, width=4, height=2, bg=COLOR_DEFAULT,
                                command=lambda row=r, col=c: self.on_click(row, col))
                btn.grid(row=r, column=c, padx=1, pady=1)
                self.buttons[r][c] = btn  # 儲存按鈕

    # ----------------------------
    # 問題設定並開始遊戲
    # ----------------------------
    def ask_start_game(self):
        try:
            # 玩家輸入飛機數量 (2 或 3)
            num = simpledialog.askinteger("遊戲設定", "請輸入飛機數量 (2 或 3):", 
                                          minvalue=2, maxvalue=3, parent=self.root)
        except:
            num = 2
        if num is None: return  # 若取消，返回

        # 玩家選擇難度
        difficulty = simpledialog.askstring("選擇難度", "請輸入難度 (簡單/一般/困難):", parent=self.root)
        if difficulty is None: return
        difficulty = difficulty.strip()
        # 設定最大步數
        if difficulty == "簡單":
            max_steps = 50
        elif difficulty == "一般":
            max_steps = 35
        elif difficulty == "困難":
            max_steps = 25
        else:
            max_steps = 50
            
        self.start_game(num, max_steps)  # 開始遊戲

    # ----------------------------
    # 開始新遊戲
    # ----------------------------
    def start_game(self, num_planes, max_steps):
        self.max_steps = max_steps
        self.game_over = False
        self.steps = 0
        self.total_heads = num_planes
        self.found_heads = 0
        self.planes = []
        self.bomb_available = 1
        self.btn_bomb.config(text=f"使用炸彈 ({self.bomb_available})", state=tk.NORMAL)
        
        self.lbl_steps.config(text=f"步數: 0 / 上限: {self.max_steps}")  # 更新步數標籤
        self.update_head_label()                                         # 更新剩餘機頭標籤
        self.preview_canvas.delete("all")                                # 清空右側預覽

        # 重置格子內容及顏色
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.grid_data[r][c] = None
                self.buttons[r][c].config(bg=COLOR_DEFAULT, state=tk.NORMAL, text="")

        self.place_planes(num_planes)   # 放置飛機
        self.draw_plane_previews()      # 繪製右側預覽

    # ----------------------------
    # 生成隨機飛機形狀
    # ----------------------------
    def generate_random_shape(self):
        shape = [(0, 0), (0, 1)]                    # 機頭+機身初始位置
        wing_y = 1
        wing_len = random.randint(1, 3)            # 翅膀長度隨機
        body_len = random.randint(2, 4)            # 機身長度隨機
        for i in range(2, body_len + 1):
            shape.append((0, i))                    # 機身
        for i in range(1, wing_len + 1):
            shape.append((-i, wing_y))             # 左翅
            shape.append((i, wing_y))              # 右翅
        # 隨機尾翼
        if random.choice([True, False]):
            tail_y = body_len
            shape.append((-1, tail_y))
            shape.append((1, tail_y))
        return shape

    # ----------------------------
    # 放置飛機
    # ----------------------------
    def place_planes(self, count):
        placed_count = 0
        attempts = 0
        while placed_count < count and attempts < 1000:
            attempts += 1
            raw_shape = self.generate_random_shape()                 # 生成飛機形狀
            rotation = random.choice([0, 90, 180, 270])             # 隨機旋轉角度
            rotated_shape = self.rotate_shape(raw_shape, rotation)  # 旋轉
            start_r = random.randint(0, GRID_SIZE-1)                # 隨機起始行
            start_c = random.randint(0, GRID_SIZE-1)                # 隨機起始列
            if self.is_valid_position(start_r, start_c, rotated_shape):  # 檢查是否可以放置
                self.add_plane_to_grid(start_r, start_c, rotated_shape)  # 放置到格子
                self.planes.append(raw_shape)                  # 保存飛機形狀
                placed_count += 1

    # ----------------------------
    # 旋轉飛機形狀
    # ----------------------------
    def rotate_shape(self, shape, angle):
        new_shape = []
        for x, y in shape:
            if angle == 0: nx, ny = x, y
            elif angle == 90: nx, ny = -y, x
            elif angle == 180: nx, ny = -x, -y
            elif angle == 270: nx, ny = y, -x
            new_shape.append((nx, ny))
        return new_shape

    # ----------------------------
    # 檢查飛機是否可以放置
    # ----------------------------
    def is_valid_position(self, r, c, shape):
        for dx, dy in shape:
            nr, nc = r + dy, c + dx
            if not (0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE):  # 超出邊界
                return False
            if self.grid_data[nr][nc] is not None:               # 與其他飛機重疊
                return False
        return True

    # ----------------------------
    # 放置飛機到格子
    # ----------------------------
    def add_plane_to_grid(self, r, c, shape):
        for i, (dx, dy) in enumerate(shape):
            nr, nc = r + dy, c + dx
            if i == 0:
                self.grid_data[nr][nc] = 'H'    # 機頭
            else:
                self.grid_data[nr][nc] = 'B'    # 機身

    # ----------------------------
    # 點擊格子
    # ----------------------------
    def on_click(self, r, c):
        if self.game_over: return           # 遊戲結束後不能點
        btn = self.buttons[r][c]
        if btn['state'] == tk.DISABLED: return  # 已翻開不可點

        self.steps += 1
        self.lbl_steps.config(text=f"步數: {self.steps} / 上限: {self.max_steps}")  # 更新步數

        if self.steps > self.max_steps:        # 超過步數上限
            self.game_over = True
            messagebox.showinfo("遊戲失敗", f"已超過步數上限 ({self.max_steps})！遊戲結束。")
            for row in self.buttons:
                for b in row:
                    b.config(state=tk.DISABLED)  # 禁用所有格子
            return
        
        self.reveal_cell(r, c)                 # 翻開格子

    # ----------------------------
    # 翻開單格 (供炸彈或點擊使用)
    # ----------------------------
    def reveal_cell(self, r, c):
        btn = self.buttons[r][c]
        if btn['state'] == tk.DISABLED: return  # 已翻開不可再點
        
        content = self.grid_data[r][c]
        if content is None:
            btn.config(bg=COLOR_MISS, state=tk.DISABLED)     # 空格
        elif content == 'B':
            btn.config(bg=COLOR_BODY, state=tk.DISABLED)     # 機身
        elif content == 'H':
            btn.config(bg=COLOR_HEAD, state=tk.DISABLED, text="X")  # 機頭
            self.found_heads += 1
            self.update_head_label()
            self.check_win()

    # ----------------------------
    # 更新剩餘機頭數
    # ----------------------------
    def update_head_label(self):
        remain = self.total_heads - self.found_heads
        self.lbl_heads.config(text=f"剩餘機頭: {remain}")

    # ----------------------------
    # 判斷是否獲勝
    # ----------------------------
    def check_win(self):
        if self.found_heads == self.total_heads:
            self.game_over = True
            messagebox.showinfo("獲勝！", f"恭喜！你用了 {self.steps} 步找到了所有飛機！")

    # ----------------------------
    # 繪製右側飛機預覽
    # ----------------------------
    def draw_plane_previews(self):
        y_offset = 20
        x_center = 75
        for idx, shape in enumerate(self.planes):
            self.preview_canvas.create_text(x_center, y_offset, text=f"飛機 {idx+1}", font=("Arial", 10))
            y_offset += 20
            xs = [p[0] for p in shape]
            ys = [p[1] for p in shape]
            for i, (dx, dy) in enumerate(shape):
                cx = x_center + dx * PREVIEW_CELL_SIZE
                cy = y_offset + dy * PREVIEW_CELL_SIZE + 20
                color = COLOR_HEAD if i == 0 else COLOR_BODY
                self.preview_canvas.create_rectangle(
                    cx - PREVIEW_CELL_SIZE/2, cy - PREVIEW_CELL_SIZE/2,
                    cx + PREVIEW_CELL_SIZE/2, cy + PREVIEW_CELL_SIZE/2,
                    fill=color, outline="white"
                )
            height_blocks = max(ys) - min(ys) + 1
            y_offset += (height_blocks * PREVIEW_CELL_SIZE) + 40

    # ----------------------------
    # 使用炸彈 (只能用一次，炸 2x2)
    # ----------------------------
    def use_bomb(self):
        if self.game_over: return
        if self.bomb_available <= 0:
            messagebox.showinfo("炸彈", "炸彈已使用過，無法再次使用！")
            return

        # 玩家輸入炸彈格座標
        row = simpledialog.askinteger("炸彈格", "請輸入炸彈格行號 (0~9):", minvalue=0, maxvalue=GRID_SIZE-1, parent=self.root)
        col = simpledialog.askinteger("炸彈格", "請輸入炸彈格列號 (0~9):", minvalue=0, maxvalue=GRID_SIZE-1, parent=self.root)
        if row is None or col is None: return

        self.bomb_available -= 1                      # 使用炸彈
        self.btn_bomb.config(text=f"使用炸彈 ({self.bomb_available})", state=tk.DISABLED)
        
        # 翻開 2x2 區域
        for dr in range(0, 2):
            for dc in range(0, 2):
                nr, nc = row + dr, col + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    self.reveal_cell(nr, nc)

# =============================
# 啟動遊戲
# =============================
if __name__ == "__main__":
    root = tk.Tk()                      # 建立主視窗
    root.geometry("600x550")            # 設定視窗大小
    game = PlaneGame(root)              # 建立遊戲物件
    root.mainloop()                     # 啟動主迴圈
