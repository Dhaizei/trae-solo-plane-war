#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import random
from sprites import Player, Enemy, Bullet, Explosion
from sounds import SoundManager

# 游戏状态常量
GAME_INIT = 0  # 游戏初始化
GAME_START = 1  # 游戏开始
GAME_OVER = 2  # 游戏结束
GAME_PAUSED = 3  # 游戏暂停

# 游戏常量
FPS = 60

class GameLogic:
    """游戏逻辑管理类，负责处理游戏核心逻辑"""
    
    def __init__(self, sound_manager=None):
        """初始化游戏逻辑"""
        # 游戏状态
        self.game_status = GAME_INIT
        self.show_instructions = False  # 是否显示操作说明
        
        # 游戏分数和生命
        self.score = 0
        
        # 音效管理器
        self.sound_manager = sound_manager
        self.sound_enabled = sound_manager is not None
        
        # 敌机生成相关
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 60  # 初始敌机生成间隔
        self.base_enemy_spawn_delay = 60  # 基础敌机生成间隔
        self.difficulty_level = 1  # 难度等级
        
        # 精灵组
        self.all_sprites = None
        self.enemies = None
        self.bullets = None
        self.explosions = None
        self.player = None
    
    def start_game(self):
        """开始游戏"""
        self.game_status = GAME_START
        self.score = 0
        
        # 重置敌机生成相关参数
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 60
        self.base_enemy_spawn_delay = 60
        self.difficulty_level = 1
        
        # 创建精灵组
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        
        # 创建玩家飞机
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # 创建初始敌机
        for i in range(8):
            self.spawn_enemy()
    
    def game_over(self):
        """游戏结束"""
        self.game_status = GAME_OVER
    
    def toggle_pause(self):
        """切换暂停状态"""
        if self.game_status == GAME_START:
            self.game_status = GAME_PAUSED
        elif self.game_status == GAME_PAUSED:
            self.game_status = GAME_START
    
    def toggle_instructions(self):
        """切换操作说明显示"""
        if self.game_status in [GAME_INIT, GAME_OVER]:
            self.show_instructions = not self.show_instructions
    
    def update(self):
        """更新游戏状态"""
        if self.game_status == GAME_START:
            # 更新难度等级
            self.update_difficulty()
            
            # 更新所有精灵
            self.all_sprites.update()
            
            # 生成敌机
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.enemy_spawn_delay:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
    
    def handle_player_shooting(self, is_shooting):
        """处理玩家射击"""
        if self.game_status == GAME_START and is_shooting and self.player:
            bullet = self.player.shoot()
            if bullet:
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
                # 播放射击音效
                if self.sound_enabled and self.sound_manager:
                    self.sound_manager.play_sound('shoot')
    
    def check_collisions(self):
        """检测碰撞"""
        if self.game_status != GAME_START:
            return
        
        # 检测子弹与敌机的碰撞
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, False)
        for bullet, enemy_list in hits.items():
            for enemy in enemy_list:
                # 敌机被击中
                if enemy.hit():  # 如果敌机被摧毁
                    self.score += enemy.score_value
                    enemy.kill()
                    
                    # 播放爆炸音效
                    if self.sound_enabled and self.sound_manager:
                        self.sound_manager.play_sound('explosion')
                    
                    # 创建爆炸效果
                    explosion = Explosion(enemy.rect.center)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)
                    
                    # 生成新的敌机
                    self.spawn_enemy()
                else:
                    # 敌机受伤但未被摧毁，设置受伤效果定时器
                    pygame.time.set_timer(pygame.USEREVENT + 1, 200)  # 200ms后恢复
        
        # 检测玩家与敌机的碰撞
        if self.player:
            hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
            for hit in hits:
                if self.player.hit():
                    # 创建爆炸效果
                    explosion = Explosion(hit.rect.center)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)
                    # 播放被击中音效
                    if self.sound_enabled and self.sound_manager:
                        self.sound_manager.play_sound('hit')
                
                # 生成新的敌机
                self.spawn_enemy()
                
                # 检查游戏是否结束
                if self.player.lives <= 0:
                    self.game_over()
                    # 播放游戏结束音效
                    if self.sound_enabled and self.sound_manager:
                        self.sound_manager.play_sound('game_over')
    
    def update_difficulty(self):
        """根据分数更新游戏难度"""
        # 每100分提升一个难度等级
        new_difficulty = (self.score // 100) + 1
        
        if new_difficulty != self.difficulty_level:
            self.difficulty_level = new_difficulty
            
            # 调整敌机生成频率（最快每20帧生成一个）
            self.enemy_spawn_delay = max(20, self.base_enemy_spawn_delay - (self.difficulty_level - 1) * 5)
            
            # 调整敌机速度（通过修改Enemy类的速度）
            Enemy.base_speed = min(8, 2 + (self.difficulty_level - 1) * 0.5)
    
    def spawn_enemy(self):
        """生成敌机"""
        # 根据难度等级决定敌机类型
        enemy_types = ["normal", "fast", "heavy"]
        
        # 基础概率：普通敌机70%，快速敌机20%，重型敌机10%
        if self.difficulty_level <= 2:
            # 低难度主要是普通敌机
            enemy_type = random.choices(enemy_types, weights=[80, 15, 5])[0]
        elif self.difficulty_level <= 5:
            # 中等难度增加特殊敌机
            enemy_type = random.choices(enemy_types, weights=[60, 25, 15])[0]
        else:
            # 高难度更多特殊敌机
            enemy_type = random.choices(enemy_types, weights=[50, 30, 20])[0]
        
        enemy = Enemy(enemy_type)
        if self.all_sprites and self.enemies:
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
    
    def handle_enemy_damage_recovery(self):
        """处理敌机受伤后的恢复"""
        # 恢复受伤敌机的透明度
        if self.enemies:
            for enemy in self.enemies:
                if enemy.health > 0:
                    enemy.image.set_alpha(255)
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # 取消定时器
    
    def get_game_data(self):
        """获取游戏数据用于渲染"""
        return {
            'game_status': self.game_status,
            'show_instructions': self.show_instructions,
            'score': self.score,
            'difficulty_level': self.difficulty_level,
            'player_lives': self.player.lives if self.player else 0,
            'all_sprites': self.all_sprites,
            'player': self.player
        }