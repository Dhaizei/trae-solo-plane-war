#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏配置文件
统一管理所有游戏常量和配置参数
"""

# ==================== 屏幕设置 ====================
SCREEN_WIDTH = 480      # 屏幕宽度
SCREEN_HEIGHT = 700     # 屏幕高度
FPS = 60               # 游戏帧率

# ==================== 颜色常量 ====================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)

# ==================== 玩家设置 ====================
PLAYER_SPEED = 8        # 玩家飞机移动速度
PLAYER_LIVES = 3        # 玩家初始生命值
PLAYER_INVINCIBLE_TIME = 3000  # 无敌时间（毫秒）
PLAYER_SHOOT_COOLDOWN = 10     # 射击冷却时间（帧数）

# ==================== 敌机设置 ====================
ENEMY_BASE_SPEED = 2    # 敌机基础移动速度
ENEMY_SPAWN_DELAY = 60  # 敌机生成间隔（帧数）
ENEMY_INITIAL_COUNT = 8 # 初始敌机数量

# 敌机类型配置
ENEMY_TYPES = {
    'normal': {
        'health': 1,
        'speed_modifier': 0,
        'score_value': 10,
        'color': RED,
        'size': (40, 30)
    },
    'fast': {
        'health': 1,
        'speed_modifier': 2,
        'score_value': 20,
        'color': YELLOW,
        'size': (35, 25)
    },
    'heavy': {
        'health': 3,
        'speed_modifier': -1,
        'score_value': 50,
        'color': BLUE,
        'size': (50, 40)
    }
}

# ==================== 子弹设置 ====================
BULLET_SPEED = 10       # 子弹移动速度
BULLET_SIZE = (5, 10)   # 子弹尺寸
BULLET_COLOR = YELLOW   # 子弹颜色

# ==================== 音效设置 ====================
SOUND_VOLUME = 0.5      # 音效音量
MUSIC_VOLUME = 0.7      # 背景音乐音量
SOUND_FREQUENCY = 440   # 音效基础频率
SOUND_SAMPLE_RATE = 22050  # 音频采样率
SOUND_BUFFER_SIZE = 512    # 音频缓冲区大小

# ==================== 游戏难度设置 ====================
DIFFICULTY_INCREASE_SCORE = 1000  # 每增加多少分提升一次难度
DIFFICULTY_INCREASE_INTERVAL = 1000  # 难度提升间隔分数
MAX_DIFFICULTY_LEVEL = 10         # 最大难度等级
DIFFICULTY_SPEED_MULTIPLIER = 0.1 # 难度对速度的影响系数
DIFFICULTY_SPAWN_MULTIPLIER = 0.9 # 难度对生成间隔的影响系数

# ==================== 文件路径设置 ====================
RESOURCES_DIR = 'resources'
IMAGES_DIR = 'resources/images'
SOUNDS_DIR = 'resources/sounds'

# 图片文件路径
IMAGE_FILES = {
    'player': 'resources/images/player.png',
    'enemy': 'resources/images/enemy.png',
    'enemy_fast': 'resources/images/enemy_fast.png',
    'enemy_heavy': 'resources/images/enemy_heavy.png',
    'bullet': 'resources/images/bullet.png',
    'background': 'resources/images/background.png',
    'explosion': [
        'resources/images/explosion0.png',
        'resources/images/explosion1.png',
        'resources/images/explosion2.png',
        'resources/images/explosion3.png',
        'resources/images/explosion4.png',
        'resources/images/explosion5.png',
        'resources/images/explosion6.png',
        'resources/images/explosion7.png'
    ]
}

# 音效文件路径
SOUND_FILES = {
    'shoot': 'resources/sounds/shoot.wav',
    'explosion': 'resources/sounds/explosion.wav',
    'hit': 'resources/sounds/hit.wav',
    'game_over': 'resources/sounds/game_over.wav',
    'level_up': 'resources/sounds/level_up.wav'
}

# ==================== 字体设置 ====================
FONT_SIZE_SMALL = 24
FONT_SIZE_MEDIUM = 36
FONT_SIZE_LARGE = 48
FONT_SIZE_XLARGE = 72

# 字体文件候选列表
FONT_CANDIDATES = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    '/System/Library/Fonts/Arial.ttf',  # macOS
    'C:/Windows/Fonts/arial.ttf',       # Windows
]

# ==================== 游戏状态常量 ====================
# 保持向后兼容的游戏状态常量
GAME_INIT = 0    # 游戏初始化
GAME_START = 1   # 游戏开始
GAME_OVER = 2    # 游戏结束
GAME_PAUSED = 3  # 游戏暂停

# ==================== UI设置 ====================
UI_MARGIN = 10          # UI元素边距
UI_PANEL_HEIGHT = 60    # UI面板高度
UI_TEXT_COLOR = WHITE   # UI文字颜色
UI_BACKGROUND_COLOR = (0, 0, 0, 128)  # UI背景颜色（半透明）

# ==================== 特效设置 ====================
EXPLOSION_FRAME_DURATION = 5  # 爆炸动画每帧持续时间（帧数）
HIT_FLASH_DURATION = 100       # 受伤闪烁持续时间（毫秒）
HIT_FLASH_ALPHA = 128          # 受伤时的透明度

# ==================== 调试设置 ====================
DEBUG_MODE = False      # 是否开启调试模式
SHOW_FPS = False        # 是否显示FPS
SHOW_STATE_INFO = False # 是否显示状态信息