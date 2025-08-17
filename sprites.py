#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import random
import os
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, YELLOW, BLUE,
    PLAYER_SPEED, PLAYER_LIVES, PLAYER_INVINCIBLE_TIME, PLAYER_SHOOT_COOLDOWN,
    ENEMY_BASE_SPEED, ENEMY_TYPES, BULLET_SPEED, BULLET_SIZE, BULLET_COLOR,
    IMAGE_FILES
)

class Player(pygame.sprite.Sprite):
    """玩家飞机类"""
    
    def __init__(self):
        """初始化玩家飞机"""
        pygame.sprite.Sprite.__init__(self)
        
        # 加载玩家飞机图像
        player_img_path = IMAGE_FILES['player']
        if os.path.exists(player_img_path):
            self.image = pygame.image.load(player_img_path).convert_alpha()
        else:
            # 如果图像不存在，使用矩形代替
            self.image = pygame.Surface((50, 40))
            self.image.fill(WHITE)
        
        self.rect = self.image.get_rect()
        
        # 设置初始位置在屏幕底部中央
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        
        # 设置飞机速度
        self.speed = PLAYER_SPEED
        
        # 设置生命值
        self.lives = PLAYER_LIVES
        
        # 设置无敌时间（毫秒）
        self.invincible = False
        self.invincible_time = 0
        
        # 射击冷却时间
        self.shoot_cooldown = 0
    
    def update(self):
        """更新玩家飞机状态"""
        # 处理无敌状态
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_time > PLAYER_INVINCIBLE_TIME:
                self.invincible = False
        
        # 处理射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # 获取按键状态
        keystate = pygame.key.get_pressed()
        
        # 左右移动
        if keystate[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keystate[pygame.K_RIGHT]:
            self.rect.x += self.speed
        
        # 上下移动
        if keystate[pygame.K_UP]:
            self.rect.y -= self.speed
        if keystate[pygame.K_DOWN]:
            self.rect.y += self.speed
        
        # 限制飞机在屏幕内
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
    
    def shoot(self):
        """发射子弹"""
        if self.shoot_cooldown <= 0:
            # 创建子弹
            bullet = Bullet(self.rect.centerx, self.rect.top)
            self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN  # 设置射击冷却时间
            return bullet
        return None
    
    def hit(self):
        """被击中"""
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_time = pygame.time.get_ticks()
            return True
        return False

class Enemy(pygame.sprite.Sprite):
    """敌机基类"""
    base_speed = ENEMY_BASE_SPEED  # 基础速度，可以被动态调整
    
    def __init__(self, enemy_type="normal"):
        """初始化敌机"""
        pygame.sprite.Sprite.__init__(self)
        
        self.enemy_type = enemy_type
        self.setup_enemy_properties()
        
        # 设置位置
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        
        # 设置移动速度
        self.speed_y = self.base_speed_y + random.randrange(0, 2)
        self.speed_x = random.randrange(-1, 2)
    
    def setup_enemy_properties(self):
        """根据敌机类型设置属性"""
        enemy_config = ENEMY_TYPES.get(self.enemy_type, ENEMY_TYPES['normal'])
        
        # 加载敌机图像
        if self.enemy_type == "normal":
            enemy_img_path = IMAGE_FILES['enemy']
        else:
            enemy_img_path = IMAGE_FILES.get(f'enemy_{self.enemy_type}', IMAGE_FILES['enemy'])
            
        if os.path.exists(enemy_img_path):
            self.image = pygame.image.load(enemy_img_path).convert_alpha()
        else:
            # 使用配置中的尺寸和颜色创建矩形
            self.image = pygame.Surface(enemy_config['size'])
            self.image.fill(enemy_config['color'])
        
        # 设置敌机属性
        self.base_speed_y = Enemy.base_speed + enemy_config['speed_modifier']
        self.health = enemy_config['health']
        self.score_value = enemy_config['score_value']
    
    def update(self):
        """更新敌机位置"""
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        # 边界检查，防止敌机飞出屏幕两侧
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x = -self.speed_x
        
        # 如果敌机移出屏幕底部，删除它
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
    
    def hit(self):
        """敌机被击中"""
        self.health -= 1
        if self.health <= 0:
            return True  # 敌机被摧毁
        else:
            # 受伤效果 - 闪烁
            self.image.set_alpha(128)
            return False  # 敌机未被摧毁

class Bullet(pygame.sprite.Sprite):
    """子弹类"""
    
    def __init__(self, x, y):
        """初始化子弹"""
        pygame.sprite.Sprite.__init__(self)
        
        # 加载子弹图像
        bullet_img_path = IMAGE_FILES['bullet']
        if os.path.exists(bullet_img_path):
            self.image = pygame.image.load(bullet_img_path).convert_alpha()
        else:
            # 如果图像不存在，使用矩形代替
            self.image = pygame.Surface(BULLET_SIZE)
            self.image.fill(BULLET_COLOR)  # 使用配置中的子弹颜色
        
        self.rect = self.image.get_rect()
        
        # 设置子弹位置
        self.rect.centerx = x
        self.rect.bottom = y
        
        # 设置子弹速度
        self.speed = -BULLET_SPEED  # 负值表示向上移动
    
    def update(self):
        """更新子弹状态"""
        # 移动子弹
        self.rect.y += self.speed
        
        # 如果子弹飞出屏幕顶部，删除子弹
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    """爆炸效果类"""
    
    def __init__(self, center):
        """初始化爆炸效果"""
        pygame.sprite.Sprite.__init__(self)
        
        # 加载爆炸效果图像序列
        self.explosion_anim = []
        for i in range(8):
            img_path = os.path.join('resources', 'images', f'explosion{i}.png')
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert_alpha()
                self.explosion_anim.append(img)
        
        # 如果没有找到图像，使用简单的圆形代替
        if not self.explosion_anim:
            self.size = 5
            self.image = pygame.Surface((self.size, self.size))
            self.image.fill(RED)
            self.use_animation = False
        else:
            self.image = self.explosion_anim[0]
            self.use_animation = True
        
        self.rect = self.image.get_rect()
        self.rect.center = center
        
        # 设置帧计数器
        self.frame = 0
        self.frame_rate = 2  # 动画速度
        self.last_update = pygame.time.get_ticks()
    
    def update(self):
        """更新爆炸效果"""
        if self.use_animation:
            # 基于时间的动画更新
            now = pygame.time.get_ticks()
            if now - self.last_update > 50:  # 每50毫秒更新一帧
                self.last_update = now
                self.frame += 1
                if self.frame < len(self.explosion_anim):
                    center = self.rect.center
                    self.image = self.explosion_anim[self.frame]
                    self.rect = self.image.get_rect()
                    self.rect.center = center
                else:
                    self.kill()  # 爆炸效果结束，删除精灵
        else:
            # 使用简单的圆形动画
            self.frame += 1
            if self.frame <= 8:
                self.size = 5 + self.frame * 2
                center = self.rect.center
                self.image = pygame.Surface((self.size, self.size))
                self.image.fill(RED)
                self.rect = self.image.get_rect()
                self.rect.center = center
            else:
                self.kill()  # 爆炸效果结束，删除精灵