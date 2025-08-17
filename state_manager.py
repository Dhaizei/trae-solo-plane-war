#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
from typing import Dict, Callable, Optional

class GameState(Enum):
    """游戏状态枚举"""
    INIT = "init"           # 游戏初始化状态
    MENU = "menu"           # 主菜单状态
    PLAYING = "playing"     # 游戏进行中状态
    PAUSED = "paused"       # 游戏暂停状态
    GAME_OVER = "game_over" # 游戏结束状态
    INSTRUCTIONS = "instructions"  # 操作说明状态

class StateManager:
    """游戏状态管理器
    
    使用状态机模式管理游戏的各种状态，提供状态切换、
    状态验证和状态回调等功能。
    """
    
    def __init__(self, initial_state: GameState = GameState.INIT):
        """初始化状态管理器
        
        Args:
            initial_state: 初始游戏状态，默认为INIT
        """
        self._current_state = initial_state
        self._previous_state = None
        
        # 状态切换回调函数字典
        self._state_enter_callbacks: Dict[GameState, Callable] = {}
        self._state_exit_callbacks: Dict[GameState, Callable] = {}
        
        # 定义允许的状态转换
        self._allowed_transitions = {
            GameState.INIT: [GameState.MENU, GameState.PLAYING],
            GameState.MENU: [GameState.PLAYING, GameState.INSTRUCTIONS],
            GameState.PLAYING: [GameState.PAUSED, GameState.GAME_OVER, GameState.MENU],
            GameState.PAUSED: [GameState.PLAYING, GameState.MENU, GameState.GAME_OVER],
            GameState.GAME_OVER: [GameState.MENU, GameState.PLAYING, GameState.INSTRUCTIONS],
            GameState.INSTRUCTIONS: [GameState.MENU, GameState.GAME_OVER]
        }
    
    @property
    def current_state(self) -> GameState:
        """获取当前状态"""
        return self._current_state
    
    def get_current_state(self) -> GameState:
        """获取当前状态（方法形式）"""
        return self._current_state
    
    @property
    def previous_state(self) -> Optional[GameState]:
        """获取前一个状态"""
        return self._previous_state
    
    def can_transition_to(self, new_state: GameState) -> bool:
        """检查是否可以转换到指定状态
        
        Args:
            new_state: 目标状态
            
        Returns:
            bool: 如果可以转换返回True，否则返回False
        """
        allowed_states = self._allowed_transitions.get(self._current_state, [])
        return new_state in allowed_states
    
    def transition_to(self, new_state: GameState, force: bool = False) -> bool:
        """转换到新状态
        
        Args:
            new_state: 目标状态
            force: 是否强制转换（忽略转换规则）
            
        Returns:
            bool: 转换成功返回True，否则返回False
        """
        # 如果已经是目标状态，直接返回True
        if self._current_state == new_state:
            return True
        
        # 检查转换是否被允许
        if not force and not self.can_transition_to(new_state):
            print(f"警告: 不允许从 {self._current_state.value} 转换到 {new_state.value}")
            return False
        
        # 执行状态退出回调
        if self._current_state in self._state_exit_callbacks:
            try:
                self._state_exit_callbacks[self._current_state]()
            except Exception as e:
                print(f"状态退出回调执行失败: {e}")
        
        # 保存前一个状态
        self._previous_state = self._current_state
        
        # 切换到新状态
        self._current_state = new_state
        
        # 执行状态进入回调
        if new_state in self._state_enter_callbacks:
            try:
                self._state_enter_callbacks[new_state]()
            except Exception as e:
                print(f"状态进入回调执行失败: {e}")
        
        print(f"状态转换: {self._previous_state.value} -> {self._current_state.value}")
        return True
    
    def register_enter_callback(self, state: GameState, callback: Callable):
        """注册状态进入回调函数
        
        Args:
            state: 状态
            callback: 回调函数
        """
        self._state_enter_callbacks[state] = callback
    
    def register_exit_callback(self, state: GameState, callback: Callable):
        """注册状态退出回调函数
        
        Args:
            state: 状态
            callback: 回调函数
        """
        self._state_exit_callbacks[state] = callback
    
    def is_state(self, state: GameState) -> bool:
        """检查当前是否为指定状态
        
        Args:
            state: 要检查的状态
            
        Returns:
            bool: 如果当前状态匹配返回True，否则返回False
        """
        return self._current_state == state
    
    def is_playing(self) -> bool:
        """检查游戏是否正在进行中"""
        return self._current_state == GameState.PLAYING
    
    def is_paused(self) -> bool:
        """检查游戏是否暂停"""
        return self._current_state == GameState.PAUSED
    
    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        return self._current_state == GameState.GAME_OVER
    
    def toggle_pause(self) -> bool:
        """切换暂停状态
        
        Returns:
            bool: 切换成功返回True，否则返回False
        """
        if self._current_state == GameState.PLAYING:
            return self.transition_to(GameState.PAUSED)
        elif self._current_state == GameState.PAUSED:
            return self.transition_to(GameState.PLAYING)
        return False
    
    def start_game(self) -> bool:
        """开始游戏
        
        Returns:
            bool: 开始成功返回True，否则返回False
        """
        return self.transition_to(GameState.PLAYING)
    
    def end_game(self) -> bool:
        """结束游戏
        
        Returns:
            bool: 结束成功返回True，否则返回False
        """
        return self.transition_to(GameState.GAME_OVER)
    
    def show_menu(self) -> bool:
        """显示主菜单
        
        Returns:
            bool: 显示成功返回True，否则返回False
        """
        return self.transition_to(GameState.MENU)
    
    def show_instructions(self) -> bool:
        """显示操作说明
        
        Returns:
            bool: 显示成功返回True，否则返回False
        """
        return self.transition_to(GameState.INSTRUCTIONS)
    
    def get_state_info(self) -> Dict[str, str]:
        """获取状态信息
        
        Returns:
            Dict[str, str]: 包含当前状态和前一个状态的字典
        """
        return {
            "current": self._current_state.value,
            "previous": self._previous_state.value if self._previous_state else None
        }