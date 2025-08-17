#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import sys
from game_logic import GAME_START, GAME_PAUSED, GAME_INIT, GAME_OVER
from state_manager import GameState

class InputHandler:
    """输入处理类，负责处理用户输入和游戏控制"""
    
    def __init__(self, game_logic):
        """初始化输入处理器"""
        self.game_logic = game_logic
        self.keys_pressed = set()  # 当前按下的键
    
    def handle_events(self):
        """处理游戏事件"""
        quit_requested = False
        
        for event in pygame.event.get():
            # 退出游戏
            if event.type == pygame.QUIT:
                quit_requested = True
            
            # 处理按键按下事件
            elif event.type == pygame.KEYDOWN:
                if self._handle_keydown(event):
                    quit_requested = True
            
            # 处理按键释放事件
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event)
            
            # 处理自定义事件
            elif event.type == pygame.USEREVENT + 1:
                # 恢复受伤敌机的透明度
                self.game_logic.handle_enemy_damage_recovery()
        
        return quit_requested
    
    def _handle_keydown(self, event):
        """处理按键按下事件"""
        key = event.key
        quit_requested = False
        
        # 添加到按下的键集合
        self.keys_pressed.add(key)
        
        # 获取当前状态
        current_state = self.game_logic.state_manager.get_current_state()
        
        # ESC键退出游戏
        if key == pygame.K_ESCAPE:
            quit_requested = True
        
        # 空格键开始游戏或射击
        elif key == pygame.K_SPACE:
            if current_state in [GameState.INIT, GameState.GAME_OVER]:
                self.game_logic.start_game()
        
        # P键暂停/继续游戏
        elif key == pygame.K_p:
            if current_state in [GameState.PLAYING, GameState.PAUSED]:
                self.game_logic.toggle_pause()
        
        # H键切换操作说明显示
        elif key == pygame.K_h:
            if current_state in [GameState.INIT, GameState.GAME_OVER]:
                self.game_logic.toggle_instructions()
        
        return quit_requested
    
    def _handle_keyup(self, event):
        """处理按键释放事件"""
        key = event.key
        
        # 从按下的键集合中移除
        self.keys_pressed.discard(key)
    
    def update_continuous_input(self):
        """更新持续输入（如移动和射击）"""
        # 只有在游戏进行状态才处理持续输入
        if not self.game_logic.state_manager.is_playing():
            return
        
        # 获取当前按键状态
        keystate = pygame.key.get_pressed()
        
        # 处理玩家移动
        self._handle_player_movement(keystate)
        
        # 处理玩家射击
        self._handle_player_shooting(keystate)
    
    def _handle_player_movement(self, keystate):
        """处理玩家移动"""
        # Player类的移动逻辑已经在其update方法中处理
        # 这里不需要额外的移动调用，因为Player.update()会自动处理按键状态
        pass
    
    def _handle_player_shooting(self, keystate):
        """处理玩家射击"""
        # 空格键射击
        is_shooting = keystate[pygame.K_SPACE]
        self.game_logic.handle_player_shooting(is_shooting)
    
    def _quit_game(self):
        """退出游戏"""
        pygame.quit()
        sys.exit()
    
    def is_key_pressed(self, key):
        """检查指定键是否被按下"""
        return key in self.keys_pressed
    
    def get_pressed_keys(self):
        """获取当前按下的所有键"""
        return self.keys_pressed.copy()