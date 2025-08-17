#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import os
import random

# 初始化pygame
pygame.init()

# 确保资源目录存在
resources_dir = 'resources'
images_dir = os.path.join(resources_dir, 'images')
sounds_dir = os.path.join(resources_dir, 'sounds')

if not os.path.exists(resources_dir):
    os.makedirs(resources_dir)
if not os.path.exists(images_dir):
    os.makedirs(images_dir)
if not os.path.exists(sounds_dir):
    os.makedirs(sounds_dir)

# 创建背景图像
def create_background():
    """创建简单的星空背景"""
    bg_size = (480, 700)
    bg = pygame.Surface(bg_size)
    bg.fill((0, 0, 30))  # 深蓝色背景
    
    # 添加一些星星
    for _ in range(100):
        x = random.randint(0, bg_size[0])
        y = random.randint(0, bg_size[1])
        radius = random.randint(1, 2)
        brightness = random.randint(150, 255)
        pygame.draw.circle(bg, (brightness, brightness, brightness), (x, y), radius)
    
    # 保存背景图像
    pygame.image.save(bg, os.path.join(images_dir, 'background.png'))
    print("背景图像已创建")

# 创建玩家飞机图像
def create_player():
    """创建玩家飞机图像"""
    player_size = (50, 40)
    player = pygame.Surface(player_size, pygame.SRCALPHA)
    
    # 飞机主体（三角形）
    pygame.draw.polygon(player, (200, 200, 255), [(25, 0), (0, 40), (50, 40)])
    
    # 飞机座舱
    pygame.draw.ellipse(player, (100, 100, 200), (15, 15, 20, 20))
    
    # 飞机引擎
    pygame.draw.rect(player, (255, 100, 100), (20, 35, 10, 5))
    
    # 保存玩家飞机图像
    pygame.image.save(player, os.path.join(images_dir, 'player.png'))
    print("玩家飞机图像已创建")

# 创建敌机图像
def create_enemy():
    """创建敌机图像"""
    enemy_size = (30, 30)
    enemy = pygame.Surface(enemy_size, pygame.SRCALPHA)
    
    # 敌机主体（圆形）
    pygame.draw.circle(enemy, (255, 100, 100), (15, 15), 15)
    
    # 敌机内部
    pygame.draw.circle(enemy, (200, 50, 50), (15, 15), 10)
    pygame.draw.circle(enemy, (150, 0, 0), (15, 15), 5)
    
    # 保存敌机图像
    pygame.image.save(enemy, os.path.join(images_dir, 'enemy.png'))
    print("敌机图像已创建")

# 创建子弹图像
def create_bullet():
    """创建子弹图像"""
    bullet_size = (5, 10)
    bullet = pygame.Surface(bullet_size, pygame.SRCALPHA)
    
    # 子弹主体（椭圆）
    pygame.draw.ellipse(bullet, (255, 255, 100), (0, 0, 5, 10))
    
    # 保存子弹图像
    pygame.image.save(bullet, os.path.join(images_dir, 'bullet.png'))
    print("子弹图像已创建")

# 创建爆炸效果图像序列
def create_explosion():
    """创建爆炸效果图像序列"""
    explosion_frames = 8
    base_size = 5
    
    for i in range(explosion_frames):
        size = base_size + i * 5
        explosion = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 爆炸效果（渐变圆形）
        color_value = 255 - i * 20
        if color_value < 0:
            color_value = 0
        
        pygame.draw.circle(explosion, (255, color_value, 0), (size//2, size//2), size//2)
        
        # 保存爆炸效果图像
        pygame.image.save(explosion, os.path.join(images_dir, f'explosion{i}.png'))
    
    print("爆炸效果图像序列已创建")

# 主函数
def main():
    create_background()
    create_player()
    create_enemy()
    create_bullet()
    create_explosion()
    print("所有资源创建完成")

if __name__ == "__main__":
    main()