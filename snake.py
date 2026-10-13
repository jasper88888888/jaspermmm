#!/usr/bin/env python3
"""简单的贪吃蛇：python3 snake.py。只使用 Python 标准库。"""

import random


class SnakeGame:
    """游戏规则与窗口分开，方便阅读和测试。坐标单位为格子。"""

    def __init__(self, columns=24, rows=18):
        if columns < 3 or rows < 2:
            raise ValueError("棋盘至少需要 3 列、2 行")
        self.columns = columns
        self.rows = rows
        self.reset()

    def reset(self):
        x, y = max(2, self.columns // 2), self.rows // 2
        self.snake = [(x, y), (x - 1, y), (x - 2, y)]
        self.direction = (1, 0)
        self.turned = False
        self.score = 0
        self.paused = False
        self.game_over = False
        self.won = False
        self.place_food()

    def place_food(self):
        occupied = set(self.snake)
        empty = [(x, y) for y in range(self.rows)
                 for x in range(self.columns) if (x, y) not in occupied]
        self.food = random.choice(empty) if empty else None
        if self.food is None:
            self.won = True
            self.game_over = True

    def turn(self, direction):
        if self.paused or self.game_over or self.turned:
            return
        if direction not in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            return
        dx, dy = self.direction
        if direction in (self.direction, (-dx, -dy)):
            return
        self.direction = direction
        # 每次移动只接受一次转弯，避免连续按键让蛇原地掉头。
        self.turned = True

    def toggle_pause(self):
        if not self.game_over:
            self.paused = not self.paused

    def step(self):
        if self.paused or self.game_over:
            return
        x, y = self.snake[0]
        dx, dy = self.direction
        head = (x + dx, y + dy)
        eating = head == self.food
        # 不吃食物时尾巴会离开原来的格子，所以那里可以进入。
        body = self.snake if eating else self.snake[:-1]
        if (not 0 <= head[0] < self.columns
                or not 0 <= head[1] < self.rows or head in body):
            self.game_over = True
            return
        self.snake.insert(0, head)
        if eating:
            self.score += 10
            self.place_food()
        else:
            self.snake.pop()
        self.turned = False


class SnakeApp:
    CELL = 24
    INTERVAL = 130  # 每步的毫秒数；调小即可加快。
    BG = "#101923"
    BOARD = "#16232f"

    def __init__(self, root):
        import tkinter as tk

        self.root = root
        self.game = SnakeGame()
        self.started = False
        self.after_id = None
        root.title("贪吃蛇 · Snake")
        root.configure(bg=self.BG)
        root.resizable(False, False)

        header = tk.Frame(root, bg=self.BG)
        header.pack(fill="x", padx=20, pady=(18, 12))
        tk.Label(header, text="SNAKE / 贪吃蛇", fg="#e6f1f5", bg=self.BG,
                 font=("sans-serif", 18, "bold")).pack(side="left")
        self.score_label = tk.Label(header, fg="#7de3ac", bg=self.BG,
                                    font=("sans-serif", 14))
        self.score_label.pack(side="right")
        self.canvas = tk.Canvas(
            root, width=self.game.columns * self.CELL,
            height=self.game.rows * self.CELL, bg=self.BOARD,
            highlightthickness=1, highlightbackground="#304353")
        self.canvas.pack(padx=20)
        tk.Label(root, text="方向键 / WASD 移动    空格 暂停    R 重开    Esc 退出",
                 fg="#bacad5", bg=self.BG,
                 font=("sans-serif", 11)).pack(pady=(12, 8))
        controls = tk.Frame(root, bg=self.BG)
        controls.pack(pady=(0, 16))
        self.pause_button = tk.Button(controls, text="开始 / 暂停", width=12,
                                      command=self.pause, takefocus=False)
        self.pause_button.pack(side="left", padx=6)
        tk.Button(controls, text="重新开始 (R)", width=14,
                  command=self.restart, takefocus=False).pack(side="left", padx=6)
        root.bind("<KeyPress>", self.on_key)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.draw()
        self.after_id = root.after(self.INTERVAL, self.tick)

    def on_key(self, event):
        key = event.keysym.lower()
        directions = {"up": (0, -1), "w": (0, -1),
                      "down": (0, 1), "s": (0, 1),
                      "left": (-1, 0), "a": (-1, 0),
                      "right": (1, 0), "d": (1, 0)}
        if key in directions:
            self.started = True
            self.game.turn(directions[key])
            self.draw()
        elif key == "space":
            self.pause()
        elif key == "r":
            self.restart()
        elif key == "escape":
            self.close()
        return "break"

    def pause(self):
        if not self.started:
            self.started = True
        else:
            self.game.toggle_pause()
        self.draw()

    def restart(self):
        self.game.reset()
        self.started = False
        self.draw()

    def tick(self):
        if self.started:
            self.game.step()
        self.draw()
        self.after_id = self.root.after(self.INTERVAL, self.tick)

    def draw(self):
        canvas, game, cell = self.canvas, self.game, self.CELL
        canvas.delete("all")
        width, height = game.columns * cell, game.rows * cell
        for x in range(cell, width, cell):
            canvas.create_line(x, 0, x, height, fill="#1d2d3b")
        for y in range(cell, height, cell):
            canvas.create_line(0, y, width, y, fill="#1d2d3b")
        if game.food is not None:
            x, y = game.food
            canvas.create_oval(x * cell + 4, y * cell + 4,
                               (x + 1) * cell - 4, (y + 1) * cell - 4,
                               fill="#ff8b75", outline="")
        for i, (x, y) in enumerate(game.snake):
            canvas.create_rectangle(x * cell + 2, y * cell + 2,
                                    (x + 1) * cell - 2, (y + 1) * cell - 2,
                                    fill="#b5f5ce" if i == 0 else "#59c68d",
                                    outline="")
        self.score_label.configure(text=f"得分  {game.score}")
        self.pause_button.configure(
            text="继续" if game.paused else "开始 / 暂停",
            state="disabled" if game.game_over else "normal")
        message = ""
        if game.game_over:
            message = "恭喜通关！" if game.won else "游戏结束"
            message += f"\n得分：{game.score}   ·   按 R 重新开始"
        elif not self.started:
            message = "准备好了吗？\n按方向键或空格开始"
        elif game.paused:
            message = "已暂停\n按空格继续"
        if message:
            canvas.create_rectangle(32, height / 2 - 55, width - 32,
                                    height / 2 + 55, fill=self.BG,
                                    outline="#426252")
            canvas.create_text(width / 2, height / 2, text=message,
                               fill="#eef8f2", font=("sans-serif", 17),
                               justify="center")

    def close(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.root.destroy()


def main():
    try:
        import tkinter as tk
    except ImportError:
        raise SystemExit("需要安装 Tkinter。Ubuntu/Debian 可运行：sudo apt install python3-tk")
    try:
        root = tk.Tk()
    except tk.TclError as error:
        raise SystemExit(f"无法打开游戏窗口，请在带图形桌面的环境中运行。\n{error}")
    SnakeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
