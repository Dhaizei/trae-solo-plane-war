#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import random
from sprites import Player, Enemy, Bullet, Explosion
from sounds import SoundManager
from state_manager import StateManager, GameState
from object_pool import PoolManager
from config import FPS, ENEMY_SPAWN_DELAY, DIFFICULTY_INCREASE_INTERVAL

# 保持向后兼容的游戏状态常量
GAME_INIT = 0  # 游戏初始化
GAME_START = 1  # 游戏开始
GAME_OVER = 2  # 游戏结束
GAME_PAUSED = 3  # 游戏暂停

class GameLogic:
    """游戏逻辑管理类，负责处理游戏核心逻辑"""
    
    def __init__(self, sound_manager=None):
        """初始化游戏逻辑"""
        # 状态管理器
        self.state_manager = StateManager(GameState.INIT)
        
        # 保持向后兼容的游戏状态
        self.game_status = GAME_INIT
        self.show_instructions = False  # 是否显示操作说明
        
        # 注册状态变化回调
        self._register_state_callbacks()
        
        # 游戏分数和生命
        self.score = 0
        
        # 音效管理器
        self.sound_manager = sound_manager
        self.sound_enabled = sound_manager is not None
        
        # 对象池管理器
        self.pool_manager = PoolManager()
        
        # 敌机生成相关
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = ENEMY_SPAWN_DELAY  # 初始敌机生成间隔
        self.base_enemy_spawn_delay = ENEMY_SPAWN_DELAY  # 基础敌机生成间隔
        self.difficulty_level = 1  # 难度等级
        
        # 精灵组
        self.all_sprites = None
        self.enemies = None
        self.bullets = None
        self.explosions = None
        self.player = None
    
    def _register_state_callbacks(self):
        """注册状态变化回调函数"""
        # 注册进入游戏状态的回调
        self.state_manager.register_enter_callback(GameState.PLAYING, self._on_enter_playing)
        self.state_manager.register_enter_callback(GameState.PAUSED, self._on_enter_paused)
        self.state_manager.register_enter_callback(GameState.GAME_OVER, self._on_enter_game_over)
        self.state_manager.register_enter_callback(GameState.INSTRUCTIONS, self._on_enter_instructions)
        
        # 注册退出游戏状态的回调
        self.state_manager.register_exit_callback(GameState.PLAYING, self._on_exit_playing)
        self.state_manager.register_exit_callback(GameState.PAUSED, self._on_exit_paused)
    
    def _on_enter_playing(self):
        """进入游戏状态时的回调"""
        print("进入游戏状态")
    
    def _on_enter_paused(self):
        """进入暂停状态时的回调"""
        print("游戏暂停")
    
    def _on_enter_game_over(self):
        """进入游戏结束状态时的回调"""
        print("游戏结束")
    
    def _on_enter_instructions(self):
        """进入操作说明状态时的回调"""
        print("显示操作说明")
    
    def _on_exit_playing(self):
        """退出游戏状态时的回调"""
        print("退出游戏状态")
    
    def _on_exit_paused(self):
        """退出暂停状态时的回调"""
        print("退出暂停状态")
    
    def start_game(self):
        """开始游戏"""
        # 使用状态管理器开始游戏
        if self.state_manager.start_game():
            self.game_status = GAME_START
            self.score = 0
        
        # 重置敌机生成相关参数
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = ENEMY_SPAWN_DELAY
        self.base_enemy_spawn_delay = ENEMY_SPAWN_DELAY
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
        # 使用状态管理器结束游戏
        if self.state_manager.end_game():
            self.game_status = GAME_OVER
            
            # 清理所有精灵并返回到对象池
            if self.bullets:
                for bullet in self.bullets.copy():
                    bullet.kill()
                    self.pool_manager.return_bullet(bullet)
            
            if self.enemies:
                for enemy in self.enemies.copy():
                    enemy.kill()
                    self.pool_manager.return_enemy(enemy)
    
    def toggle_pause(self):
        """切换暂停状态"""
        # 使用状态管理器切换暂停状态
        if self.state_manager.toggle_pause():
            if self.state_manager.is_playing():
                self.game_status = GAME_START
            elif self.state_manager.is_paused():
                self.game_status = GAME_PAUSED
    
    def toggle_instructions(self):
        """切换操作说明显示"""
        if self.state_manager.is_state(GameState.INSTRUCTIONS):
            # 如果当前在说明页面，返回到之前的状态
            if self.state_manager.previous_state == GameState.INIT:
                self.state_manager.transition_to(GameState.INIT)
                self.game_status = GAME_INIT
            elif self.state_manager.previous_state == GameState.GAME_OVER:
                self.state_manager.transition_to(GameState.GAME_OVER)
                self.game_status = GAME_OVER
            self.show_instructions = False
        elif self.game_status in [GAME_INIT, GAME_OVER]:
            # 显示操作说明
            if self.state_manager.show_instructions():
                self.show_instructions = True
    
    def update(self):
        """更新游戏状态"""
        # 使用状态管理器检查游戏状态
        if self.state_manager.is_playing():
            # 更新难度等级
            self.update_difficulty()
            
            # 更新所有精灵
            self.all_sprites.update()
            
            # 清理超出屏幕的精灵
            self.cleanup_offscreen_sprites()
            
            # 生成敌机
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.enemy_spawn_delay:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
    
    def handle_player_shooting(self, is_shooting):
        """处理玩家射击"""
        if self.state_manager.is_playing() and is_shooting and self.player and self.player.can_shoot():
            # 从对象池获取子弹
            bullet = self.pool_manager.get_bullet(self.player.rect.centerx, self.player.rect.top)
            if bullet:
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
                # 播放射击音效
                if self.sound_enabled and self.sound_manager:
                    self.sound_manager.play_sound('shoot')
                # 重置射击冷却
                self.player.reset_shoot_cooldown()
    
    def check_collisions(self):
        """检测碰撞"""
        if not self.state_manager.is_playing():
            return
        
        # 检测子弹与敌机的碰撞
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, False, False)
        for bullet, enemy_list in hits.items():
            for enemy in enemy_list:
                # 敌机被击中
                if enemy.hit():  # 如果敌机被摧毁
                    self.score += enemy.score_value
                    enemy.kill()
                    
                    # 将敌机返回到对象池
                    self.pool_manager.return_enemy(enemy)
                    
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
                
                # 子弹击中敌机后销毁，返回到对象池
                bullet.kill()
                self.pool_manager.return_bullet(bullet)
                break  # 子弹只能击中一个敌机
        
        # 检测玩家与敌机的碰撞
        if self.player:
            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            for hit in hits:
                if self.player.hit():
                    # 创建爆炸效果
                    explosion = Explosion(hit.rect.center)
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)
                    # 播放被击中音效
                    if self.sound_enabled and self.sound_manager:
                        self.sound_manager.play_sound('hit')
                
                # 敌机与玩家碰撞后销毁，返回到对象池
                hit.kill()
                self.pool_manager.return_enemy(hit)
                
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
        
        # 从对象池获取敌机
        enemy = self.pool_manager.get_enemy(enemy_type)
        if enemy and self.all_sprites and self.enemies:
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
    
    def cleanup_offscreen_sprites(self):
        """清理超出屏幕的精灵并返回到对象池"""
        from config import SCREEN_HEIGHT, SCREEN_WIDTH
        
        # 清理超出屏幕的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom < 0 or bullet.rect.top > SCREEN_HEIGHT:
                bullet.kill()
                self.pool_manager.return_bullet(bullet)
        
        # 清理超出屏幕的敌机
        for enemy in self.enemies.copy():
            if enemy.rect.top > SCREEN_HEIGHT or enemy.rect.right < 0 or enemy.rect.left > SCREEN_WIDTH:
                enemy.kill()
                self.pool_manager.return_enemy(enemy)
    
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