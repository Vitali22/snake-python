import json
import random
import tkinter as tk
import time
import winsound
from pathlib import Path


CELL_SIZE = 28
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
GAME_VERSION = "1.6.0"
BOMB_DISTANCE = 5
EXPLOSION_TICKS = 5
FLOATING_TEXT_TICKS = 18
STARTING_LIVES = 3
MAX_LIVES = 6
SHIELD_CHANCE = 0.18
SHIELD_TICKS = 55
BOSS_TIMES = [20, 30, 40]
BOSS_DURATION_SECONDS = 7
BOSS_VULNERABLE_SECONDS = 3
BOSS_MOVE_EVERY = 5
BOSS_POINTS = 5

DIFFICULTY_CONFIG = {
    1: {
        "name": "Clasico",
        "start_speed": 160,
        "min_speed": 92,
        "bomb_chance": 0.14,
        "bomb_ticks": 8,
        "bomb_min_score": 3,
        "ghost_count": 0,
        "ghost_move_every": 99,
    },
    2: {
        "name": "Persecucion",
        "start_speed": 155,
        "min_speed": 88,
        "bomb_chance": 0.18,
        "bomb_ticks": 7,
        "bomb_min_score": 2,
        "ghost_count": 1,
        "ghost_move_every": 4,
    },
    3: {
        "name": "Caos",
        "start_speed": 145,
        "min_speed": 82,
        "bomb_chance": 0.28,
        "bomb_ticks": 5,
        "bomb_min_score": 1,
        "ghost_count": 2,
        "ghost_move_every": 2,
    },
}

BACKGROUND = "#111827"
GRID_LINE = "#1f2937"
SNAKE_HEAD = "#22c55e"
SNAKE_BODY = "#16a34a"
FOOD = "#ef4444"
SPECIAL_FOOD = "#f59e0b"
SHIELD_POWER = "#38bdf8"
SHIELD_RING = "#bae6fd"
OBSTACLE = "#4b5563"
OBSTACLE_EDGE = "#9ca3af"
BOMB = "#111827"
BOMB_FUSE = "#f97316"
BOMB_TEXT = "#fef3c7"
GHOST = "#a78bfa"
GHOST_DARK = "#7c3aed"
GHOST_EYE = "#f8fafc"
EXPLOSION = "#f97316"
EXPLOSION_CORE = "#fde047"
BOSS = "#dc2626"
BOSS_EDGE = "#fecaca"
BOSS_VULNERABLE = "#22c55e"
BOSS_VULNERABLE_EDGE = "#bbf7d0"
BOARD_BORDER = "#e5e7eb"
TEXT = "#f9fafb"
MUTED_TEXT = "#9ca3af"


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Snake v{GAME_VERSION}")
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
            highlightthickness=3,
            highlightbackground=BOARD_BORDER,
            highlightcolor=BOARD_BORDER,
        )
        self.canvas.pack()

        footer = tk.Frame(root, bg=BACKGROUND, padx=12, pady=10)
        footer.pack(fill="x")

        controls = "1/2/3 elegir nivel | Flechas o WASD moverte | Espacio pausar | R reiniciar | L niveles | M sonido"
        tk.Label(
            footer,
            text=controls,
            bg=BACKGROUND,
            fg=MUTED_TEXT,
            font=("Segoe UI", 9),
        ).pack()

        self.root.bind("<KeyPress>", self.on_key_press)
        self.after_id = None
        self.sound_enabled = True
        self.high_scores = self.load_high_scores()
        self.selected_level = 1
        self.config = DIFFICULTY_CONFIG[self.selected_level]
        self.waiting_for_level = True
        self.show_level_menu()

    def show_level_menu(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.waiting_for_level = True
        self.game_over = False
        self.paused = False
        records = " | ".join(
            f"N{level}: {self.high_scores.get(str(level), 0)}" for level in [1, 2, 3]
        )
        self.score_var.set(f"v{GAME_VERSION} | Elige nivel | Records {records}")
        self.status_var.set("Presiona 1, 2 o 3")
        self.draw_level_menu()

    def reset(self, selected_level=None):
        if selected_level is not None:
            self.selected_level = selected_level
        self.config = DIFFICULTY_CONFIG[self.selected_level]
        self.waiting_for_level = False
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
        self.bombs = {}
        self.food = None
        self.special_food = None
        self.special_food_ticks = 0
        self.shield_power = None
        self.shield_ticks = 0
        self.lives = STARTING_LIVES
        self.ghost_tick = 0
        self.extra_life_ticks = 0
        self.explosions = {}
        self.floating_texts = []
        self.ghosts = self.create_ghosts()
        self.boss_cells = set()
        self.boss_active = False
        self.boss_spawned = set()
        self.boss_started_at = None
        self.boss_tick = 0
        self.started_at = time.monotonic()
        self.food = self.place_food()
        self.score = 0
        self.level = 1
        self.speed_ms = self.config["start_speed"]
        self.game_over = False
        self.paused = False
        self.update_scoreboard()
        self.status_var.set(f"Nivel {self.selected_level}: {self.config['name']}")
        self.draw()
        self.schedule_tick()

    def schedule_tick(self):
        if self.waiting_for_level:
            return
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(self.speed_ms, self.tick)

    def tick(self):
        if self.game_over or self.waiting_for_level:
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
        ate_shield = new_head == self.shield_power
        hit_bomb = self.hit_bomb(new_head)
        hit_ghost = self.hit_ghost(new_head)
        hit_boss = self.hit_boss(new_head)

        if self.hit_wall(new_head) or self.hit_obstacle(new_head):
            self.end_game()
            return
        if hit_boss and self.boss_is_vulnerable():
            self.eat_boss()
            if self.game_over:
                return
            hit_boss = False
        if hit_bomb or hit_ghost or hit_boss:
            if not self.handle_danger_hit(new_head, hit_bomb, hit_ghost, hit_boss):
                return
        if self.hit_self(new_head, grows=ate_food or ate_special or ate_shield):
            self.end_game()
            return

        self.snake.insert(0, new_head)

        if ate_food:
            self.score += 1
            self.play_sound("eat")
            self.after_food_eaten()
            self.food = self.place_food()
            if self.game_over:
                return
        elif ate_special:
            self.score += BONUS_POINTS
            self.special_food = None
            self.special_food_ticks = 0
            self.after_food_eaten()
            self.play_sound("bonus")
        elif ate_shield:
            self.shield_power = None
            self.shield_ticks = SHIELD_TICKS
            self.status_var.set("Escudo activado")
            self.play_sound("shield")
        else:
            self.snake.pop()

        self.update_special_food_timer()
        self.update_shield_timer()
        self.update_extra_life_timer()
        self.update_bombs()
        self.update_explosions()
        self.update_floating_texts()
        self.update_boss()
        if self.game_over:
            return
        if self.hit_boss(self.snake[0]):
            if not self.handle_danger_hit(self.snake[0], False, False, True):
                return
        self.maybe_spawn_bomb()
        self.maybe_spawn_shield_power()
        if self.update_ghosts():
            self.end_game(caught=True)
            return
        self.update_scoreboard()
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

    def hit_bomb(self, position):
        return position in self.bombs

    def hit_ghost(self, position):
        return position in self.ghosts

    def hit_boss(self, position):
        return position in self.boss_cells

    def create_ghosts(self):
        corners = [
            (2, 2),
            (GRID_WIDTH - 3, GRID_HEIGHT - 3),
            (GRID_WIDTH - 3, 2),
            (2, GRID_HEIGHT - 3),
        ]
        return corners[: self.config["ghost_count"]]

    def place_food(self):
        available_cells = self.available_cells()
        if not available_cells:
            self.win_game()
            return None
        return random.choice(available_cells)

    def available_cells(self):
        blocked = set(getattr(self, "snake", []))
        blocked.update(getattr(self, "obstacles", set()))
        blocked.update(getattr(self, "bombs", {}).keys())
        blocked.update(getattr(self, "ghosts", []))
        blocked.update(getattr(self, "explosions", {}).keys())
        blocked.update(getattr(self, "boss_cells", set()))
        food = getattr(self, "food", None)
        special_food = getattr(self, "special_food", None)
        shield_power = getattr(self, "shield_power", None)
        if food:
            blocked.add(food)
        if special_food:
            blocked.add(special_food)
        if shield_power:
            blocked.add(shield_power)

        return [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in blocked
        ]

    def after_food_eaten(self):
        self.level = 1 + self.score // 5
        self.speed_ms = max(
            self.config["min_speed"],
            self.config["start_speed"] - self.score * SPEED_STEP,
        )
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

    def update_shield_timer(self):
        if self.shield_ticks <= 0:
            return
        self.shield_ticks -= 1
        if self.shield_ticks <= 0:
            self.status_var.set("Escudo terminado")

    def update_extra_life_timer(self):
        if self.extra_life_ticks > 0:
            self.extra_life_ticks -= 1

    def maybe_spawn_shield_power(self):
        if self.shield_power is not None or self.shield_ticks > 0:
            return
        if random.random() > SHIELD_CHANCE:
            return
        available_cells = self.available_cells()
        if available_cells:
            self.shield_power = random.choice(available_cells)
            self.status_var.set("Escudo azul disponible")

    def update_bombs(self):
        expired_bombs = []
        for position in self.bombs:
            self.bombs[position] -= 1
            if self.bombs[position] <= 0:
                expired_bombs.append(position)

        for position in expired_bombs:
            del self.bombs[position]

    def update_explosions(self):
        expired_explosions = []
        for position in self.explosions:
            self.explosions[position] -= 1
            if self.explosions[position] <= 0:
                expired_explosions.append(position)

        for position in expired_explosions:
            del self.explosions[position]

    def update_floating_texts(self):
        active_texts = []
        for text_item in self.floating_texts:
            text_item["ticks"] -= 1
            text_item["offset"] += 1
            if text_item["ticks"] > 0:
                active_texts.append(text_item)
        self.floating_texts = active_texts

    def handle_danger_hit(self, position, hit_bomb, hit_ghost, hit_boss):
        if self.shield_ticks > 0:
            self.clear_danger(position, hit_bomb, hit_ghost, hit_boss)
            self.explosions[position] = EXPLOSION_TICKS
            self.status_var.set("El escudo te salvo")
            self.play_sound("explode")
            return True

        self.lose_life(position, hit_bomb, hit_ghost, hit_boss)
        return False

    def clear_danger(self, position, hit_bomb, hit_ghost, hit_boss):
        if hit_bomb and position in self.bombs:
            del self.bombs[position]
        if hit_ghost and position in self.ghosts:
            self.ghosts.remove(position)
        if hit_boss:
            self.boss_cells.clear()
            self.boss_active = False

    def lose_life(self, position, hit_bomb=False, hit_ghost=False, hit_boss=False):
        self.lives -= 1
        self.clear_danger(position, hit_bomb, hit_ghost, hit_boss)
        self.explosions[position] = EXPLOSION_TICKS
        self.play_sound("hurt")

        if self.lives <= 0:
            self.end_game(exploded=hit_bomb or hit_boss, caught=hit_ghost)
            return

        self.status_var.set(f"Perdiste una vida | Vidas: {self.lives}")
        self.draw()
        self.schedule_tick()

    def update_boss(self):
        elapsed = int(time.monotonic() - self.started_at)
        for boss_time in BOSS_TIMES:
            if elapsed >= boss_time and boss_time not in self.boss_spawned:
                self.spawn_boss(boss_time)
                break

        if not self.boss_active:
            return

        if time.monotonic() - self.boss_started_at >= BOSS_DURATION_SECONDS:
            self.boss_cells.clear()
            self.boss_active = False
            self.play_sound("bonus")
            self.status_var.set("El jefe se fue")
            return

        self.boss_tick += 1
        if self.boss_tick % BOSS_MOVE_EVERY == 0:
            self.move_boss()

    def spawn_boss(self, boss_time):
        self.boss_spawned.add(boss_time)
        self.current_boss_time = boss_time
        self.boss_active = True
        self.boss_started_at = time.monotonic()
        self.boss_tick = 0
        self.boss_cells = self.create_boss_cells()
        if not self.boss_cells:
            self.boss_active = False
            return
        self.status_var.set(f"Jefe de {boss_time} segundos")
        self.play_sound("boss")

    def boss_is_vulnerable(self):
        if not self.boss_active or self.boss_started_at is None:
            return False
        return time.monotonic() - self.boss_started_at >= (
            BOSS_DURATION_SECONDS - BOSS_VULNERABLE_SECONDS
        )

    def eat_boss(self):
        self.score += BOSS_POINTS
        boss_center = self.boss_center()
        self.floating_texts.append(
            {
                "position": boss_center,
                "text": f"+{BOSS_POINTS}",
                "ticks": FLOATING_TEXT_TICKS,
                "offset": 0,
                "color": BOSS_VULNERABLE_EDGE,
            }
        )
        self.boss_cells.clear()
        self.boss_active = False
        self.play_sound("win" if self.current_boss_time == 40 else "bonus")
        self.after_food_eaten()
        if self.current_boss_time == 40:
            self.win_game()
        else:
            self.status_var.set("Te comiste al jefe verde")

    def boss_center(self):
        if not self.boss_cells:
            return self.snake[0]
        x_values = [cell[0] for cell in self.boss_cells]
        y_values = [cell[1] for cell in self.boss_cells]
        return (sum(x_values) / len(x_values), sum(y_values) / len(y_values))

    def create_boss_cells(self):
        head_x, head_y = self.snake[0]
        anchors = [
            (1, 1),
            (GRID_WIDTH - 3, 1),
            (1, GRID_HEIGHT - 3),
            (GRID_WIDTH - 3, GRID_HEIGHT - 3),
        ]
        anchors.sort(key=lambda cell: self.distance(cell, (head_x, head_y)), reverse=True)
        for start_x, start_y in anchors:
            cells = {
                (start_x, start_y),
                (start_x + 1, start_y),
                (start_x, start_y + 1),
                (start_x + 1, start_y + 1),
            }
            if self.can_boss_move_to(cells):
                return cells
        return set()

    def move_boss(self):
        if not self.boss_cells:
            return
        target = self.snake[0]
        anchor = min(self.boss_cells)
        candidates = [
            (anchor[0] + 1, anchor[1]),
            (anchor[0] - 1, anchor[1]),
            (anchor[0], anchor[1] + 1),
            (anchor[0], anchor[1] - 1),
            anchor,
        ]
        candidates.sort(key=lambda cell: self.distance(cell, target))
        for candidate in candidates:
            cells = {
                candidate,
                (candidate[0] + 1, candidate[1]),
                (candidate[0], candidate[1] + 1),
                (candidate[0] + 1, candidate[1] + 1),
            }
            if self.can_boss_move_to(cells):
                self.boss_cells = cells
                return

    def can_boss_move_to(self, cells):
        blocked = set(self.snake[1:])
        blocked.update(self.ghosts)
        blocked.update(cell for cell in [self.food, self.special_food, self.shield_power] if cell is not None)
        for x, y in cells:
            if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
                return False
            if (x, y) in self.obstacles or (x, y) in self.bombs or (x, y) in blocked:
                return False
        return True

    def maybe_spawn_bomb(self):
        if self.score < self.config["bomb_min_score"]:
            return
        if random.random() > self.config["bomb_chance"]:
            return

        head_x, head_y = self.snake[0]
        move_x, move_y = self.direction
        bomb_position = (
            head_x + move_x * BOMB_DISTANCE,
            head_y + move_y * BOMB_DISTANCE,
        )

        if self.can_place_bomb(bomb_position):
            self.bombs[bomb_position] = self.config["bomb_ticks"]
            self.status_var.set("Bomba adelante: cambia de camino")

    def can_place_bomb(self, position):
        x, y = position
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False
        blocked = set(self.snake)
        blocked.update(self.obstacles)
        blocked.update(self.bombs.keys())
        blocked.update(self.ghosts)
        blocked.update(self.explosions.keys())
        blocked.update(cell for cell in [self.food, self.special_food] if cell is not None)
        return position not in blocked

    def update_ghosts(self):
        if not self.ghosts:
            return False
        self.ghost_tick += 1
        if self.ghost_tick % self.config["ghost_move_every"] != 0:
            return self.snake[0] in self.ghosts

        head = self.snake[0]
        snake_body = set(self.snake[1:])
        new_ghosts = []

        for ghost in self.ghosts:
            next_position = self.next_ghost_step(ghost, head, new_ghosts)
            if next_position == head:
                new_ghosts.append(next_position)
            elif next_position in snake_body:
                self.explosions[next_position] = EXPLOSION_TICKS
                self.lives = min(MAX_LIVES, self.lives + 1)
                self.extra_life_ticks = 20
                self.status_var.set("Fantasmita exploto: ganaste una vida")
                self.play_sound("explode")
                self.update_scoreboard()
            else:
                new_ghosts.append(next_position)

        self.ghosts = new_ghosts
        return head in self.ghosts

    def next_ghost_step(self, ghost, target, reserved):
        x, y = ghost
        candidates = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
            ghost,
        ]
        random.shuffle(candidates)
        candidates.sort(key=lambda cell: self.distance(cell, target))

        for candidate in candidates:
            if self.can_ghost_move_to(candidate, reserved):
                return candidate
        return ghost

    def can_ghost_move_to(self, position, reserved):
        x, y = position
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False
        blocked = set(self.obstacles)
        blocked.update(self.bombs.keys())
        blocked.update(reserved)
        return position not in blocked

    def distance(self, first, second):
        return abs(first[0] - second[0]) + abs(first[1] - second[1])

    def update_scoreboard(self):
        record = self.high_scores.get(str(self.selected_level), 0)
        shield = f" | Escudo: {self.shield_ticks}" if self.shield_ticks > 0 else ""
        boss = f" | Boss: {self.boss_timer_text()}"
        self.score_var.set(
            f"v{GAME_VERSION} | Modo {self.selected_level} | P:{self.score} | V:{self.lives} | R:{record}{shield}{boss}"
        )

    def boss_timer_text(self):
        if self.boss_active:
            remaining = max(
                0,
                BOSS_DURATION_SECONDS - int(time.monotonic() - self.boss_started_at),
            )
            state = "verde" if self.boss_is_vulnerable() else "rojo"
            return f"{state} {remaining}s"

        elapsed = int(time.monotonic() - self.started_at)
        for boss_time in BOSS_TIMES:
            if boss_time not in self.boss_spawned:
                return f"{max(0, boss_time - elapsed)}s"
        return "listo"

    def on_key_press(self, event):
        key = event.keysym.lower()
        if self.waiting_for_level:
            if key in {"1", "2", "3"}:
                self.reset(int(key))
            return

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
        elif key == "l":
            self.show_level_menu()
        elif key == "m":
            self.sound_enabled = not self.sound_enabled
            self.status_var.set("Sonidos activados" if self.sound_enabled else "Sonidos silenciados")

    def is_opposite(self, first, second):
        return first[0] + second[0] == 0 and first[1] + second[1] == 0

    def end_game(self, exploded=False, caught=False):
        self.game_over = True
        level_key = str(self.selected_level)
        if self.score > self.high_scores.get(level_key, 0):
            self.high_scores[level_key] = self.score
            self.save_high_scores()
            self.update_scoreboard()
        self.play_sound("lose")
        if exploded:
            self.status_var.set("Boom | Presiona R para reiniciar")
        elif caught:
            self.status_var.set("Te atraparon | Presiona R para reiniciar")
        else:
            self.status_var.set("Fin del juego | Presiona R para reiniciar")
        self.draw()
        title = "BOOM" if exploded else "ATRAPADO" if caught else "GAME OVER"
        self.draw_overlay(
            title,
            f"Puntuacion final: {self.score}",
            "R reinicia | L cambia nivel",
        )

    def win_game(self):
        self.game_over = True
        level_key = str(self.selected_level)
        if self.score > self.high_scores.get(level_key, 0):
            self.high_scores[level_key] = self.score
            self.save_high_scores()
        self.play_sound("win")
        self.status_var.set("Ganaste | Presiona R para reiniciar")
        self.draw()
        self.draw_overlay("GANASTE", "Superaste el reto", "R reinicia | L cambia nivel")

    def draw_level_menu(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.canvas.create_text(
            self.width // 2,
            62,
            text="ELIGE NIVEL",
            fill=TEXT,
            font=("Segoe UI", 28, "bold"),
        )

        level_cards = [
            ("1", "Clasico", "Comida, obstaculos y bombas suaves"),
            ("2", "Persecucion", "Un fantasmita lento te sigue"),
            ("3", "Caos", "Dos fantasmitas y bombas mas bravas"),
        ]
        card_width = 420
        card_height = 72
        start_y = 122

        for index, (number, title, description) in enumerate(level_cards):
            y = start_y + index * 92
            left = (self.width - card_width) // 2
            right = left + card_width
            self.canvas.create_rectangle(
                left,
                y,
                right,
                y + card_height,
                fill="#020617",
                outline=GRID_LINE,
                width=2,
            )
            self.canvas.create_text(
                left + 34,
                y + card_height // 2,
                text=number,
                fill=SPECIAL_FOOD,
                font=("Segoe UI", 24, "bold"),
            )
            self.canvas.create_text(
                left + 88,
                y + 24,
                text=title,
                anchor="w",
                fill=TEXT,
                font=("Segoe UI", 15, "bold"),
            )
            self.canvas.create_text(
                left + 88,
                y + 49,
                text=f"{description} | Record: {self.high_scores.get(number, 0)}",
                anchor="w",
                fill=MUTED_TEXT,
                font=("Segoe UI", 10),
            )

        self.canvas.create_text(
            self.width // 2,
            self.height - 34,
            text="Presiona 1, 2 o 3 para empezar",
            fill=MUTED_TEXT,
            font=("Segoe UI", 12, "bold"),
        )

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

        for bomb_position, ticks_left in self.bombs.items():
            self.draw_bomb(bomb_position, ticks_left)

        for explosion_position, ticks_left in self.explosions.items():
            self.draw_explosion(explosion_position, ticks_left)

        for text_item in self.floating_texts:
            self.draw_floating_text(text_item)

        boss_color = BOSS_VULNERABLE if self.boss_is_vulnerable() else BOSS
        boss_outline = BOSS_VULNERABLE_EDGE if self.boss_is_vulnerable() else BOSS_EDGE
        for boss_cell in self.boss_cells:
            self.draw_cell(boss_cell, boss_color, outline=boss_outline)

        for index, ghost in enumerate(self.ghosts):
            self.draw_ghost(ghost, index)

        if self.food is not None:
            self.draw_cell(self.food, FOOD, rounded=True)

        if self.special_food is not None:
            self.draw_cell(self.special_food, SPECIAL_FOOD, rounded=True)

        if self.shield_power is not None:
            self.draw_shield_power(self.shield_power)

        for index, segment in enumerate(self.snake):
            color = SNAKE_HEAD if index == 0 else SNAKE_BODY
            self.draw_cell(segment, color)

        if self.shield_ticks > 0:
            self.draw_active_shield()

        if self.extra_life_ticks > 0:
            self.draw_extra_life_hint()

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

    def draw_bomb(self, position, ticks_left):
        x, y = position
        padding = 3
        left = x * CELL_SIZE + padding
        top = y * CELL_SIZE + padding
        right = (x + 1) * CELL_SIZE - padding
        bottom = (y + 1) * CELL_SIZE - padding
        center_x = x * CELL_SIZE + CELL_SIZE // 2
        center_y = y * CELL_SIZE + CELL_SIZE // 2

        self.canvas.create_oval(left, top + 3, right, bottom, fill=BOMB, outline=BOMB_FUSE, width=2)
        self.canvas.create_line(center_x, top + 3, center_x + 6, top - 2, fill=BOMB_FUSE, width=2)
        self.canvas.create_text(
            center_x,
            center_y + 1,
            text=str(max(1, ticks_left)),
            fill=BOMB_TEXT,
            font=("Segoe UI", 8, "bold"),
        )

    def draw_explosion(self, position, ticks_left):
        x, y = position
        center_x = x * CELL_SIZE + CELL_SIZE // 2
        center_y = y * CELL_SIZE + CELL_SIZE // 2
        radius = 5 + ticks_left * 2

        self.canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill=EXPLOSION,
            outline="",
        )
        self.canvas.create_oval(
            center_x - radius // 2,
            center_y - radius // 2,
            center_x + radius // 2,
            center_y + radius // 2,
            fill=EXPLOSION_CORE,
            outline="",
        )

    def draw_shield_power(self, position):
        x, y = position
        padding = 4
        left = x * CELL_SIZE + padding
        top = y * CELL_SIZE + padding
        right = (x + 1) * CELL_SIZE - padding
        bottom = (y + 1) * CELL_SIZE - padding
        self.canvas.create_oval(left, top, right, bottom, fill=SHIELD_POWER, outline=SHIELD_RING, width=2)
        self.canvas.create_text(
            x * CELL_SIZE + CELL_SIZE // 2,
            y * CELL_SIZE + CELL_SIZE // 2,
            text="S",
            fill=BACKGROUND,
            font=("Segoe UI", 10, "bold"),
        )

    def draw_active_shield(self):
        head_x, head_y = self.snake[0]
        center_x = head_x * CELL_SIZE + CELL_SIZE // 2
        center_y = head_y * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 2 + 5
        self.canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            outline=SHIELD_RING,
            width=3,
        )

    def draw_extra_life_hint(self):
        head_x, head_y = self.snake[0]
        move_x, move_y = self.direction
        hint_position = (head_x + move_x, head_y + move_y)
        x, y = hint_position
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return
        padding = 5
        left = x * CELL_SIZE + padding
        top = y * CELL_SIZE + padding
        right = (x + 1) * CELL_SIZE - padding
        bottom = (y + 1) * CELL_SIZE - padding
        self.canvas.create_oval(left, top, right, bottom, fill=GHOST, outline=GHOST_EYE, width=2)
        self.canvas.create_text(
            x * CELL_SIZE + CELL_SIZE // 2,
            y * CELL_SIZE + CELL_SIZE // 2,
            text="+1",
            fill=TEXT,
            font=("Segoe UI", 9, "bold"),
        )

    def draw_floating_text(self, text_item):
        x, y = text_item["position"]
        center_x = x * CELL_SIZE + CELL_SIZE // 2
        center_y = y * CELL_SIZE + CELL_SIZE // 2 - text_item["offset"]
        self.canvas.create_text(
            center_x,
            center_y,
            text=text_item["text"],
            fill=text_item["color"],
            font=("Segoe UI", 16, "bold"),
        )

    def draw_ghost(self, position, index):
        x, y = position
        padding = 3
        left = x * CELL_SIZE + padding
        top = y * CELL_SIZE + padding
        right = (x + 1) * CELL_SIZE - padding
        bottom = (y + 1) * CELL_SIZE - padding
        color = GHOST if index % 2 == 0 else GHOST_DARK

        self.canvas.create_arc(left, top, right, bottom + 8, start=0, extent=180, fill=color, outline="")
        self.canvas.create_rectangle(left, top + CELL_SIZE // 2 - 2, right, bottom, fill=color, outline="")
        for wave in range(3):
            wave_left = left + wave * 6
            self.canvas.create_oval(wave_left, bottom - 4, wave_left + 8, bottom + 4, fill=color, outline="")
        self.canvas.create_oval(left + 5, top + 7, left + 9, top + 11, fill=GHOST_EYE, outline="")
        self.canvas.create_oval(right - 9, top + 7, right - 5, top + 11, fill=GHOST_EYE, outline="")

    def load_high_scores(self):
        default_scores = {"1": 0, "2": 0, "3": 0}
        try:
            with HIGH_SCORE_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
                if "high_scores" in data:
                    scores = data["high_scores"]
                else:
                    scores = {"1": int(data.get("high_score", 0)), "2": 0, "3": 0}
                default_scores.update({str(key): int(value) for key, value in scores.items()})
                return default_scores
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            return default_scores

    def save_high_scores(self):
        with HIGH_SCORE_FILE.open("w", encoding="utf-8") as file:
            json.dump({"high_scores": self.high_scores}, file)

    def play_sound(self, sound_name):
        if not self.sound_enabled:
            return
        sounds = {
            "eat": (880, 55),
            "bonus": (1175, 90),
            "shield": (660, 120),
            "explode": (220, 130),
            "hurt": (160, 170),
            "lose": (120, 260),
            "win": (988, 180),
            "boss": (330, 180),
        }
        frequency, duration = sounds.get(sound_name, (440, 60))
        try:
            winsound.Beep(frequency, duration)
        except RuntimeError:
            pass


def main():
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
