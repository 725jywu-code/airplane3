# ============================================================
# 【第 1 段】匯入模組
# 目的：載入 GUI、對話框與隨機工具
# ============================================================
import tkinter as tk
from tkinter import messagebox
import random


# ============================================================
# 【第 2 段】遊戲基本參數設定
# 目的：統一管理棋盤與格子大小
# ============================================================
GRID_SIZE = 10              # 棋盤大小為 10x10
CELL_SIZE = 40              # 主棋盤格子大小
PREVIEW_CELL_SIZE = 20      # 右側預覽飛機格子大小


# ============================================================
# 【第 3 段】顏色與視覺風格設定 (深色雷達風)
# 目的：讓不同狀態有明確顏色區分
# ============================================================
# 介面基礎色 (採用 Nord 主題配色風格)
THEME_BG = "#2E3440"        # 背景色 (深灰藍)
THEME_FG = "#D8DEE9"        # 主要文字色 (灰白)
THEME_ACCENT = "#88C0D0"    # 強調色 (青色)
THEME_BTN_BG = "#EBCB8B"    # 功能按鈕底色 (黃色)

# 遊戲格子顏色
COLOR_DEFAULT = "#4C566A"   # 未翻開 (較淺的灰藍)
COLOR_HOVER = "#5E81AC"     # 滑鼠滑過
COLOR_MISS = "#ECEFF4"      # 空包彈 (白)
COLOR_BODY = "#5E81AC"      # 機身 (藍)
COLOR_HEAD = "#BF616A"      # 機頭 (紅)

# 字體設定
BTN_FONT = ("Microsoft JhengHei", 10, "bold")
UI_FONT = ("Microsoft JhengHei", 12)
HEADER_FONT = ("Microsoft JhengHei", 16, "bold")


# ============================================================
# 【第 4 段】PlaneGame 類別（主遊戲架構）
# 目的：將整個遊戲封裝成一個物件
# ============================================================
class PlaneGame:
    def __init__(self, root):
        self.root = root
        self.root.title("尋找機頭 - 雷達作戰中心")
        self.root.geometry("780x600")
        self.root.configure(bg=THEME_BG)

        # 【優化】將難度設定對應表放入類別變數
        self.DIFFICULTY_MODES = {
            "簡單": 40,
            "一般": 30,
            "困難": 20
        }

        # ====================================================
        # 【第 5 段】遊戲資料結構與狀態變數
        # ====================================================
        self.grid_data = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.buttons = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.planes = []
        self.total_heads = 0
        self.found_heads = 0
        self.steps = 0
        self.max_steps = 0
        self.game_over = False
        self.bomb_available = 1
        self.is_bombing = False

        # 介面初始化
        self._setup_ui()
        self.root.after(100, self.ask_start_game)

    def _setup_ui(self):
        """建構所有 Tkinter UI 元素"""
        # ====================================================
        # 【第 6 段】上方資訊列
        # ====================================================
        self.top_frame = tk.Frame(self.root, bg=THEME_BG, pady=15)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.lbl_steps = tk.Label(self.top_frame, text="步數: 0", font=UI_FONT, bg=THEME_BG, fg=THEME_FG)
        self.lbl_steps.pack(side=tk.LEFT, padx=30)

        self.lbl_heads = tk.Label(self.top_frame, text="剩餘目標: 0", font=UI_FONT, bg=THEME_BG, fg=COLOR_HEAD)
        self.lbl_heads.pack(side=tk.LEFT, padx=20)

        # 右上角按鈕群
        btn_frame = tk.Frame(self.top_frame, bg=THEME_BG)
        btn_frame.pack(side=tk.RIGHT, padx=30)

        self.btn_restart = tk.Button(btn_frame, text="↺ 重置任務", command=self.ask_start_game,
                                     font=BTN_FONT, bg=THEME_ACCENT, fg="#2E3440", relief="flat", padx=10)
        self.btn_restart.pack(side=tk.RIGHT, padx=5)

        self.btn_bomb = tk.Button(btn_frame, text="💣 呼叫空襲 (1)", command=self.use_bomb,
                                  font=BTN_FONT, bg=THEME_BTN_BG, fg="#2E3440", relief="flat", padx=10)
        self.btn_bomb.pack(side=tk.RIGHT, padx=5)

        # ====================================================
        # 【第 7 段】主畫面與右側飛機預覽區
        # ====================================================
        self.main_container = tk.Frame(self.root, bg=THEME_BG)
        self.main_container.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # 左側：遊戲棋盤
        self.game_frame = tk.Frame(self.main_container, bg=THEME_BG)
        self.game_frame.pack(side=tk.LEFT, padx=20)
        self._init_grid_ui()

        # 右側：情報區
        self.info_frame = tk.Frame(self.main_container, bg=THEME_BG, width=220)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        tk.Label(self.info_frame, text="▼ 敵機情報 ▼", font=HEADER_FONT, bg=THEME_BG, fg=THEME_ACCENT).pack(pady=(0, 10))
        
        self.preview_canvas = tk.Canvas(self.info_frame, width=200, height=450, bg=THEME_BG, highlightthickness=0)
        self.preview_canvas.pack()

    # ========================================================
    # 【第 8 段】建立棋盤按鈕
    # ========================================================
    def _init_grid_ui(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                btn = tk.Button(
                    self.game_frame, width=4, height=2,
                    bg=COLOR_DEFAULT, activebackground=COLOR_HOVER,
                    relief="groove", borderwidth=1,
                    command=lambda row=r, col=c: self.on_click(row, col)
                )
                btn.grid(row=r, column=c, padx=1, pady=1)
                self.buttons[r][c] = btn

    # ========================================================
    # 【第 9 段】遊戲設定與開始邏輯
    # ========================================================
    def ask_start_game(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("新任務設定")
        settings_win.geometry("320x400")
        settings_win.configure(bg="#F0F0F0") 
        settings_win.transient(self.root)
        settings_win.grab_set()
        
        # 【修正】處理使用者直接點擊 X 關閉視窗 (穩健性優化)
        settings_win.protocol("WM_DELETE_WINDOW", lambda: self.handle_settings_close(settings_win))

        frame_center = tk.Frame(settings_win, bg="#F0F0F0")
        frame_center.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # 1. 飛機數量
        tk.Label(frame_center, text="請選擇飛機數量", font=("Microsoft JhengHei", 12, "bold"), bg="#F0F0F0").pack(pady=(0, 10))
        var_planes = tk.IntVar(value=2)
        frame_planes = tk.Frame(frame_center, bg="#F0F0F0")
        frame_planes.pack(pady=5)
        
        tk.Radiobutton(frame_planes, text="2 架", variable=var_planes, value=2, indicatoron=0, width=8, height=2, selectcolor="#ADD8E6", font=("Microsoft JhengHei", 10)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_planes, text="3 架", variable=var_planes, value=3, indicatoron=0, width=8, height=2, selectcolor="#ADD8E6", font=("Microsoft JhengHei", 10)).pack(side=tk.LEFT, padx=5)

        # 2. 難度
        tk.Label(frame_center, text="請選擇難度", font=("Microsoft JhengHei", 12, "bold"), bg="#F0F0F0").pack(pady=(20, 10))
        var_diff = tk.StringVar(value="一般")
        frame_diff = tk.Frame(frame_center, bg="#F0F0F0")
        frame_diff.pack(pady=5)

        # 難度模式列表 (文本, 顏色)
        modes = [("簡單", "#90EE90"), ("一般", "#FFFFE0"), ("困難", "#FFB6C1")]
        for text, color in modes:
            tk.Radiobutton(frame_diff, text=text, variable=var_diff, value=text, indicatoron=0, width=6, height=2, selectcolor=color, font=("Microsoft JhengHei", 10)).pack(side=tk.LEFT, padx=2)

        def confirm():
            """【優化】：使用字典查找步數上限，提高可讀性"""
            num = var_planes.get()
            diff_text = var_diff.get()
            steps = self.DIFFICULTY_MODES.get(diff_text, 30) # 預設為一般 (30)
            settings_win.destroy()
            self.start_game(num, steps)

        tk.Button(frame_center, text="開始任務", command=confirm, font=("Microsoft JhengHei", 14, "bold"), bg="#4CAF50", fg="white", height=2, width=15, relief="flat").pack(pady=(30, 0))

    def handle_settings_close(self, settings_win):
        """【新增】處理設定視窗被 X 關閉的事件 (如果遊戲已開始則不動作)"""
        if self.total_heads == 0 and self.steps == 0:
            # 首次啟動但取消，退出應用
            self.root.quit()
        else:
            # 遊戲已在進行，則只是關閉設定視窗
            settings_win.destroy()


    def start_game(self, num_planes, max_steps):
        """重置遊戲狀態並開始新局"""
        self.max_steps = max_steps
        self.steps = 0
        self.total_heads = num_planes
        self.found_heads = 0
        self.planes.clear()
        self.bomb_available = 1
        self.game_over = False
        self.is_bombing = False

        self.lbl_steps.config(text=f"步數: 0 / 上限: {self.max_steps}")
        self.lbl_heads.config(text=f"剩餘目標: {self.total_heads}")
        self.btn_bomb.config(text="💣 呼叫空襲 (1)", state=tk.NORMAL, bg=THEME_BTN_BG, relief="flat")
        self.preview_canvas.delete("all")

        # 重置棋盤狀態與 UI
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.grid_data[r][c] = None
                self.buttons[r][c].config(
                    bg=COLOR_DEFAULT, state=tk.NORMAL, text="", 
                    relief="groove" # 確保重設 relief
                )

        self.place_planes(num_planes)
        self.draw_plane_previews()

    def disable_all_buttons(self):
        """【新增】遊戲結束時，禁用所有按鈕 (用於步數超限或勝利)"""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.buttons[r][c].config(state=tk.DISABLED)


    # ========================================================
    # 【第 10 段】飛機生成、旋轉與放置演算法
    # ========================================================
    def generate_random_shape(self):
        """隨機生成飛機基礎形狀 (未旋轉，機頭在 (0, 0))"""
        shape = [(0, 0), (0, 1)] # 頭+頸
        body_len = random.randint(2, 4)
        wing_len = random.randint(1, 3)
        for i in range(2, body_len + 1): shape.append((0, i))
        for i in range(1, wing_len + 1):
            shape.append((-i, 1))
            shape.append((i, 1))
        if random.choice([True, False]): # 尾翼
            shape.append((-1, body_len)); shape.append((1, body_len))
        return shape

    def rotate_shape(self, shape, angle):
        """根據角度旋轉座標點"""
        new_shape = []
        for x, y in shape:
            if angle == 90: nx, ny = -y, x
            elif angle == 180: nx, ny = -x, -y
            elif angle == 270: nx, ny = y, -x
            else: nx, ny = x, y
            new_shape.append((nx, ny))
        return new_shape

    def place_planes(self, count):
        """【修正】放置飛機並儲存原始形狀"""
        placed = 0
        while placed < count:
            raw_shape = self.generate_random_shape() # <-- 取得原始形狀
            rotation_angle = random.choice([0, 90, 180, 270])
            rotated_shape = self.rotate_shape(raw_shape, rotation_angle)
            
            r, c = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            
            if self.is_valid_position(r, c, rotated_shape):
                self.add_plane_to_grid(r, c, rotated_shape)
                self.planes.append(raw_shape) # <-- 【關鍵修正】：儲存原始形狀供右側預覽
                placed += 1

    def is_valid_position(self, r, c, shape):
        """檢查飛機是否越界或重疊"""
        for dx, dy in shape:
            nr, nc = r + dy, c + dx
            if not (0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE): return False
            if self.grid_data[nr][nc] is not None: return False
        return True

    def add_plane_to_grid(self, r, c, shape):
        """將飛機數據寫入棋盤"""
        for i, (dx, dy) in enumerate(shape):
            nr, nc = r + dy, c + dx
            self.grid_data[nr][nc] = 'H' if i == 0 else 'B'


    # ========================================================
    # 【第 11 段】點擊翻格 (包含勝負判定)
    # ========================================================
    def on_click(self, r, c):
        """處理單次點擊事件，包含步數限制檢查"""
        if self.game_over: return

        if self.is_bombing:
            self.execute_bomb_at(r, c)
            return

        if self.buttons[r][c]["state"] == tk.DISABLED: return

        self.steps += 1
        self.lbl_steps.config(text=f"步數: {self.steps} / 上限: {self.max_steps}")

        # 步數超限判定
        if self.steps > self.max_steps:
            self.game_over = True
            self.disable_all_buttons() # 【修正】：遊戲失敗禁用所有按鈕
            messagebox.showinfo("任務失敗", "步數已用盡，作戰失敗！")
            return

        self.reveal_cell(r, c)

    def reveal_cell(self, r, c):
        """揭示單個格子內容並更新 UI"""
        btn = self.buttons[r][c]
        if btn["state"] == tk.DISABLED: return # 已經被揭示或炸開

        cell = self.grid_data[r][c]
        
        # 根據內容設定顏色與狀態
        if cell is None:
            btn.config(bg=COLOR_MISS, relief="sunken") # 空格
        elif cell == 'B':
            btn.config(bg=COLOR_BODY, relief="sunken") # 機身
        elif cell == 'H':
            btn.config(bg=COLOR_HEAD, text="X", relief="sunken") # 機頭
            self.found_heads += 1
            self.lbl_heads.config(text=f"剩餘目標: {self.total_heads - self.found_heads}")
            
            # 獲勝判定
            if self.found_heads == self.total_heads:
                self.game_over = True
                self.disable_all_buttons() # 【修正】：遊戲勝利禁用所有按鈕
                messagebox.showinfo("任務完成", f"恭喜！您以 {self.steps} 步殲滅了所有敵機！")

        btn.config(state=tk.DISABLED)


    # ========================================================
    # 【第 12 段】預覽繪製 & 炸彈功能
    # ========================================================
    def use_bomb(self):
        """切換轟炸模式"""
        if self.bomb_available <= 0 or self.game_over: return

        self.is_bombing = not self.is_bombing
        
        if self.is_bombing:
            self.btn_bomb.config(text="鎖定目標中...", bg="#FF8888", relief="sunken")
        else:
            self.btn_bomb.config(text="💣 呼叫空襲 (1)", bg=THEME_BTN_BG, relief="flat")

    def execute_bomb_at(self, r, c):
        """執行 2x2 轟炸，並禁用炸彈按鈕"""
        self.bomb_available = 0
        self.is_bombing = False
        self.btn_bomb.config(text="空襲已耗盡", state=tk.DISABLED, bg="#555555", relief="sunken")

        # 炸開 2x2 區域 (點擊點 (r, c) 開始)
        for dr in range(0, 2):
            for dc in range(0, 2):
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    # 使用 reveal_cell 確保觸發機頭計數和勝負判定
                    self.reveal_cell(nr, nc)

    def draw_plane_previews(self):
        """繪製右側飛機預覽 (使用原始形狀繪製)"""
        self.preview_canvas.delete("all")
        y_current = 20
        
        for idx, shape in enumerate(self.planes):
            self.preview_canvas.create_text(
                100, y_current, text=f"敵機訊號 {idx + 1}", 
                font=("Microsoft JhengHei", 10, "bold"), fill=THEME_FG
            )
            y_current += 20
            
            # 計算邊界和尺寸
            xs = [p[0] for p in shape]; ys = [p[1] for p in shape]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            
            plane_height_blocks = max_y - min_y + 1
            plane_width_px = (max_x - min_x + 1) * PREVIEW_CELL_SIZE
            
            for i, (dx, dy) in enumerate(shape):
                norm_x = dx - min_x # 相對最小 X 偏移
                norm_y = dy - min_y # 相對最小 Y 偏移
                
                # X軸置中公式: 畫布寬度200
                cx = 100 - (plane_width_px / 2) + (norm_x * PREVIEW_CELL_SIZE) + (PREVIEW_CELL_SIZE / 2)
                cy = y_current + (norm_y * PREVIEW_CELL_SIZE) + (PREVIEW_CELL_SIZE / 2)
                
                color = COLOR_HEAD if i == 0 else COLOR_BODY
                self.preview_canvas.create_rectangle(
                    cx - PREVIEW_CELL_SIZE/2, cy - PREVIEW_CELL_SIZE/2,
                    cx + PREVIEW_CELL_SIZE/2, cy + PREVIEW_CELL_SIZE/2,
                    fill=color, outline="white"
                )
            # 計算下一個圖形的起始 Y 座標
            y_current += (plane_height_blocks * PREVIEW_CELL_SIZE) + 30


# ============================================================
# 【主程式入口】建立視窗並啟動遊戲
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    game = PlaneGame(root)
    root.mainloop()
