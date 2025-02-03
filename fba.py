import pygame
import random
import sys
import sqlite3
import numpy as np
import gym
import cv2
from flask import Flask
from flask_socketio import SocketIO
from stable_baselines3 import PPO
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
import threading
# Initialize Pygame
pygame.init()
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8

# Game Assets
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'

# Flask Server for Multiplayer
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def home():
    return "Flappy Bird AI Server is Running! 🎮"

@socketio.on('connect')
def handle_connect():
    print("A player connected")

@socketio.on('score_update')
def handle_score_update(data):
    print(f"Player {data['player']} scored {data['score']}")
    socketio.emit('score_update', data, broadcast=True)

# SQLite Database for High Scores
conn = sqlite3.connect('flappy_scores.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT,
    score INTEGER
)
''')
conn.commit()

def save_score(name, score):
    cursor.execute("INSERT INTO scores (player_name, score) VALUES (?, ?)", (name, score))
    conn.commit()

def get_top_scores():
    cursor.execute("SELECT * FROM scores ORDER BY score DESC LIMIT 10")
    return cursor.fetchall()

# Neural Network for Dynamic Difficulty
model = Sequential([
    Input(shape=(1,)),
    Dense(8, activation='relu'),
    Dense(4, activation='relu'),
    Dense(1, activation='linear')
])
model.compile(optimizer='adam', loss='mse')
X_train = np.array([0, 5, 10, 20, 30, 50])
y_train = np.array([4, 5, 6, 8, 10, 12])
model.fit(X_train, y_train, epochs=50, verbose=0)

def get_dynamic_pipe_speed(score):
    return model.predict(np.array([[score]]), verbose=0)[0][0]

# AI Player using PPO
class FlappyBirdEnv(gym.Env):
    def __init__(self):
        super(FlappyBirdEnv, self).__init__()
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=(84, 84, 1), dtype=np.uint8)
        self.action_space = gym.spaces.Discrete(2)

    def step(self, action):
        reward = 1
        done = False
        obs = self.get_screen()
        return obs, reward, done, {}

    def reset(self):
        return self.get_screen()

    def get_screen(self):
        screen = pygame.surfarray.array3d(SCREEN)
        screen = np.transpose(screen, (1, 0, 2))
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        screen = cv2.resize(screen, (84, 84))
        screen = np.expand_dims(screen, axis=-1)
        return screen.astype(np.uint8)

env = FlappyBirdEnv()
ai_model = PPO("CnnPolicy", env, verbose=1)
ai_model.learn(total_timesteps=5)
ai_model.save("flappy_ai")

# Power-Ups & Moving Pipes
class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.active = True

    def apply(self):
        if self.type == "shield":
            return "Shield Activated!"
        elif self.type == "slow_motion":
            return "Slow Motion Activated!"

    def update(self):
        self.x -= 3
        if self.x < -20:
            self.active = False

power_ups = [PowerUp(300, random.randint(100, 400), "shield")]

class MovingPipe:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 1

    def update(self):
        self.y += self.direction * 2
        if self.y > SCREENHEIGHT - 150 or self.y < 50:
            self.direction *= -1

# Main Game Loop
def mainGame():
    ai_model = PPO.load("flappy_ai")
    obs = env.reset()

    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENWIDTH / 2)
    basex = 0
    pipeVelX = -get_dynamic_pipe_speed(score)
    playerVelY = -9
    playerAccY = 1
    playerFlapAccv = -8
    playerFlapped = False

    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()
    upperPipes = [{'x': SCREENWIDTH+200, 'y': newPipe1[0]['y']}, {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y': newPipe2[0]['y']}]
    lowerPipes = [{'x': SCREENWIDTH+200, 'y': newPipe1[1]['y']}, {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y': newPipe2[1]['y']}]

    while True:
        action, _states = ai_model.predict(obs)
        if action == 1 and playery > 0:
            playerVelY = playerFlapAccv
            playerFlapped = True
            GAME_SOUNDS['wing'].play()

        if playerFlapped:
            playerFlapped = False
        playery = playery + min(playerVelY, GROUNDY - playery - 25)

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest:
            obs = env.reset()
            score = 0
            continue

        score += 1
        pipeVelX = -get_dynamic_pipe_speed(score)

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        pygame.display.update()
        pygame.time.Clock().tick(FPS)

def isCollide(playerx, playery, upperPipes, lowerPipes):
    return playery > GROUNDY - 25 or playery < 0

def getRandomPipe():
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    return [{'x': pipeX, 'y': -y1}, {'x': pipeX, 'y': y2}]
def load_game_assets():
    """Load all game assets (sprites & sounds) before starting the game."""
    global GAME_SPRITES, GAME_SOUNDS

    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )

    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha()
    )

    # Load game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    print("Game assets loaded successfully!")

if __name__ == '__main__':
     # Start Flask Server in Background
    threading.Thread(target=lambda: socketio.run(app, port=5050, use_reloader=False, allow_unsafe_werkzeug=True, host='0.0.0.0', debug=True), daemon=True).start()
    load_game_assets()
    mainGame()
