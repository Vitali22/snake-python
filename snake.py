import json
import random
import tkinter as tk
from pathlib import Path


CELL_SIZE = 24
GRID_WIDTH = 24
GRID_HEIGHT = 18
START_SPEED_MS = 130
MIN_SPEED_MS = 65
SPEED_STEP = 3
BONUS_POINTS = 3
SPECIAL_FOOD_CHANCE = 0.35
SPECIAL_FOOD_TICKS = 45
OBSTACLE_EVERY_POINTS = 4
MAX_OBSTACLES = 28
HIGH_SCORE_FILE = Path(__file__).with_name("high_score.json")

BACKGROUND = "#111827"
GRID_LINE = "#1f2937"
SNAKE_HEAD = "#22c55e"
SNAKE_BODY = "#16a34a"
FOOD = "#ef4444"
SPECIAL_FOOD = "#f59e0b"
OBSTACLE = "#4b5563"
OBSTACLE_EDGE = "#9ca3af"
TEXT = "#f9fafb"
MUTED_TEXT = "#9ca3af"


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake")
        self.root.resizable(False, False)

        self.width = GRID_WIDTH * CELL_SIZE
        self.height = GRID_HEIGHT * CELL_SIZE

        self.score_var = tk.StringVar()
        self.status_var = tk.StringVar()

        header = tk.Frame(root, bg=BACKGROUND, padx=12, pady=10)
        header.pack(fill="x")

        score_label = tk.Label(
            header,
            textvariable=self.score_var,
            bg=BACKGROUND,
            fg=TEXT,
            font=("Segoe UI", 14, "bold"),
        )
        score_label.pack(side="left")

        status_label = tk.Label(
            header,
            textvariable=self.status_var,
            bg=BACKGROUND,
            fg=MUTED_TEXT,
            font=("Segoe UI", 10),
        )
        status_label.pack(side="right")

        self.canvas = tk.Canvas(
            root,
            width=self.width,
            height=self.height,
            bg=BACKGROUND,
            highlightthickness=0,
        )
        self.canvas.pack()

        footer = tk.Frame(root, bg=BACKGROUND, padx=12, pady=10)
        footer.pack(fill="x")

        controls = "Flechas o WASD para moverte | Espacio para pausar | R para reiniciar"
        tk.Label(
            footer,
            text=controls,
            bg=BACKGROUND,
            fg=MUTED_TEXT,
            font=("Segoe UI", 9),
        ).pack()

        self.root.bind("<KeyPress>", self.on_key_press)
        self.after_id = None
        self.high_score = self.load_high_score()
        self.reset()

    def reset(self):
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
        ]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.obstacles = set()
        self.food = self.place_food()
        self.special_food = None
        self.special_food_ticks = 0
        self.score = 0
        self.level = 1
        self.speed_ms = START_SPEED_MS
        self.game_over = False
        self.paused = False
        self.update_scoreboard()
        self.status_var.set("Come la comida roja")
        self.draw()
        self.schedule_tick()

    def schedule_tick(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(self.speed_ms, self.tick)

    def tick(self):
        if self.game_over:
            return
        if self.paused:
            self.schedule_tick()
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        move_x, move_y = self.direction
        new_head = (head_x + move_x, head_y + move_y)
        ate_food = new_head == self.food
        ate_special = new_head == self.special_food

        if (
            self.hit_wall(new_head)
            or self.hit_obstacle(new_head)
            or self.hit_self(new_head, grows=ate_food or ate_special)
        ):
            self.end_game()
            return

        self.snake.insert(0, new_head)

        if ate_food:
            self.score += 1
            self.after_food_eaten()
            self.food = self.place_food()
            if self.game_over:
                return
        elif ate_special:
            self.score += BONUS_POINTS
            self.special_food = None
            self.special_food_ticks = 0
            self.after_food_eaten()
        else:
            self.snake.pop()

        self.update_special_food_timer()
        self.draw()
        self.schedule_tick()

    def hit_wall(self, position):
        x, y = position
        return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT

    def hit_self(self, position, grows):
        body_to_check = self.snake if grows else self.snake[:-1]
        return position in body_to_check

    def hit_obstacle(self, position):
        return position in self.obstacles

    def place_food(self):
        available_cells = self.available_cells()
        if not available_cells:
            self.win_game()
            return None
        return random.choice(available_cells)

    def available_cells(self):
        blocked = set(getattr(self, "snake", []))
        blocked.update(getattr(self, "obstacles", set()))
        food = getattr(self, "food", None)
        special_food = getattr(self, "special_food", None)
        if food:
            blocked.add(food)
        if special_food:
            blocked.add(special_food)

        return [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in blocked
        ]

    def after_food_eaten(self):
        self.level = 1 + self.score // 5
        self.speed_ms = max(MIN_SPEED_MS, START_SPEED_MS - self.score * SPEED_STEP)
        self.maybe_add_obstacle()
        self.maybe_spawn_special_food()
        self.update_scoreboard()

    def maybe_add_obstacle(self):
        if self.score == 0 or self.score % OBSTACLE_EVERY_POINTS != 0:
            return
        if len(self.obstacles) >= MAX_OBSTACLES:
            return
        available_cells = self.available_cells()
        if available_cells:
            self.obstacles.add(random.choice(available_cells))

    def maybe_spawn_special_food(self):
        if self.special_food is not None:
            return
        if random.random() > SPECIAL_FOOD_CHANCE:
            return
        available_cells = self.available_cells()
        if available_cells:
            self.special_food = random.choice(available_cells)
            self.special_food_ticks = SPECIAL_FOOD_TICKS
            self.status_var.set("Comida dorada: vale 3 puntos")

    def update_special_food_timer(self):
        if self.special_food is None:
            return
        self.special_food_ticks -= 1
        if self.special_food_ticks <= 0:
            self.special_food = None
            self.status_var.set("Come la comida roja")

    def update_scoreboard(self):
        self.score_var.set(
            f"Puntos: {self.score} | Nivel: {self.level} | Record: {self.high_score}"
        )

    def on_key_press(self, event):
        key = event.keysym.lower()
        directions = {
            "up": (0, -1),
            "w": (0, -1),
            "down": (0, 1),
            "s": (0, 1),
            "left": (-1, 0),
            "a": (-1, 0),
            "right": (1, 0),
            "d": (1, 0),
        }

        if key in directions and not self.game_over:
            new_direction = directions[key]
            if not self.is_opposite(new_direction, self.direction):
                self.next_direction = new_direction
        elif key == "space" and not self.game_over:
            self.paused = not self.paused
            self.status_var.set("Pausado" if self.paused else "Come la comida roja")
            self.draw()
        elif key == "r":
            self.reset()

    def is_opposite(self, first, second):
        return first[0] + second[0] == 0 and first[1] + second[1] == 0

    def end_game(self):
        self.game_over = True
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            self.update_scoreboard()
        self.status_var.set("Fin del juego | Presiona R para reiniciar")
        self.draw()
        self.draw_overlay(
            "GAME OVER",
            f"Puntuacion final: {self.score}",
            "Presiona R para volver a jugar",
        )

    def win_game(self):
        self.game_over = True
        self.status_var.set("Ganaste | Presiona R para reiniciar")
        self.draw()
        self.draw_overlay("GANASTE", "Llenaste todo el tablero", "Presiona R para reiniciar")

    def draw_overlay(self, title, subtitle, hint):
        self.canvas.create_rectangle(
            0,
            self.height // 2 - 82,
            self.width,
            self.height // 2 + 82,
            fill="#020617",
            outline="",
            stipple="gray50",
        )
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 - 36,
            text=title,
            fill=TEXT,
            font=("Segoe UI", 28, "bold"),
        )
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 + 4,
            text=subtitle,
            fill=MUTED_TEXT,
            font=("Segoe UI", 14),
        )
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 + 38,
            text=hint,
            fill=SPECIAL_FOOD,
            font=("Segoe UI", 11, "bold"),
        )

    def draw(self):
        self.canvas.delete("all")
        self.draw_grid()

        for obstacle in self.obstacles:
            self.draw_cell(obstacle, OBSTACLE, outline=OBSTACLE_EDGE)

        if self.food is not None:
            self.draw_cell(self.food, FOOD, rounded=True)

        if self.special_food is not None:
            self.draw_cell(self.special_food, SPECIAL_FOOD, rounded=True)

        for index, segment in enumerate(self.snake):
            color = SNAKE_HEAD if index == 0 else SNAKE_BODY
            self.draw_cell(segment, color)

        if self.paused and not self.game_over:
            self.draw_overlay("PAUSA", "Respira tantito", "Presiona espacio para continuar")

    def draw_grid(self):
        for x in range(0, self.width, CELL_SIZE):
            self.canvas.create_line(x, 0, x, self.height, fill=GRID_LINE)
        for y in range(0, self.height, CELL_SIZE):
            self.canvas.create_line(0, y, self.width, y, fill=GRID_LINE)

    def draw_cell(self, position, color, outline="", rounded=False):
        x, y = position
        padding = 2
        left = x * CELL_SIZE + padding
        top = y * CELL_SIZE + padding
        right = (x + 1) * CELL_SIZE - padding
        bottom = (y + 1) * CELL_SIZE - padding

        if rounded:
            self.canvas.create_oval(left, top, right, bottom, fill=color, outline=outline)
        else:
            self.canvas.create_rectangle(left, top, right, bottom, fill=color, outline=outline)

    def load_high_score(self):
        try:
            with HIGH_SCORE_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
                return int(data.get("high_score", 0))
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            return 0

    def save_high_score(self):
        with HIGH_SCORE_FILE.open("w", encoding="utf-8") as file:
            json.dump({"high_score": self.high_score}, file)


def main():
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
