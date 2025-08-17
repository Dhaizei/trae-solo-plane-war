#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import sys
from game_logic import GameLogic, GAME_INIT, GAME_START, GAME_OVER, GAME_PAUSED, FPS
from renderer import Renderer
from input_handler import InputHandler
from state_manager import GameState, StateManager

class Game:
    """游戏主类 - 重构后的简化版本"""
    
    def __init__(self):
        """初始化游戏"""
        pygame.init()
        
        # 设置窗口
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("飞机大战")
        
        # 设置时钟
        self.clock = pygame.time.Clock()
        
        # 初始化各个模块
        self.game_logic = GameLogic()
        self.renderer = Renderer(self.screen)
        self.input_handler = InputHandler(self.game_logic)
        
        # 获取状态管理器的引用
        self.state_manager = self.game_logic.state_manager
        
        # 设置敌机受伤效果计时器
        pygame.time.set_timer(pygame.USEREVENT + 1, 100)  # 每100ms检查一次
    

    

    

    

    

    
    def run(self):
        """运行游戏主循环 - 使用状态机模式"""
        running = True
        
        while running:
            # 处理输入事件
            quit_requested = self.input_handler.handle_events()
            if quit_requested:
                running = False
                break
            
            # 根据当前状态执行不同的逻辑
            current_state = self.state_manager.get_current_state()
            
            if current_state == GameState.INIT:
                # 初始化状态：等待用户开始游戏
                pass
            elif current_state == GameState.PLAYING:
                # 游戏进行状态：更新游戏逻辑
                self.input_handler.update_continuous_input()
                self.game_logic.update()
            elif current_state == GameState.PAUSED:
                # 暂停状态：不更新游戏逻辑，只处理输入
                pass
            elif current_state == GameState.GAME_OVER:
                # 游戏结束状态：等待重新开始或退出
                pass
            elif current_state == GameState.INSTRUCTIONS:
                # 操作说明状态：显示说明
                pass
            
            # 渲染游戏画面（所有状态都需要渲染）
            game_data = self.game_logic.get_game_data()
            # 添加状态信息到游戏数据中
            game_data['current_state'] = current_state
            game_data['state_manager'] = self.state_manager
            self.renderer.render(game_data)
            
            # 控制帧率
            self.clock.tick(FPS)



# 游戏入口
if __name__ == "__main__":
    game = Game()
    game.run()