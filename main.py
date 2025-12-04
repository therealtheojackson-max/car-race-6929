import pygame
import random
import sys
import os
import socket
import threading
import json
import time

# Top-down car racer with cities, islands, and ferry transport

WIDTH, HEIGHT = 1000, 700
FPS = 60

# Allow environment overrides for width/height. Useful when launching on Switchroot
# Example: export SWITCH_GAME_WIDTH=800 SWITCH_GAME_HEIGHT=600
try:
    env_w = os.environ.get('SWITCH_GAME_WIDTH') or os.environ.get('GAME_WIDTH')
    env_h = os.environ.get('SWITCH_GAME_HEIGHT') or os.environ.get('GAME_HEIGHT')
    if env_w:
        WIDTH = int(env_w)
    if env_h:
        HEIGHT = int(env_h)
except Exception:
    # If parsing fails, fall back to defaults
    pass

# Device detection
IS_MOBILE = HEIGHT < 800 or WIDTH < 1000  # Small screen = mobile
BUTTON_SIZE = 60
BUTTON_PADDING = 10

# Colors
PLAYER_COLOR = (50, 200, 50)
NPC_COLOR = (200, 50, 50)
ROAD_COLOR = (80, 80, 80)
LINE_COLOR = (255, 255, 150)
WATER_COLOR = (30, 100, 200)
FERRY_COLOR = (150, 200, 100)
BUILDING_COLOR1 = (200, 100, 50)
BUILDING_COLOR2 = (100, 150, 200)
BUILDING_COLOR3 = (180, 80, 100)
GRASS_COLOR = (60, 150, 80)
BUTTON_COLOR = (100, 100, 150)
BUTTON_HOVER_COLOR = (150, 150, 200)
GARAGE_COLOR = (120, 80, 40)

# Car models available for purchase
CAR_MODELS = [
    {'name': 'Sport Sedan', 'price': 500, 'speed_bonus': 2, 'acc_bonus': 0.1},
    {'name': 'Racing Car', 'price': 1000, 'speed_bonus': 4, 'acc_bonus': 0.2},
    {'name': 'Supercar', 'price': 2000, 'speed_bonus': 6, 'acc_bonus': 0.3},
    {'name': 'Hypercar', 'price': 5000, 'speed_bonus': 10, 'acc_bonus': 0.5},
]

# Decoration items available for purchase
DECORATIONS = [
    {'name': 'Lamp', 'price': 50, 'color': (255, 255, 100)},
    {'name': 'Plant', 'price': 75, 'color': (100, 200, 100)},
    {'name': 'Painting', 'price': 100, 'color': (255, 100, 150)},
    {'name': 'Sofa', 'price': 150, 'color': (200, 100, 50)},
    {'name': 'Table', 'price': 120, 'color': (180, 120, 60)},
    {'name': 'Statue', 'price': 200, 'color': (150, 150, 150)},
]

# House upgrade tiers
HOUSE_TIERS = [
    {'name': 'Small House', 'price': 0, 'size': 120, 'capacity': 3},  # Starting house
    {'name': 'Medium House', 'price': 1000, 'size': 180, 'capacity': 6},
    {'name': 'Large House', 'price': 3000, 'size': 250, 'capacity': 12},
    {'name': 'Mansion', 'price': 8000, 'size': 320, 'capacity': 20},
]

# Island definitions
ISLANDS = [
    {'name': 'Downtown', 'id': 0, 'x': 100, 'y': 100, 'width': 200, 'height': 200},
    {'name': 'Harbor', 'id': 1, 'x': 450, 'y': 100, 'width': 200, 'height': 200},
    {'name': 'Uptown', 'id': 2, 'x': 100, 'y': 400, 'width': 200, 'height': 200},
    {'name': 'Industrial', 'id': 3, 'x': 450, 'y': 400, 'width': 200, 'height': 200},
]

# Ferry routes between islands
FERRY_ROUTES = [
    (0, 1),  # Downtown <-> Harbor
    (0, 2),  # Downtown <-> Uptown
    (1, 3),  # Harbor <-> Industrial
    (2, 3),  # Uptown <-> Industrial
]

# Racing difficulty levels
RACE_DIFFICULTIES = [
    {'name': 'Beginner', 'opponent_speed_mult': 0.8, 'prize': 200},  # NPC at 80% max speed
    {'name': 'Intermediate', 'opponent_speed_mult': 1.0, 'prize': 400},  # NPC at full speed
    {'name': 'Expert', 'opponent_speed_mult': 1.2, 'prize': 800},  # NPC at 120% speed
    {'name': 'Master', 'opponent_speed_mult': 1.5, 'prize': 1500},  # NPC at 150% speed
]

# NPC collision tuning defaults (can be adjusted in-game with T)
NPC_COLLISION_KNOCKBACK = 30
NPC_COLLISION_SLOW = 4
NPC_COLLISION_SCORE_PENALTY = 20
NPC_COLLISION_COOLDOWN = 1.0


class Car:
    def __init__(self, x, y, width=40, height=70, color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.centerx = x
        self.rect.centery = y
        self.color = color
        self.speed = 0

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=6)


class Button:
    """On-screen button for mobile controls"""
    def __init__(self, x, y, width, height, label, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.action = action
        self.pressed = False
        self.color = BUTTON_COLOR

    def draw(self, surf):
        color = BUTTON_HOVER_COLOR if self.pressed else self.color
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        pygame.draw.rect(surf, (255, 255, 255), self.rect, 2, border_radius=8)
        
        # Draw label
        font = pygame.font.SysFont("Arial", 16, bold=True)
        text = font.render(self.label, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surf.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False

    def is_pressed(self):
        return self.pressed


class GamepadHandler:
    """Handles Nintendo Switch and console controller input"""
    def __init__(self):
        pygame.joystick.init()
        self.joysticks = []
        self.gamepad = None
        self.detect_gamepads()
        # Deadzone for analog sticks (0-1)
        self.deadzone = 0.3
        # Button mappings for common controllers
        self.buttons = {
            'a': 0,       # A button (confirm)
            'b': 1,       # B button (cancel)
            'x': 2,       # X button
            'y': 3,       # Y button
            'lb': 4,      # LB button
            'rb': 5,      # RB button
            'back': 6,    # Back/Select button
            'start': 7,   # Start button
            'stick_left': 8,
            'stick_right': 9,
        }
        # Axes (analog sticks and triggers)
        self.axes = {
            'left_stick_x': 0,
            'left_stick_y': 1,
            'right_stick_x': 2,
            'right_stick_y': 3,
            'lt': 4,      # Left trigger
            'rt': 5,      # Right trigger
        }
        # D-pad axes (some controllers use hat)
        self.hat = 0  # Hat index for d-pad
        self.prev_buttons = {}
        
    def detect_gamepads(self):
        """Detect connected gamepads/joysticks"""
        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            print(f"Gamepad detected: {self.gamepad.get_name()}")
            return True
        print("No gamepad detected. Using keyboard.")
        return False
    
    def is_connected(self):
        """Check if a gamepad is currently connected"""
        return self.gamepad is not None
    
    def get_stick_input(self):
        """Get left analog stick input (x, y)
        Returns: (x, y) tuple with values -1 to 1, 0 if in deadzone
        """
        if not self.is_connected():
            return (0, 0)
        
        x = self.gamepad.get_axis(self.axes['left_stick_x'])
        y = self.gamepad.get_axis(self.axes['left_stick_y'])
        
        # Apply deadzone
        if abs(x) < self.deadzone:
            x = 0
        if abs(y) < self.deadzone:
            y = 0
        
        return (x, y)
    
    def get_dpad(self):
        """Get D-pad input (up, down, left, right)
        Returns: tuple of (up, down, left, right) booleans
        """
        if not self.is_connected():
            return (False, False, False, False)
        
        # Method 1: Hat (most common for D-pad)
        if self.gamepad.get_numhats() > 0:
            hat = self.gamepad.get_hat(self.hat)
            # hat returns (-1, 0, or 1, -1, 0, or 1)
            # (0, 1) = up, (0, -1) = down, (-1, 0) = left, (1, 0) = right
            return (
                hat[1] == 1,  # up
                hat[1] == -1,  # down
                hat[0] == -1,  # left
                hat[0] == 1    # right
            )
        return (False, False, False, False)
    
    def is_button_pressed(self, button_name):
        """Check if a button is pressed"""
        if not self.is_connected():
            return False
        if button_name not in self.buttons:
            return False
        return self.gamepad.get_button(self.buttons[button_name])
    
    def was_button_pressed(self, button_name):
        """Check if button was just pressed (not held)"""
        if not self.is_connected():
            return False
        current = self.is_button_pressed(button_name)
        previous = self.prev_buttons.get(button_name, False)
        self.prev_buttons[button_name] = current
        return current and not previous
    
    def get_trigger_input(self):
        """Get trigger inputs (LT, RT)
        Returns: (lt, rt) tuple with values 0 to 1
        """
        if not self.is_connected():
            return (0, 0)
        
        lt = max(0, self.gamepad.get_axis(self.axes['lt']))
        rt = max(0, self.gamepad.get_axis(self.axes['rt']))
        return (lt, rt)
    
    def update(self):
        """Update gamepad state (call once per frame)"""
        # Re-detect if gamepad was disconnected
        if self.gamepad:
            try:
                self.gamepad.get_name()  # Test if still connected
            except:
                print("Gamepad disconnected!")
                self.gamepad = None
                self.detect_gamepads()


class PlayerCar(Car):
    def __init__(self, x, y):
        super().__init__(x, y, color=PLAYER_COLOR)
        self.max_speed = 8
        self.acc = 0.4
        self.friction = 0.2
        self.current_island = 0
        self.currency = 500  # Starting money for home/decoration
        self.car_model = None  # Current car model (None = default)
        self.home = Home(self)  # Player's home with decorations
        self.decoration_inventory = []  # Decorations player has bought

    def update(self, keys, buttons=None, gamepad=None):
        # Vertical control (keyboard or buttons or gamepad)
        going_up = keys[pygame.K_w] or (buttons and buttons['up'].is_pressed())
        going_down = keys[pygame.K_s] or (buttons and buttons['down'].is_pressed())
        
        # Add gamepad stick input
        if gamepad and gamepad.is_connected():
            stick_x, stick_y = gamepad.get_stick_input()
            # Negative Y = up, positive Y = down
            if stick_y < -0.5:
                going_up = True
            elif stick_y > 0.5:
                going_down = True
        
        if going_up:
            self.speed = min(self.max_speed, self.speed + self.acc)
        elif going_down:
            self.speed = max(-2, self.speed - self.acc)
        else:
            # friction
            if self.speed > 0:
                self.speed = max(0, self.speed - self.friction)
            elif self.speed < 0:
                self.speed = min(0, self.speed + self.friction)

        # Horizontal control (keyboard or buttons or gamepad)
        going_left = keys[pygame.K_a] or (buttons and buttons['left'].is_pressed())
        going_right = keys[pygame.K_d] or (buttons and buttons['right'].is_pressed())
        
        # Add gamepad stick input
        if gamepad and gamepad.is_connected():
            stick_x, stick_y = gamepad.get_stick_input()
            if stick_x < -0.5:
                going_left = True
            elif stick_x > 0.5:
                going_right = True
        
        if going_left:
            self.rect.x -= 6
        if going_right:
            self.rect.x += 6

        # Keep within island bounds
        island = ISLANDS_OBJ[self.current_island]
        self.rect.x = max(island.x, min(island.x + island.width - self.width, self.rect.x))
        self.rect.y = max(island.y, min(island.y + island.height - self.height, self.rect.y))

    def move(self):
        self.rect.y -= int(self.speed)
    
    def buy_car(self, car_model):
        """Purchase a car model if player has enough currency"""
        if self.currency >= car_model['price']:
            self.currency -= car_model['price']
            self.car_model = car_model
            # Apply car bonuses
            self.max_speed += car_model['speed_bonus']

    def buy_decoration(self, decoration):
        """Purchase a decoration if player has enough currency"""
        if self.currency >= decoration['price']:
            self.currency -= decoration['price']
            self.decoration_inventory.append(decoration)
            return True
        return False

    def buy_house_upgrade(self):
        """Upgrade house to next tier if possible"""
        return self.home.upgrade()


class TrackBlock:
    """A single block that can be placed to build a track."""
    TYPES = {
        'straight': {'color': (200, 200, 200)},
        'curve': {'color': (180, 180, 255)},
        'start': {'color': (50, 200, 50)},
        'finish': {'color': (200, 50, 50)},
        'boost': {'color': (255, 200, 0)},
        'obstacle': {'color': (120, 60, 60)},
    }

    SIZE = 40  # block size in pixels

    def __init__(self, x, y, btype='straight', rotation=0):
        self.x = x
        self.y = y
        self.type = btype
        self.rotation = rotation  # degrees: 0, 90, 180, 270
        self.last_trigger = 0

    def rect(self):
        return pygame.Rect(self.x - TrackBlock.SIZE//2, self.y - TrackBlock.SIZE//2,
                           TrackBlock.SIZE, TrackBlock.SIZE)

    def draw(self, surf):
        col = TrackBlock.TYPES.get(self.type, {}).get('color', (200,200,200))
        r = self.rect()
        pygame.draw.rect(surf, col, r)
        # draw border
        pygame.draw.rect(surf, (0,0,0), r, 2)
        # draw type letter
        font = pygame.font.SysFont(None, 18)
        text = font.render(self.type[0].upper(), True, (0,0,0))
        surf.blit(text, (self.x - 6, self.y - 8))

    def to_dict(self):
        return {'x': self.x, 'y': self.y, 'type': self.type, 'rotation': self.rotation}

    @staticmethod
    def from_dict(d):
        return TrackBlock(d['x'], d['y'], d.get('type','straight'), d.get('rotation',0))


class TrackEditor:
    """Simple track editor to place blocks and save/load tracks."""
    BLOCK_ORDER = ['straight','curve','start','finish','boost','obstacle']

    def __init__(self):
        self.blocks = []
        self.selected_index = 0
        self.grid = 10
        self.show_grid = True
        # cursor for gamepad editing
        self.cursor_x = WIDTH // 2
        self.cursor_y = HEIGHT // 2
        self.cursor_speed = 300  # pixels per second
        self.prev_dpad = (False, False, False, False)

    def snap(self, x, y):
        gx = (x // self.grid) * self.grid + self.grid//2
        gy = (y // self.grid) * self.grid + self.grid//2
        return gx, gy

    def place_block(self, x, y):
        gx, gy = self.snap(x,y)
        # prevent duplicate same-type at same spot
        for b in self.blocks:
            if b.x==gx and b.y==gy and b.type==self.BLOCK_ORDER[self.selected_index]:
                return
        b = TrackBlock(gx, gy, self.BLOCK_ORDER[self.selected_index])
        self.blocks.append(b)

    def remove_block_at(self, x, y):
        gx, gy = self.snap(x,y)
        for i, b in enumerate(self.blocks):
            if b.x==gx and b.y==gy:
                self.blocks.pop(i)
                return

    def rotate_block_at(self, x, y):
        gx, gy = self.snap(x,y)
        for b in self.blocks:
            if b.x==gx and b.y==gy:
                b.rotation = (b.rotation + 90) % 360
                return

    def save(self, filename='tracks.json'):
        data = [b.to_dict() for b in self.blocks]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, filename='tracks.json'):
        if not os.path.exists(filename):
            return
        with open(filename, 'r') as f:
            data = json.load(f)
        self.blocks = [TrackBlock.from_dict(d) for d in data]

    def draw(self, surf):
        if self.show_grid:
            for x in range(0, WIDTH, self.grid):
                pygame.draw.line(surf, (40,40,40), (x,0),(x,HEIGHT),1)
            for y in range(0, HEIGHT, self.grid):
                pygame.draw.line(surf, (40,40,40), (0,y),(WIDTH,y),1)

        # draw blocks
        for b in self.blocks:
            b.draw(surf)

        # UI overlay
        font = pygame.font.SysFont(None, 20)
        info = [
            f"TRACK EDITOR - Press E to exit",
            f"Selected: {self.BLOCK_ORDER[self.selected_index]} (1-{len(self.BLOCK_ORDER)})",
            "Left-click: place, Right-click: remove, R: rotate",
            "S: save, L: load, G: toggle grid"
        ]
        y = 8
        for line in info:
            txt = font.render(line, True, (255,255,255))
            surf.blit(txt, (8, y))
            y += 20
        # draw cursor for gamepad
        try:
            cx = int(self.cursor_x)
            cy = int(self.cursor_y)
            pygame.draw.circle(surf, (255,255,255), (cx, cy), 6, 2)
            pygame.draw.line(surf, (255,255,255), (cx-10, cy), (cx+10, cy), 1)
            pygame.draw.line(surf, (255,255,255), (cx, cy-10), (cx, cy+10), 1)
            coord_txt = font.render(f"{cx},{cy}", True, (200,200,200))
            surf.blit(coord_txt, (cx + 10, cy + 10))
        except Exception:
            pass


class HitEffect:
    """Simple visual effect for collisions"""
    def __init__(self, x, y, duration=0.6):
        self.x = x
        self.y = y
        self.duration = duration
        self.start = time.time()

    def draw(self, surf):
        t = (time.time() - self.start) / self.duration
        if t >= 1.0:
            return False
        # expanding circle with fading alpha
        radius = int(10 + t * 60)
        alpha = max(0, int(180 * (1 - t)))
        s = pygame.Surface((radius*2+4, radius*2+4), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 0, 0, alpha), (radius+2, radius+2), radius, 3)
        surf.blit(s, (int(self.x - radius - 2), int(self.y - radius - 2)))
        return True


class NPCCar(Car):
    def __init__(self, x, y, speed, island_id):
        super().__init__(x, y, color=NPC_COLOR)
        self.normal_speed = speed  # Normal driving speed (slow)
        self.speed = speed
        self.island_id = island_id
        self.in_race = False  # Whether currently racing player
        self.race_speed = speed  # Speed while racing (boosted)
        self.last_collision_time = 0

    def update(self):
        # NPCs move downward (toward the player)
        self.rect.y += int(self.speed)
    
    def set_race_mode(self, enabled, difficulty_level=0):
        """Enable race mode with boosted speed"""
        self.in_race = enabled
        if enabled:
            difficulty = RACE_DIFFICULTIES[min(difficulty_level, len(RACE_DIFFICULTIES) - 1)]
            self.race_speed = self.normal_speed * difficulty['opponent_speed_mult']
            self.speed = self.race_speed
        else:
            self.speed = self.normal_speed


class Race:
    """Active race between player and an NPC"""
    def __init__(self, npc, difficulty_level=0):
        self.npc = npc
        self.difficulty_level = min(difficulty_level, len(RACE_DIFFICULTIES) - 1)
        self.difficulty = RACE_DIFFICULTIES[self.difficulty_level]
        self.prize_money = self.difficulty['prize']
        self.start_y = npc.rect.y
        self.player_progress = 0
        self.npc_progress = 0
        self.finished = False
        self.won = False
        
        # Start race mode for NPC
        self.npc.set_race_mode(True, self.difficulty_level)

    def update(self, player_rect, player_speed):
        """Update race progress"""
        if self.finished:
            return
        
        # Track distance traveled (upward)
        self.player_progress -= player_speed  # Negative because moving up decreases y
        self.npc_progress -= self.npc.speed   # Same for NPC
        
        # Finish line at 500 pixels traveled
        finish_distance = 500
        
        if self.player_progress >= finish_distance:
            self.finished = True
            self.won = True
        elif self.npc_progress >= finish_distance:
            self.finished = True
            self.won = False

    def get_display_progress(self):
        """Get progress as percentage for HUD"""
        player_pct = min(100, int((self.player_progress / 500) * 100))
        npc_pct = min(100, int((self.npc_progress / 500) * 100))
        return player_pct, npc_pct


class ChatClient:
    """Simple TCP chat client with authentication support"""
    def __init__(self, host='127.0.0.1', port=50007):
        self.host = host
        self.port = port
        self.username = None
        self.sock = None
        self.listener = None
        self.running = False
        self.inbox = []  # list of received chat/system lines
        self.auth_state = None  # 'need_auth', 'authenticated', 'error'

    def register(self, username, password, timeout=3):
        """Register a new account"""
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
            # Receive auth_required
            data = self.sock.recv(1024).decode('utf-8')
            
            # Send registration
            reg = {'type': 'register', 'username': username, 'password': password}
            self.sock.sendall((json.dumps(reg) + "\n").encode('utf-8'))
            
            # Get response
            response = self.sock.recv(1024).decode('utf-8')
            msg = json.loads(response)
            if msg.get('success'):
                self.username = username
                self.auth_state = 'authenticated'
                # Start listener
                self.running = True
                self.listener = threading.Thread(target=self._listen, daemon=True)
                self.listener.start()
                return True, "Account created"
            else:
                self.auth_state = 'error'
                return False, msg.get('message', 'Registration failed')
        except Exception as e:
            self.auth_state = 'error'
            return False, str(e)

    def login(self, username, password, timeout=3):
        """Login to an existing account"""
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
            # Receive auth_required
            data = self.sock.recv(1024).decode('utf-8')
            
            # Send login
            login_msg = {'type': 'login', 'username': username, 'password': password}
            self.sock.sendall((json.dumps(login_msg) + "\n").encode('utf-8'))
            
            # Get response
            response = self.sock.recv(1024).decode('utf-8')
            msg = json.loads(response)
            if msg.get('success'):
                self.username = username
                self.auth_state = 'authenticated'
                # Start listener
                self.running = True
                self.listener = threading.Thread(target=self._listen, daemon=True)
                self.listener.start()
                return True, "Logged in"
            else:
                self.auth_state = 'error'
                return False, msg.get('message', 'Login failed')
        except Exception as e:
            self.auth_state = 'error'
            return False, str(e)

    def connect(self):
        """Connect to chat after authentication (requires join message)"""
        if not self.sock or not self.username or self.auth_state != 'authenticated':
            return False
        try:
            join = {'type': 'join', 'username': self.username}
            self.sock.sendall((json.dumps(join) + "\n").encode('utf-8'))
            return True
        except Exception:
            return False

    def _listen(self):
        buf = b''
        try:
            while self.running and self.sock:
                data = self.sock.recv(4096)
                if not data:
                    break
                buf += data
                while b'\n' in buf:
                    line, buf = buf.split(b'\n', 1)
                    try:
                        msg = json.loads(line.decode('utf-8'))
                        self.inbox.append(msg)
                    except Exception:
                        continue
        except Exception:
            pass
        finally:
            self.running = False

    def send_message(self, text):
        if not self.sock or not self.username:
            return False
        try:
            msg = {'type': 'msg', 'username': self.username, 'text': text}
            self.sock.sendall((json.dumps(msg) + "\n").encode('utf-8'))
            return True
        except Exception:
            return False

    def close(self):
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        self.sock = None
        self.username = None
    
    


class Ferry:
    def __init__(self, island_from, island_to):
        self.from_island = island_from
        self.to_island = island_to
        self.width = 80
        self.height = 50
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.color = FERRY_COLOR
        
        # Position ferry near the island
        island = ISLANDS[island_from]
        self.rect.centerx = island['x'] + island['width'] // 2
        self.rect.centery = island['y'] + island['height'] // 2

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=8)
        # Draw portholes
        pygame.draw.circle(surf, (50, 100, 150), (self.rect.centerx - 15, self.rect.centery), 5)
        pygame.draw.circle(surf, (50, 100, 150), (self.rect.centerx + 15, self.rect.centery), 5)


class Building:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)
        # Draw windows
        for wx in range(self.rect.x + 5, self.rect.x + self.rect.width - 5, 15):
            for wy in range(self.rect.y + 5, self.rect.y + self.rect.height - 5, 15):
                pygame.draw.rect(surf, (255, 255, 100), pygame.Rect(wx, wy, 8, 8))


class Garage:
    """Garage building where player can buy cars"""
    def __init__(self, x, y, garage_id):
        self.rect = pygame.Rect(x, y, 60, 50)
        self.color = GARAGE_COLOR
        self.garage_id = garage_id
        self.name = f"Garage {garage_id + 1}"

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)
        pygame.draw.rect(surf, (255, 200, 0), self.rect, 2)  # Gold border
        
        # Draw garage door indicator
        pygame.draw.rect(surf, (80, 50, 20), pygame.Rect(self.rect.x + 5, self.rect.y + 5, 50, 40))


class DecorationShop:
    """Shop building where player can buy decorations for home"""
    def __init__(self, x, y, shop_id):
        self.rect = pygame.Rect(x, y, 60, 50)
        self.color = (200, 150, 100)
        self.shop_id = shop_id
        self.name = f"Decor Shop {shop_id + 1}"

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)
        pygame.draw.rect(surf, (200, 100, 200), self.rect, 2)  # Purple border
        
        # Draw shop window
        pygame.draw.rect(surf, (100, 100, 200), pygame.Rect(self.rect.x + 5, self.rect.y + 5, 50, 40))


class Video:
    """Represents a recorded video"""
    def __init__(self, title="Video", duration=0, timestamp=None):
        self.title = title
        self.duration = duration  # in seconds
        self.timestamp = timestamp or time.time()
        self.views = 0
        self.likes = 0
        self.description = ""

    def to_dict(self):
        return {
            'title': self.title,
            'duration': self.duration,
            'timestamp': self.timestamp,
            'views': self.views,
            'likes': self.likes,
            'description': self.description
        }

    @staticmethod
    def from_dict(data):
        v = Video(data.get('title', 'Video'), data.get('duration', 0), data.get('timestamp'))
        v.views = data.get('views', 0)
        v.likes = data.get('likes', 0)
        v.description = data.get('description', '')
        return v


class VideoLibrary:
    """Manages recorded videos"""
    def __init__(self, player):
        self.player = player
        self.videos = []
        self.load_videos()

    def add_video(self, title, duration):
        """Add a new recorded video"""
        video = Video(title, duration)
        self.videos.append(video)
        self.save_videos()
        return video

    def upload_video(self, video_index, title="", description=""):
        """Upload video and earn currency from views"""
        if 0 <= video_index < len(self.videos):
            video = self.videos[video_index]
            if title:
                video.title = title
            if description:
                video.description = description
            # Earn currency based on video duration (10 currency per minute)
            earnings = max(50, int(video.duration / 60 * 10))
            video.views = random.randint(10, 500)  # Random views
            video.likes = random.randint(0, video.views // 3)
            self.player.currency += earnings
            self.save_videos()
            return earnings
        return 0

    def delete_video(self, video_index):
        """Delete a video from library"""
        if 0 <= video_index < len(self.videos):
            self.videos.pop(video_index)
            self.save_videos()
            return True
        return False

    def save_videos(self):
        """Save videos to file"""
        try:
            videos_data = [v.to_dict() for v in self.videos]
            with open('videos.json', 'w', encoding='utf-8') as f:
                json.dump(videos_data, f, indent=2)
        except Exception:
            pass

    def load_videos(self):
        """Load videos from file"""
        try:
            if os.path.exists('videos.json'):
                with open('videos.json', 'r', encoding='utf-8') as f:
                    videos_data = json.load(f)
                    self.videos = [Video.from_dict(v) for v in videos_data]
        except Exception:
            pass


class Computer:
    """Computer system in home for recording and uploading videos"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 50)
        self.desk_rect = pygame.Rect(x - 10, y + 30, 80, 20)  # Desk below computer
        self.is_recording = False
        self.recording_start = 0

    def start_recording(self):
        """Start recording a video"""
        self.is_recording = True
        self.recording_start = time.time()

    def stop_recording(self):
        """Stop recording and return duration"""
        if self.is_recording:
            duration = time.time() - self.recording_start
            self.is_recording = False
            return duration
        return 0

    def draw(self, surf):
        """Draw computer and desk"""
        # Draw desk
        pygame.draw.rect(surf, (139, 90, 43), self.desk_rect)  # Brown desk
        pygame.draw.rect(surf, (100, 60, 20), self.desk_rect, 2)  # Dark border
        
        # Draw computer monitor
        pygame.draw.rect(surf, (50, 50, 50), self.rect)  # Monitor
        pygame.draw.rect(surf, (100, 200, 100), pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height - 15))  # Screen
        
        # Draw screen content - recording indicator if active
        if self.is_recording:
            pygame.draw.circle(surf, (255, 0, 0), (self.rect.centerx, self.rect.centery), 5)  # Red recording dot


class Home:
    """Player's home where decorations can be placed and computer is used"""
    def __init__(self, player):
        self.player = player
        self.house_tier = 0  # 0 = Small, 1 = Medium, 2 = Large, 3 = Mansion
        self.decorations = []  # List of {'decoration': {...}, 'x': x, 'y': y}
        self.x = WIDTH // 2 - HOUSE_TIERS[0]['size'] // 2
        self.y = HEIGHT // 2 - HOUSE_TIERS[0]['size'] // 2
        # Add computer in corner of home
        self.computer = Computer(self.x + 80, self.y + 30)
        self.video_library = VideoLibrary(player)

    def get_current_tier(self):
        return HOUSE_TIERS[self.house_tier]

    def get_current_size(self):
        return self.get_current_tier()['size']

    def can_upgrade(self):
        """Check if can upgrade to next tier"""
        if self.house_tier < len(HOUSE_TIERS) - 1:
            next_tier = HOUSE_TIERS[self.house_tier + 1]
            return self.player.currency >= next_tier['price']
        return False

    def upgrade(self):
        """Upgrade to next house tier"""
        if self.can_upgrade():
            next_tier = HOUSE_TIERS[self.house_tier + 1]
            self.player.currency -= next_tier['price']
            self.house_tier += 1
            # Re-center house
            self.x = WIDTH // 2 - self.get_current_size() // 2
            self.y = HEIGHT // 2 - self.get_current_size() // 2
            # Re-position computer
            self.computer.rect.x = self.x + 80
            self.computer.rect.y = self.y + 30
            self.computer.desk_rect.x = self.x + 70
            self.computer.desk_rect.y = self.y + 60
            return True
        return False

    def add_decoration(self, decoration, x, y):
        """Add a decoration to the home"""
        current_tier = self.get_current_tier()
        if len(self.decorations) < current_tier['capacity']:
            self.decorations.append({'decoration': decoration, 'x': x, 'y': y})
            return True
        return False

    def draw(self, surf):
        """Draw the home interior"""
        size = self.get_current_size()
        
        # Draw house background
        pygame.draw.rect(surf, (220, 200, 180), pygame.Rect(self.x, self.y, size, size))
        pygame.draw.rect(surf, (100, 100, 100), pygame.Rect(self.x, self.y, size, size), 3)
        
        # Draw floor grid
        for i in range(0, size, 20):
            pygame.draw.line(surf, (200, 180, 160), (self.x + i, self.y), (self.x + i, self.y + size), 1)
            pygame.draw.line(surf, (200, 180, 160), (self.x, self.y + i), (self.x + size, self.y + i), 1)
        
        # Draw computer and desk
        self.computer.draw(surf)
        
        # Draw decorations
        for item in self.decorations:
            decor = item['decoration']
            x = self.x + item['x']
            y = self.y + item['y']
            pygame.draw.rect(surf, decor['color'], pygame.Rect(x, y, 20, 20), border_radius=3)
            pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(x, y, 20, 20), 1, border_radius=3)



class Island:
    def __init__(self, island_data):
        self.name = island_data['name']
        self.id = island_data['id']
        self.x = island_data['x']
        self.y = island_data['y']
        self.width = island_data['width']
        self.height = island_data['height']
        self.buildings = self._generate_buildings()
        self.garages = self._generate_garages()
        self.shops = self._generate_shops()

    def _generate_buildings(self):
        buildings = []
        colors = [BUILDING_COLOR1, BUILDING_COLOR2, BUILDING_COLOR3]
        
        # Create a grid of buildings
        for bx in range(self.x + 10, self.x + self.width - 10, 50):
            for by in range(self.y + 10, self.y + self.height - 10, 50):
                color = random.choice(colors)
                b = Building(bx, by, 40, 40, color)
                buildings.append(b)
        
        return buildings

    def _generate_garages(self):
        """Create 2 garages on this island"""
        garages = []
        # Garage 1: left side
        garages.append(Garage(self.x + 20, self.y + self.height - 60, 0))
        # Garage 2: right side
        garages.append(Garage(self.x + self.width - 80, self.y + self.height - 60, 1))
        return garages

    def _generate_shops(self):
        """Create 1 decoration shop on this island"""
        shops = []
        # Shop: center bottom
        shops.append(DecorationShop(self.x + self.width // 2 - 30, self.y + self.height - 65, self.id))
        return shops

    def draw(self, surf):
        # Draw grass/ground
        pygame.draw.rect(surf, GRASS_COLOR, pygame.Rect(self.x, self.y, self.width, self.height))
        
        # Draw buildings
        for building in self.buildings:
            building.draw(surf)
        
        # Draw garages
        for garage in self.garages:
            garage.draw(surf)
        
        # Draw decoration shops
        for shop in self.shops:
            shop.draw(surf)
        
        # Draw island name
        font = pygame.font.SysFont("Arial", 14, bold=True)
        text = font.render(self.name, True, (0, 0, 0))
        surf.blit(text, (self.x + 5, self.y + 5))



def draw_world(surf):
    """Draw the world with all islands and water"""
    surf.fill(WATER_COLOR)  # Water background
    
    # Draw all islands
    for island in ISLANDS_OBJ:
        island.draw(surf)
    
    # Draw ferry connections as simple docks
    for from_id, to_id in FERRY_ROUTES:
        island_from = ISLANDS_OBJ[from_id]
        island_to = ISLANDS_OBJ[to_id]
        
        # Draw a simple line representing ferry route
        pygame.draw.line(
            surf,
            (100, 150, 100),
            (island_from.x + island_from.width // 2, island_from.y + island_from.height),
            (island_to.x + island_to.width // 2, island_to.y),
            2
        )


def draw_text(surf, text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.SysFont("Arial", size)
    img = font.render(text, True, color)
    rect = img.get_rect()
    rect.topleft = (x, y)
    surf.blit(img, rect)


def get_available_ferries(current_island_id):
    """Get ferries available from current island"""
    available = []
    for from_id, to_id in FERRY_ROUTES:
        if from_id == current_island_id:
            available.append(to_id)
        elif to_id == current_island_id:
            available.append(from_id)
    return available


def draw_login_screen(screen, font, username="", password="", mode="login", error_msg="", info_msg="", input_mode="username"):
    """Draw login/register screen"""
    screen.fill((50, 50, 50))
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title = title_font.render("City Car Race - Account System", True, (255, 255, 255))
    title_rect = title.get_rect(center=(WIDTH // 2, 50))
    screen.blit(title, title_rect)
    
    # Mode indicator
    mode_text = font.render(f"[{mode.upper()}] Press Tab to switch", True, (200, 200, 255))
    screen.blit(mode_text, (20, 100))
    
    # Username label and input
    user_label = font.render("Username:", True, (255, 255, 255))
    screen.blit(user_label, (100, 150))
    user_color = (255, 200, 100) if input_mode == "username" else (200, 200, 200)
    pygame.draw.rect(screen, (100, 100, 100), (100, 180, 400, 40), border_radius=5)
    pygame.draw.rect(screen, user_color, (100, 180, 400, 40), 2, border_radius=5)
    user_text = font.render(username + ("_" if input_mode == "username" else ""), True, (255, 255, 255))
    screen.blit(user_text, (110, 190))
    
    # Password label and input
    pass_label = font.render("Password:", True, (255, 255, 255))
    screen.blit(pass_label, (100, 240))
    pass_color = (255, 200, 100) if input_mode == "password" else (200, 200, 200)
    pygame.draw.rect(screen, (100, 100, 100), (100, 270, 400, 40), border_radius=5)
    pygame.draw.rect(screen, pass_color, (100, 270, 400, 40), 2, border_radius=5)
    pass_text = font.render("*" * len(password) + ("_" if input_mode == "password" else ""), True, (255, 255, 255))
    screen.blit(pass_text, (110, 280))
    
    # Instructions
    instr_font = pygame.font.Font(None, 24)
    instr = instr_font.render("Press ENTER to submit, TAB to switch mode, ESC to skip (play offline)", True, (200, 200, 200))
    screen.blit(instr, (50, 330))
    instr2 = instr_font.render("Use arrow keys to switch between username/password", True, (200, 200, 200))
    screen.blit(instr2, (50, 360))
    
    # Error message
    if error_msg:
        err = font.render(f"Error: {error_msg}", True, (255, 100, 100))
        screen.blit(err, (100, 400))
    
    # Info message
    if info_msg:
        info = font.render(info_msg, True, (100, 255, 100))
        y_offset = 440 if not error_msg else 440
        screen.blit(info, (100, y_offset))
    
    pygame.display.flip()

def login_screen():
    """Show login/register screen and return ChatClient if authenticated, None if offline"""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("City Car Race - Login")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    
    username = ""
    password = ""
    mode = "login"  # "login" or "register"
    input_mode = "username"  # which field to edit
    error_msg = ""
    info_msg = ""
    chat_client = None
    
    # Initialize gamepad for login screen
    gamepad = GamepadHandler()
    prev_dpad = (False, False, False, False)  # Track previous D-pad state
    
    running = True
    while running:
        clock.tick(30)
        gamepad.update()  # Update gamepad state
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # offline mode
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None  # offline mode
                
                elif event.key == pygame.K_TAB:
                    # Switch mode
                    mode = "register" if mode == "login" else "login"
                    error_msg = ""
                    info_msg = f"Switched to {mode.upper()} mode"
                
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    # Switch input field
                    input_mode = "password" if input_mode == "username" else "username"
                
                elif event.key == pygame.K_RETURN:
                    # Submit login/register
                    if not username or not password:
                        error_msg = "Username and password required"
                        info_msg = ""
                        continue
                    
                    error_msg = ""
                    info_msg = f"Attempting {mode}..."
                    draw_login_screen(screen, font, username, password, mode, error_msg, info_msg, input_mode)
                    pygame.display.flip()
                    pygame.time.wait(500)
                    
                    try:
                        chat_client = ChatClient()
                        if mode == "login":
                            success, msg = chat_client.login(username, password, timeout=3)
                        else:  # register
                            success, msg = chat_client.register(username, password, timeout=3)
                        
                        if success:
                            info_msg = f"Success! Logged in as {username}"
                            draw_login_screen(screen, font, username, password, mode, "", info_msg, input_mode)
                            pygame.display.flip()
                            pygame.time.wait(1500)
                            return chat_client
                        else:
                            error_msg = msg
                            info_msg = ""
                            password = ""  # clear password on error
                    except Exception as e:
                        error_msg = str(e)
                        info_msg = ""
                        password = ""
                
                elif event.key == pygame.K_BACKSPACE:
                    if input_mode == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                    error_msg = ""
                
                elif event.unicode.isprintable():
                    if input_mode == "username":
                        username += event.unicode
                    else:
                        password += event.unicode
                    error_msg = ""
        
        # Gamepad D-pad controls for login screen
        if gamepad.is_connected():
            dpad_up, dpad_down, dpad_left, dpad_right = gamepad.get_dpad()
            curr_dpad = (dpad_up, dpad_down, dpad_left, dpad_right)
            
            # D-pad UP or LEFT = Switch to login mode
            if (dpad_up or dpad_left) and not (prev_dpad[0] or prev_dpad[2]):
                mode = "login"
                error_msg = ""
                info_msg = "Switched to LOGIN mode"
            
            # D-pad DOWN or RIGHT = Switch to register mode
            if (dpad_down or dpad_right) and not (prev_dpad[1] or prev_dpad[3]):
                mode = "register"
                error_msg = ""
                info_msg = "Switched to REGISTER mode"
            
            prev_dpad = curr_dpad
            
            # A button = Submit
            if gamepad.was_button_pressed('a'):
                if not username or not password:
                    error_msg = "Username and password required"
                    info_msg = ""
                else:
                    error_msg = ""
                    info_msg = f"Attempting {mode}..."
                    draw_login_screen(screen, font, username, password, mode, error_msg, info_msg, input_mode)
                    pygame.display.flip()
                    pygame.time.wait(500)
                    
                    try:
                        chat_client = ChatClient()
                        if mode == "login":
                            success, msg = chat_client.login(username, password, timeout=3)
                        else:
                            success, msg = chat_client.register(username, password, timeout=3)
                        
                        if success:
                            info_msg = f"Success! Logged in as {username}"
                            draw_login_screen(screen, font, username, password, mode, "", info_msg, input_mode)
                            pygame.display.flip()
                            pygame.time.wait(1500)
                            return chat_client
                        else:
                            error_msg = msg
                            info_msg = ""
                            password = ""
                    except Exception as e:
                        error_msg = str(e)
                        info_msg = ""
                        password = ""
            
            # B button = Back to offline mode
            if gamepad.was_button_pressed('b'):
                return None  # offline mode
        
        draw_login_screen(screen, font, username, password, mode, error_msg, info_msg, input_mode)
    
    return None

def main():
    pygame.init()
    
    # Show login screen first
    print("Showing login screen...")
    auth_client = login_screen()
    if auth_client:
        print(f"Logged in as: {auth_client.username}")
        online_mode_default = True
    else:
        print("Playing offline mode")
        online_mode_default = False
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("City Car Race - Multi-Island Adventure")
    clock = pygame.time.Clock()

    # Initialize islands
    global ISLANDS_OBJ
    ISLANDS_OBJ = [Island(island_data) for island_data in ISLANDS]

    # player starts on Downtown island
    downtown = ISLANDS_OBJ[0]
    player = PlayerCar(downtown.x + downtown.width // 2, downtown.y + downtown.height // 2)
    player.speed = 0
    player.current_island = 0

    # Create mobile control buttons (if applicable)
    buttons = None
    if IS_MOBILE:
        buttons = {
            'up': Button(WIDTH // 2 - BUTTON_SIZE // 2, HEIGHT - 4 * BUTTON_SIZE - 3 * BUTTON_PADDING, BUTTON_SIZE, BUTTON_SIZE, '▲', 'up'),
            'down': Button(WIDTH // 2 - BUTTON_SIZE // 2, HEIGHT - 2 * BUTTON_SIZE - BUTTON_PADDING, BUTTON_SIZE, BUTTON_SIZE, '▼', 'down'),
            'left': Button(WIDTH // 2 - 3 * BUTTON_SIZE - 2 * BUTTON_PADDING, HEIGHT - 2 * BUTTON_SIZE - BUTTON_PADDING, BUTTON_SIZE, BUTTON_SIZE, '◄', 'left'),
            'right': Button(WIDTH // 2 + BUTTON_SIZE + BUTTON_PADDING, HEIGHT - 2 * BUTTON_SIZE - BUTTON_PADDING, BUTTON_SIZE, BUTTON_SIZE, '►', 'right'),
            'ferry': Button(WIDTH - BUTTON_SIZE - BUTTON_PADDING, HEIGHT - BUTTON_SIZE - BUTTON_PADDING, BUTTON_SIZE, BUTTON_SIZE, 'F', 'ferry'),
        }
    
    # Initialize gamepad support (Nintendo Switch, Xbox, PlayStation, etc.)
    gamepad = GamepadHandler()

    npcs = []
    spawn_timer = 0
    spawn_interval = 80

    score = 0
    distance = 0
    races_won = 0  # Track races won for difficulty progression
    running = True
    game_over = False
    garage_open = False  # Track if garage shop is open
    current_garage = None  # Which garage is open
    shop_open = False  # Track if decoration shop is open
    current_shop = None  # Which shop is open
    home_open = False  # Track if home is open
    camera_app_open = False  # Track if camera app is open
    camera_recording = False  # Track if currently recording
    video_library_view = False  # Track if viewing video library
    active_race = None  # Current active race
    race_prompt = None  # NPC to race with (pending confirmation)
    # Track editor
    editor_open = False
    track_editor = TrackEditor()
    # Effects (visual feedback)
    effects = []
    # Tuning overlay
    tuning_mode = False
    tuning_params = [
        {'name': 'knockback', 'value': NPC_COLLISION_KNOCKBACK, 'step': 5},
        {'name': 'slow', 'value': NPC_COLLISION_SLOW, 'step': 1},
        {'name': 'score_penalty', 'value': NPC_COLLISION_SCORE_PENALTY, 'step': 5},
        {'name': 'cooldown', 'value': NPC_COLLISION_COOLDOWN, 'step': 0.1},
    ]
    tuning_index = 0
    # try load saved settings
    try:
        if os.path.exists('settings.json'):
            with open('settings.json','r') as f:
                s = json.load(f)
                for p in tuning_params:
                    if p['name'] in s:
                        p['value'] = s[p['name']]
    except Exception:
        pass
    # Online chat variables
    chat_client = auth_client  # Use authenticated client if logged in
    online_mode = online_mode_default  # Start in online mode if logged in
    if online_mode and chat_client:
        chat_client.connect()  # Send join message
    chat_active = False
    chat_input = ""
    chat_lines = []  # list of recent chat lines to display

    while running:
        dt = clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if buttons:
                for button in buttons.values():
                    button.handle_event(event)
            # Mouse controls for track editor
            if event.type == pygame.MOUSEBUTTONDOWN:
                if editor_open:
                    if event.button == 1:  # left click -> place
                        track_editor.place_block(*event.pos)
                    elif event.button == 3:  # right click -> remove
                        track_editor.remove_block_at(*event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and game_over:
                    # restart
                    npcs.clear()
                    downtown = ISLANDS_OBJ[0]
                    player.rect.centerx = downtown['x'] + downtown['width'] // 2
                    player.rect.centery = downtown['y'] + downtown['height'] // 2
                    player.speed = 0
                    player.current_island = 0
                    score = 0
                    distance = 0
                    spawn_timer = 0
                    game_over = False
                # Toggle tuning overlay (F1)
                if event.key == pygame.K_F1:
                    tuning_mode = not tuning_mode
                    tuning_index = 0
                    # if closing tuning overlay, persist settings
                    if not tuning_mode:
                        try:
                            s = {p['name']: p['value'] for p in tuning_params}
                            with open('settings.json', 'w') as f:
                                json.dump(s, f, indent=2)
                            chat_lines.append({'type': 'system', 'text': 'Tuning saved.'})
                        except Exception:
                            pass
                # Press F to take a ferry (keyboard)
                if event.key == pygame.K_f:
                    available_ferries = get_available_ferries(player.current_island)
                    if available_ferries:
                        target_island = available_ferries[0]
                        player.current_island = target_island
                        island_data = ISLANDS[target_island]
                        player.rect.centerx = island_data['x'] + island_data['width'] // 2
                        player.rect.centery = island_data['y'] + island_data['height'] // 2
                        player.speed = 0
                        score += 50
                
                # Press H to enter home
                if event.key == pygame.K_h and not garage_open and not shop_open and not home_open:
                    home_open = True
                
                # Press G to open garage
                if event.key == pygame.K_g and not garage_open and not shop_open and not home_open:
                    for garage in ISLANDS_OBJ[player.current_island].garages:
                        if player.rect.colliderect(garage.rect):
                            garage_open = True
                            current_garage = garage
                            break
                # Toggle Track Editor
                if event.key == pygame.K_e:
                    editor_open = not editor_open
                    if editor_open:
                        track_editor.load()

                # If editor is open, handle editor-specific keys
                if editor_open:
                    # Select block types 1-6
                    if event.key == pygame.K_1:
                        track_editor.selected_index = 0
                    elif event.key == pygame.K_2:
                        track_editor.selected_index = 1
                    elif event.key == pygame.K_3:
                        track_editor.selected_index = 2
                    elif event.key == pygame.K_4:
                        track_editor.selected_index = 3
                    elif event.key == pygame.K_5:
                        track_editor.selected_index = 4
                    elif event.key == pygame.K_6:
                        track_editor.selected_index = 5
                    elif event.key == pygame.K_s:
                        track_editor.save()
                        chat_lines.append({'type':'system','text':'Track saved to tracks.json'})
                    elif event.key == pygame.K_l:
                        track_editor.load()
                        chat_lines.append({'type':'system','text':'Track loaded from tracks.json'})
                    elif event.key == pygame.K_g:
                        track_editor.show_grid = not track_editor.show_grid
                    elif event.key == pygame.K_r:
                        mx, my = pygame.mouse.get_pos()
                        track_editor.rotate_block_at(mx, my)

                # If tuning overlay is open, handle tuning keys
                if tuning_mode:
                    if event.key == pygame.K_UP:
                        tuning_index = max(0, tuning_index - 1)
                    elif event.key == pygame.K_DOWN:
                        tuning_index = min(len(tuning_params)-1, tuning_index + 1)
                    elif event.key == pygame.K_LEFT:
                        p = tuning_params[tuning_index]
                        p['value'] = max(0, p['value'] - p.get('step', 1))
                    elif event.key == pygame.K_RIGHT:
                        p = tuning_params[tuning_index]
                        p['value'] = p['value'] + p.get('step', 1)
                
                # Press S to open shop
                if event.key == pygame.K_s and not garage_open and not shop_open and not home_open:
                    for shop in ISLANDS_OBJ[player.current_island].shops:
                        if player.rect.colliderect(shop.rect):
                            shop_open = True
                            current_shop = shop
                            break
            
            # Gamepad button controls
            # X button = Ferry
            if gamepad.was_button_pressed('x'):
                available_ferries = get_available_ferries(player.current_island)
                if available_ferries:
                    target_island = available_ferries[0]
                    player.current_island = target_island
                    island_data = ISLANDS[target_island]
                    player.rect.centerx = island_data['x'] + island_data['width'] // 2
                    player.rect.centery = island_data['y'] + island_data['height'] // 2
                    player.speed = 0
                    score += 50
            
            # Y button = Home
            if gamepad.was_button_pressed('y') and not garage_open and not shop_open and not home_open:
                home_open = True
            
            # RB button = Garage
            if gamepad.was_button_pressed('rb') and not garage_open and not shop_open and not home_open:
                for garage in ISLANDS_OBJ[player.current_island].garages:
                    if player.rect.colliderect(garage.rect):
                        garage_open = True
                        current_garage = garage
                        break
            
            # LB button = Shop
            if gamepad.was_button_pressed('lb') and not garage_open and not shop_open and not home_open:
                for shop in ISLANDS_OBJ[player.current_island].shops:
                    if player.rect.colliderect(shop.rect):
                        shop_open = True
                        current_shop = shop
                        break
            
            # RT button = Chat
            if gamepad.was_button_pressed('rt') and online_mode and not chat_active:
                chat_active = True
                chat_input = ""
            # Start button toggles tuning overlay
            if gamepad.was_button_pressed('start'):
                tuning_mode = not tuning_mode
                tuning_index = 0
                if not tuning_mode:
                    try:
                        s = {p['name']: p['value'] for p in tuning_params}
                        with open('settings.json', 'w') as f:
                            json.dump(s, f, indent=2)
                        chat_lines.append({'type': 'system', 'text': 'Tuning saved.'})
                    except Exception:
                        pass
            # Chat / online controls
            if event.type == pygame.KEYDOWN:
                # Toggle online mode (connect/disconnect)
                if event.key == pygame.K_o:
                    if not online_mode:
                        # attempt to connect
                        username = f"Player{random.randint(1000,9999)}"
                        chat_client = ChatClient(username=username)
                        connected = chat_client.connect()
                        if connected:
                            online_mode = True
                            chat_lines.append({'type': 'system', 'text': 'Connected to chat server.'})
                        else:
                            chat_client = None
                            chat_lines.append({'type': 'system', 'text': 'Failed to connect to chat server.'})
                    else:
                        # disconnect
                        if chat_client:
                            chat_client.close()
                        chat_client = None
                        online_mode = False
                        chat_lines.append({'type': 'system', 'text': 'Disconnected from chat server.'})

                # Open chat input
                if event.key == pygame.K_t and online_mode:
                    chat_active = True
                    chat_input = ""

                # If chat is active, handle typing keys
                if chat_active:
                    if event.key == pygame.K_RETURN:
                        # send message
                        if chat_input.strip():
                            if chat_client:
                                chat_client.send_message(chat_input.strip())
                            chat_lines.append({'type': 'chat', 'username': 'You', 'text': chat_input.strip()})
                        chat_input = ""
                        chat_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        chat_input = chat_input[:-1]
                    else:
                        # append printable chars
                        if hasattr(event, 'unicode') and event.unicode:
                            chat_input += event.unicode
                
                # Camera app controls (when in home with camera open)
                if camera_app_open:
                    if event.key == pygame.K_ESCAPE:
                        camera_app_open = False
                    elif event.key == pygame.K_SPACE:
                        # Toggle recording
                        if not camera_recording:
                            player.home.computer.start_recording()
                            camera_recording = True
                        else:
                            duration = player.home.computer.stop_recording()
                            camera_recording = False
                            # Auto-save video
                            title = f"Video {len(player.home.video_library.videos) + 1}"
                            player.home.video_library.add_video(title, duration)
                    elif event.key == pygame.K_l:
                        # View library
                        video_library_view = not video_library_view
                    elif event.key == pygame.K_RETURN and video_library_view:
                        # Upload video
                        videos = player.home.video_library.videos
                        if videos:
                            earnings = player.home.video_library.upload_video(0)
                            chat_lines.append({'type': 'system', 'text': f'Uploaded video! Earned ${earnings}'})
                            # Move uploaded video to end
                            uploaded = videos.pop(0)
                            videos.append(uploaded)
                            player.home.video_library.save_videos()
                    elif event.key == pygame.K_DELETE and video_library_view:
                        # Delete video
                        videos = player.home.video_library.videos
                        if videos:
                            player.home.video_library.delete_video(0)
                
                # Gamepad camera app controls (when in home with camera open)
                if camera_app_open and gamepad.is_connected():
                    # B button = Close camera
                    if gamepad.was_button_pressed('b'):
                        camera_app_open = False
                    # A button or Y button = Toggle recording
                    elif gamepad.was_button_pressed('a') or gamepad.was_button_pressed('y'):
                        if not camera_recording:
                            player.home.computer.start_recording()
                            camera_recording = True
                        else:
                            duration = player.home.computer.stop_recording()
                            camera_recording = False
                            # Auto-save video
                            title = f"Video {len(player.home.video_library.videos) + 1}"
                            player.home.video_library.add_video(title, duration)
                    # X button = Toggle library view
                    elif gamepad.was_button_pressed('x'):
                        video_library_view = not video_library_view
                    # RT button = Upload video
                    elif gamepad.was_button_pressed('rt') and video_library_view:
                        videos = player.home.video_library.videos
                        if videos:
                            earnings = player.home.video_library.upload_video(0)
                            chat_lines.append({'type': 'system', 'text': f'Uploaded video! Earned ${earnings}'})
                            # Move uploaded video to end
                            uploaded = videos.pop(0)
                            videos.append(uploaded)
                            player.home.video_library.save_videos()
                    # LB button = Delete video
                    elif gamepad.was_button_pressed('lb') and video_library_view:
                        videos = player.home.video_library.videos
                        if videos:
                            player.home.video_library.delete_video(0)

        if not game_over:
            gamepad.update()  # Update gamepad state each frame
            player.update(keys, buttons, gamepad)
            player.move()

            # Editor gamepad cursor handling (per-frame)
            if editor_open and gamepad.is_connected():
                stick_x, stick_y = gamepad.get_stick_input()
                # stick_y: negative = up, positive = down
                # move cursor based on dt
                move_x = stick_x * track_editor.cursor_speed * (dt / 1000.0)
                move_y = stick_y * track_editor.cursor_speed * (dt / 1000.0)
                track_editor.cursor_x = max(0, min(WIDTH, track_editor.cursor_x + move_x))
                track_editor.cursor_y = max(0, min(HEIGHT, track_editor.cursor_y + move_y))
                # D-pad selection
                d_up, d_down, d_left, d_right = gamepad.get_dpad()
                # detect edges
                prev = track_editor.prev_dpad
                if d_left and not prev[2]:
                    track_editor.selected_index = max(0, track_editor.selected_index - 1)
                if d_right and not prev[3]:
                    track_editor.selected_index = min(len(track_editor.BLOCK_ORDER)-1, track_editor.selected_index + 1)
                if d_up and not prev[0]:
                    track_editor.selected_index = 0
                if d_down and not prev[1]:
                    track_editor.selected_index = len(track_editor.BLOCK_ORDER)-1
                track_editor.prev_dpad = (d_up, d_down, d_left, d_right)
                # Buttons: A = place, B = remove, X = rotate
                if gamepad.was_button_pressed('a'):
                    track_editor.place_block(track_editor.cursor_x, track_editor.cursor_y)
                if gamepad.was_button_pressed('b'):
                    track_editor.remove_block_at(track_editor.cursor_x, track_editor.cursor_y)
                if gamepad.was_button_pressed('x'):
                    track_editor.rotate_block_at(track_editor.cursor_x, track_editor.cursor_y)

            # Tuning overlay gamepad handling
            if tuning_mode and gamepad.is_connected():
                d_up, d_down, d_left, d_right = gamepad.get_dpad()
                # edge detection using prev_dpad stored on gamepad object
                prev_hat = getattr(gamepad, 'prev_hat', (False, False, False, False))
                if d_up and not prev_hat[0]:
                    tuning_index = max(0, tuning_index - 1)
                if d_down and not prev_hat[1]:
                    tuning_index = min(len(tuning_params)-1, tuning_index + 1)
                # left/right adjust value
                if d_left and not prev_hat[2]:
                    p = tuning_params[tuning_index]
                    p['value'] = max(0, p['value'] - p.get('step', 1))
                if d_right and not prev_hat[3]:
                    p = tuning_params[tuning_index]
                    p['value'] = p['value'] + p.get('step', 1)
                # LB/RB for larger steps
                if gamepad.was_button_pressed('lb'):
                    p = tuning_params[tuning_index]
                    p['value'] = max(0, p['value'] - p.get('step', 1) * 5)
                if gamepad.was_button_pressed('rb'):
                    p = tuning_params[tuning_index]
                    p['value'] = p['value'] + p.get('step', 1) * 5
                gamepad.prev_hat = (d_up, d_down, d_left, d_right)

            # Track block gameplay interactions
            if track_editor.blocks:
                cx, cy = player.rect.center
                for b in track_editor.blocks:
                    if abs(b.x - cx) < TrackBlock.SIZE//2 and abs(b.y - cy) < TrackBlock.SIZE//2:
                        now = time.time()
                        if now - getattr(b, 'last_trigger', 0) > 1.0:
                            b.last_trigger = now
                            if b.type == 'boost':
                                # give a burst of speed
                                player.speed = min(player.max_speed + 3, player.speed + 4)
                            elif b.type == 'obstacle':
                                # slow player and penalize
                                player.speed = max(0, player.speed - 3)
                                score = max(0, score - 10)
                            elif b.type == 'start':
                                player.lap_started = True
                            elif b.type == 'finish':
                                if getattr(player, 'lap_started', False):
                                    player.lap_started = False
                                    races_won += 1
                                    player.currency += 100
                                    chat_lines.append({'type': 'system', 'text': f'Finished lap! Earned $100. Laps: {races_won}'})
            
            # Close garage/shop/home (press Escape or B button)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and (garage_open or shop_open or home_open):
                garage_open = False
                shop_open = False
                home_open = False
            
            # B button = Cancel (close menus)
            if gamepad.was_button_pressed('b') and (garage_open or shop_open or home_open):
                garage_open = False
                shop_open = False
                home_open = False
                current_garage = None
                current_shop = None
            
            # Buy car (press 1, 2, 3, or 4 in garage)
            if garage_open and event.type == pygame.KEYDOWN:
                car_num = event.key - pygame.K_1
                if 0 <= car_num < len(CAR_MODELS):
                    car_model = CAR_MODELS[car_num]
                    if player.buy_car(car_model):
                        score += 100  # Bonus for buying a car
                    else:
                        player.currency += 100  # Give player money if purchase fails (for testing)
            
            # Buy decoration (press 1, 2, 3, etc. in shop)
            if shop_open and event.type == pygame.KEYDOWN:
                decor_num = event.key - pygame.K_1
                if 0 <= decor_num < len(DECORATIONS):
                    decoration = DECORATIONS[decor_num]
                    if player.buy_decoration(decoration):
                        score += 25
            
            # Upgrade house (press U in home screen)
            if home_open and event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                if player.buy_house_upgrade():
                    score += 200
            
            # Place decoration in home (click mouse button)
            if home_open and event.type == pygame.MOUSEBUTTONDOWN:
                home_size = player.home.get_current_size()
                home_x = player.home.x
                home_y = player.home.y
                
                # Check if click is on computer
                computer = player.home.computer
                if computer.rect.collidepoint(event.pos):
                    camera_app_open = True
                    video_library_view = False
                    camera_recording = False
                # Check if click is inside home for decoration placement
                elif (home_x <= event.pos[0] <= home_x + home_size and 
                    home_y <= event.pos[1] <= home_y + home_size):
                    # Get click position relative to home
                    rel_x = event.pos[0] - home_x
                    rel_y = event.pos[1] - home_y
                    
                    # Snap to grid (20 pixel cells)
                    grid_x = (rel_x // 20) * 20
                    grid_y = (rel_y // 20) * 20
                    
                    # Place most recent decoration
                    if player.decoration_inventory and player.home.add_decoration(player.decoration_inventory[-1], grid_x, grid_y):
                        player.decoration_inventory.pop()
            
            # Check ferry button on mobile
            if buttons and buttons['ferry'].is_pressed():
                available_ferries = get_available_ferries(player.current_island)
                if available_ferries:
                    target_island = available_ferries[0]
                    player.current_island = target_island
                    island_data = ISLANDS[target_island]
                    player.rect.centerx = island_data['x'] + island_data['width'] // 2
                    player.rect.centery = island_data['y'] + island_data['height'] // 2
                    player.speed = 0
                    score += 50
                    buttons['ferry'].pressed = False  # Release button

            # spawn NPCs on current island periodically
            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                island_data = ISLANDS[player.current_island]
                x = random.randint(island_data['x'] + 30, island_data['x'] + island_data['width'] - 30)
                y = island_data['y'] - 80
                speed = random.uniform(2.0, 5.0)
                npc = NPCCar(x, y, speed, player.current_island)
                npcs.append(npc)

            # update NPCs - only those on current island
            for npc in list(npcs):
                if npc.island_id == player.current_island:
                    npc.update()
                    island_data = ISLANDS[player.current_island]
                    if npc.rect.top > island_data['y'] + island_data['height'] + 200:
                        npcs.remove(npc)
                        score += 15
                        player.currency += 25  # Earn money when avoiding NPCs

            # collision check with NPCs on current island
            for npc in npcs:
                if npc.island_id == player.current_island and not active_race:
                    if player.rect.colliderect(npc.rect):
                        now = time.time()
                        if now - getattr(npc, 'last_collision_time', 0) > tuning_params[3]['value']:
                            npc.last_collision_time = now
                            # read tuning params
                            kb = tuning_params[0]['value']
                            sl = tuning_params[1]['value']
                            sp = tuning_params[2]['value']
                            # knock back player a bit (pixels)
                            try:
                                player.rect.y += int(kb)
                            except Exception:
                                pass
                            # slow player and reduce score
                            player.speed = max(0, player.speed - sl)
                            score = max(0, score - int(sp))
                            chat_lines.append({'type': 'system', 'text': f'You hit an NPC! Slowdown and -{int(sp)} score.'})
                            # spawn visual effect at player's center
                            effects.append(HitEffect(player.rect.centerx, player.rect.centery))
            
            # Handle race prompt (press Space to accept race)
            if race_prompt and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                active_race = Race(race_prompt, races_won)  # Difficulty increases with races won
                race_prompt = None
            
            # Update active race
            if active_race:
                active_race.update(player.rect, player.speed)
                if active_race.finished:
                    if active_race.won:
                        player.currency += active_race.prize_money
                        score += active_race.prize_money // 10
                        races_won += 1
                    else:
                        score -= 50  # Penalty for losing race
                    active_race.npc.set_race_mode(False)  # End race mode
                    active_race = None

            # update distance score based on player speed
            distance += max(0, int(player.speed))

        # draw world
        draw_world(screen)

        # draw NPCs on current island
        for npc in npcs:
            if npc.island_id == player.current_island:
                npc.draw(screen)

        # draw player
        player.draw(screen)

        # draw effects (and prune finished ones)
        new_effects = []
        for ef in effects:
            alive = ef.draw(screen)
            if alive:
                new_effects.append(ef)
        effects = new_effects

        # HUD
        current_island_name = ISLANDS_OBJ[player.current_island].name
        draw_text(screen, f"Score: {score}", 24, 10, 10)
        draw_text(screen, f"Distance: {distance}", 24, 10, 40)
        draw_text(screen, f"Island: {current_island_name}", 24, 10, 70)
        draw_text(screen, f"Money: ${player.currency}", 24, 10, 100, color=(255, 200, 0))
        draw_text(screen, f"Races Won: {races_won}", 16, 10, 130, color=(150, 255, 255))
        
        # Show current car if owned
        if player.car_model:
            draw_text(screen, f"Car: {player.car_model['name']}", 16, 10, 150, color=(150, 255, 150))
        
        # Show race prompt if nearby
        if race_prompt and not active_race:
            draw_text(screen, "RACE CHALLENGE!", 32, WIDTH // 2 - 120, HEIGHT // 2, color=(255, 100, 100))
            draw_text(screen, f"Difficulty: {RACE_DIFFICULTIES[min(races_won, len(RACE_DIFFICULTIES) - 1)]['name']}", 20, WIDTH // 2 - 140, HEIGHT // 2 + 40)
            draw_text(screen, f"Prize: ${RACE_DIFFICULTIES[min(races_won, len(RACE_DIFFICULTIES) - 1)]['prize']}", 20, WIDTH // 2 - 110, HEIGHT // 2 + 70)
            draw_text(screen, "Press SPACE to accept race!", 18, WIDTH // 2 - 140, HEIGHT // 2 + 110, color=(255, 255, 100))
        
        # Show active race HUD
        if active_race:
            draw_text(screen, "RACING!", 40, WIDTH // 2 - 100, 30, color=(255, 150, 0))
            player_pct, npc_pct = active_race.get_display_progress()
            draw_text(screen, f"You: {player_pct}%", 24, 200, 80, color=(150, 255, 150))
            draw_text(screen, f"Opponent: {npc_pct}%", 24, 200, 110, color=(255, 100, 100))
            draw_text(screen, f"Prize: ${active_race.prize_money}", 20, 200, 140, color=(255, 200, 0))
            
            # Progress bars
            bar_width = 300
            pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(200, 160, bar_width, 20))
            pygame.draw.rect(screen, (150, 255, 150), pygame.Rect(200, 160, int(bar_width * player_pct / 100), 20))
            
            pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(200, 190, bar_width, 20))
            pygame.draw.rect(screen, (255, 100, 100), pygame.Rect(200, 190, int(bar_width * npc_pct / 100), 20))
        
        # Show available ferries
        available = get_available_ferries(player.current_island)
        if available:
            ferry_info = "Ferries: " + ", ".join([ISLANDS_OBJ[dest].name for dest in available])
            draw_text(screen, ferry_info, 16, 10, 150, color=(150, 255, 150))
            if not IS_MOBILE:
                draw_text(screen, "Press F to take ferry", 14, 10, 170, color=(150, 255, 150))
        
        # Show control hints based on device
        if not IS_MOBILE:
            draw_text(screen, "WASD: move | G: garage | S: shop | H: home | R: restart | Esc: quit", 14, 10, HEIGHT - 25)
        else:
            draw_text(screen, "Tap buttons to move | Tap F to take ferry", 14, 10, HEIGHT - 100, color=(150, 255, 150))
        # Tuning hint
        if not IS_MOBILE:
            draw_text(screen, "F1: Tuning (Start on controller)", 14, 10, HEIGHT - 45, color=(200,200,255))

        # Process incoming chat messages
        if online_mode and chat_client:
            # move any new messages from client inbox to local chat_lines
            while chat_client.inbox:
                msg = chat_client.inbox.pop(0)
                # Filter out NPC-generated chat messages (usernames starting with 'npc')
                try:
                    if msg.get('type') == 'chat':
                        uname = (msg.get('username') or '')
                        if isinstance(uname, str) and uname.lower().startswith('npc'):
                            # discard NPC chat
                            continue
                except Exception:
                    pass
                chat_lines.append(msg)
            # cap lines
            if len(chat_lines) > 50:
                chat_lines = chat_lines[-50:]

        # Draw chat area (bottom-left)
        chat_x = 10
        chat_y = HEIGHT - 180
        chat_w = 360
        chat_h = 160
        pygame.draw.rect(screen, (0, 0, 0, 120), pygame.Rect(chat_x - 6, chat_y - 6, chat_w + 12, chat_h + 12))
        # show last 6 lines
        start = max(0, len(chat_lines) - 6)
        y = chat_y
        for line in chat_lines[start:]:
            if line.get('type') == 'system':
                draw_text(screen, f"* {line.get('text')}", 14, chat_x, y, color=(200, 200, 200))
            elif line.get('type') == 'warning':
                draw_text(screen, f"! {line.get('text')}", 14, chat_x, y, color=(255, 160, 0))
            elif line.get('type') == 'chat':
                draw_text(screen, f"{line.get('username')}: {line.get('text')}", 14, chat_x, y, color=(180, 255, 180))
            else:
                # fallback
                txt = line.get('text') if isinstance(line, dict) else str(line)
                draw_text(screen, txt, 14, chat_x, y)
            y += 20

        # Chat input box
        if online_mode:
            input_box = pygame.Rect(chat_x, HEIGHT - 18, chat_w, 18)
            pygame.draw.rect(screen, (40, 40, 40), input_box)
            pygame.draw.rect(screen, (200, 200, 200), input_box, 1)
            hint = 'Press T to chat' if not chat_active else chat_input
            draw_text(screen, hint, 14, chat_x + 4, HEIGHT - 18, color=(220, 220, 220))

        # Draw garage shop UI
        if garage_open and current_garage:
            # Semi-transparent overlay
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, WIDTH, HEIGHT))
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Shop UI
            shop_rect = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)
            pygame.draw.rect(screen, (50, 50, 100), shop_rect)
            pygame.draw.rect(screen, (255, 200, 0), shop_rect, 3)
            
            draw_text(screen, current_garage.name, 28, shop_rect.x + 20, shop_rect.y + 20, color=(255, 200, 0))
            draw_text(screen, f"Your Money: ${player.currency}", 20, shop_rect.x + 20, shop_rect.y + 60)
            
            # List cars for sale
            y_offset = 110
            for i, car in enumerate(CAR_MODELS):
                can_afford = player.currency >= car['price']
                color = (150, 255, 150) if can_afford else (255, 100, 100)
                draw_text(screen, f"{i+1}. {car['name']} - ${car['price']}", 16, shop_rect.x + 20, shop_rect.y + y_offset, color=color)
                y_offset += 30
            
            draw_text(screen, "Press 1-4 to buy | Esc to close", 14, shop_rect.x + 20, shop_rect.y + HEIGHT // 3, color=(200, 200, 255))
        
        # Draw decoration shop UI
        if shop_open and current_shop:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Shop UI
            shop_rect = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)
            pygame.draw.rect(screen, (100, 50, 100), shop_rect)
            pygame.draw.rect(screen, (200, 100, 200), shop_rect, 3)
            
            draw_text(screen, current_shop.name, 28, shop_rect.x + 20, shop_rect.y + 20, color=(200, 100, 200))
            draw_text(screen, f"Your Money: ${player.currency}", 20, shop_rect.x + 20, shop_rect.y + 60)
            draw_text(screen, f"Decorations Owned: {len(player.decoration_inventory)}", 16, shop_rect.x + 20, shop_rect.y + 85)
            
            # List decorations for sale
            y_offset = 120
            for i, decor in enumerate(DECORATIONS):
                can_afford = player.currency >= decor['price']
                color = (150, 255, 150) if can_afford else (255, 100, 100)
                draw_text(screen, f"{i+1}. {decor['name']} - ${decor['price']}", 16, shop_rect.x + 20, shop_rect.y + y_offset, color=color)
                y_offset += 25
            
            draw_text(screen, "Press 1-6 to buy | Esc to close", 14, shop_rect.x + 20, shop_rect.y + HEIGHT // 3 + 10, color=(200, 200, 255))
        
        # Draw home screen UI
        if home_open:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(100)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Draw home
            player.home.draw(screen)
            
            # Home info panel
            home_tier = player.home.get_current_tier()
            draw_text(screen, f"Your Home: {home_tier['name']}", 24, 10, 20, color=(150, 255, 200))
            draw_text(screen, f"Decorations: {len(player.home.decorations)}/{home_tier['capacity']}", 18, 10, 50)
            draw_text(screen, f"Owned Decorations: {len(player.decoration_inventory)}", 18, 10, 75)
            draw_text(screen, f"Your Money: ${player.currency}", 20, 10, 105, color=(255, 200, 0))
            
            # Upgrade info
            if player.home.can_upgrade():
                next_tier = HOUSE_TIERS[player.home.house_tier + 1]
                draw_text(screen, f"Next: {next_tier['name']} - ${next_tier['price']}", 16, 10, 135, color=(150, 255, 150))
                draw_text(screen, "Press U to upgrade house", 14, 10, 160, color=(150, 255, 150))
            else:
                if player.home.house_tier < len(HOUSE_TIERS) - 1:
                    draw_text(screen, "Not enough money for upgrade", 14, 10, 135, color=(255, 100, 100))
                else:
                    draw_text(screen, "You own the Mansion!", 16, 10, 135, color=(255, 200, 100))
            
            # Decoration placement hint
            if player.decoration_inventory:
                draw_text(screen, f"Click to place decorations ({len(player.decoration_inventory)} available)", 14, 10, HEIGHT - 80, color=(150, 255, 255))
            
            # Computer/Camera app hint
            draw_text(screen, "Click Computer for Camera App / Video Library", 12, 10, HEIGHT - 55, color=(100, 200, 255))
            draw_text(screen, f"Videos recorded: {len(player.home.video_library.videos)}", 12, 10, HEIGHT - 35, color=(100, 200, 255))
            
            draw_text(screen, "Press Esc to close", 14, 10, HEIGHT - 15, color=(200, 200, 255))
        
        # Draw camera app UI
        if camera_app_open:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(120)
            overlay.fill((20, 20, 40))
            screen.blit(overlay, (0, 0))
            
            # Camera app window
            app_width, app_height = 600, 500
            app_x = (WIDTH - app_width) // 2
            app_y = (HEIGHT - app_height) // 2
            pygame.draw.rect(screen, (30, 30, 60), pygame.Rect(app_x, app_y, app_width, app_height))
            pygame.draw.rect(screen, (100, 200, 255), pygame.Rect(app_x, app_y, app_width, app_height), 3)
            
            if not video_library_view:
                # Camera recording view
                draw_text(screen, "CAMERA APP", 28, app_x + 20, app_y + 10, color=(100, 200, 255))
                
                # Show camera preview area
                preview_x = app_x + 50
                preview_y = app_y + 60
                preview_w, preview_h = 500, 250
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(preview_x, preview_y, preview_w, preview_h))
                pygame.draw.rect(screen, (100, 200, 255), pygame.Rect(preview_x, preview_y, preview_w, preview_h), 2)
                
                # Recording indicator
                if camera_recording:
                    draw_text(screen, "● RECORDING", 20, preview_x + 150, preview_y + 100, color=(255, 50, 50))
                    elapsed = time.time() - player.home.computer.recording_start
                    draw_text(screen, f"{int(elapsed)}s", 16, preview_x + 200, preview_y + 130, color=(255, 100, 100))
                else:
                    draw_text(screen, "Ready to Record", 18, preview_x + 120, preview_y + 110, color=(150, 200, 255))
                
                # Controls
                draw_text(screen, f"Total Videos: {len(player.home.video_library.videos)}", 14, app_x + 20, preview_y + preview_h + 20, color=(200, 200, 200))
                draw_text(screen, "SPACE: Record | L: Library | ESC: Close", 12, app_x + 20, preview_y + preview_h + 50, color=(150, 200, 255))
            else:
                # Video library view
                draw_text(screen, "VIDEO LIBRARY", 28, app_x + 20, app_y + 10, color=(100, 200, 255))
                
                videos = player.home.video_library.videos
                if videos:
                    library_y = app_y + 60
                    for i, video in enumerate(videos[:6]):  # Show up to 6 videos
                        color = (150, 255, 150) if i == 0 else (150, 200, 200)
                        draw_text(screen, f"{i+1}. {video.title} ({int(video.duration)}s) - Views: {video.views}", 12, app_x + 30, library_y + i*40, color=color)
                        
                        # Upload button for first video
                        if i == 0:
                            earnings = max(50, int(video.duration / 60 * 10))
                            draw_text(screen, f"Press Enter to upload for ${earnings}", 11, app_x + 50, library_y + i*40 + 20, color=(200, 255, 150))
                else:
                    draw_text(screen, "No videos yet. Record one!", 14, app_x + 50, app_y + 100, color=(200, 150, 150))
                
                draw_text(screen, "Enter: Upload First Video | Delete: Remove | L: Back | ESC: Close", 11, app_x + 20, app_y + app_height - 40, color=(150, 200, 255))

        # Draw mobile buttons
        if buttons:
            for button in buttons.values():
                button.draw(screen)

        if game_over:
            draw_text(screen, "GAME OVER - Hit by car!", 48, WIDTH // 2 - 250, HEIGHT // 2 - 40, color=(255, 40, 40))
            draw_text(screen, f"Final Score: {score}", 32, WIDTH // 2 - 150, HEIGHT // 2 + 30)
            draw_text(screen, f"Final Money: ${player.currency}", 24, WIDTH // 2 - 150, HEIGHT // 2 + 80)
            draw_text(screen, "Press R to restart", 24, WIDTH // 2 - 120, HEIGHT // 2 + 130)

        # Draw track editor overlay if active
        if editor_open:
            track_editor.draw(screen)

        # Draw tuning overlay if active
        if tuning_mode:
            overlay_w = 360
            overlay_h = 140
            overlay_x = WIDTH - overlay_w - 10
            overlay_y = 10
            s = pygame.Surface((overlay_w, overlay_h))
            s.set_alpha(200)
            s.fill((20, 20, 30))
            screen.blit(s, (overlay_x, overlay_y))
            font = pygame.font.SysFont(None, 20)
            title = font.render("TUNING - NPC COLLISION", True, (220,220,220))
            screen.blit(title, (overlay_x + 10, overlay_y + 8))
            y = overlay_y + 36
            for i, p in enumerate(tuning_params):
                name = p['name']
                val = p['value']
                txt = f"{name}: {val}"
                color = (255, 255, 120) if i == tuning_index else (200, 200, 200)
                line = font.render(txt, True, color)
                screen.blit(line, (overlay_x + 12, y))
                y += 26
            hint = font.render("Use F1 to close | D-pad/LB/RB to adjust", True, (160,160,160))
            screen.blit(hint, (overlay_x + 10, overlay_y + overlay_h - 24))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
