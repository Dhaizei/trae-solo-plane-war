#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import sys
from game_logic import GameLogic, GAME_INIT, GAME_START, GAME_OVER, GAME_PAUSED, FPS
from renderer import Renderer
from input_handler import InputHandler

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
        
        # 设置敌机受伤效果计时器
        pygame.time.set_timer(pygame.USEREVENT + 1, 100)  # 每100ms检查一次
    

    

    

    

    

    
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            # 处理输入事件
            self.input_handler.handle_events()
            
            # 更新持续输入（移动和射击）
            self.input_handler.update_continuous_input()
            
            # 更新游戏逻辑
            self.game_logic.update()
            
            # 渲染游戏画面
            game_data = self.game_logic.get_game_data()
            self.renderer.render(game_data)
            
            # 控制帧率
            self.clock.tick(FPS)



# 游戏入口
if __name__ == "__main__":
    game = Game()
    game.run()