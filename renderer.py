#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import os
from game_logic import GAME_INIT, GAME_START, GAME_OVER, GAME_PAUSED
from state_manager import GameState
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN, BLUE,
    FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL
)

class Renderer:
    """渲染管理类，负责处理所有渲染相关功能"""
    
    def __init__(self, screen):
        """初始化渲染器"""
        self.screen = screen
        self.load_resources()
    
    def load_resources(self):
        """加载渲染资源"""
        # 创建资源目录
        if not os.path.exists('resources'):
            os.makedirs('resources')
            os.makedirs('resources/images')
            os.makedirs('resources/sounds')
            print("请将游戏资源放入resources目录")
        
        # 初始化字体
        pygame.font.init()
        print("字体系统初始化完成")
        
        # 尝试加载系统字体（优先使用DejaVu字体，因为系统中确实存在）
        font_candidates = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/System/Library/Fonts/Arial.ttf',  # macOS
            'C:/Windows/Fonts/arial.ttf',       # Windows
        ]
        
        font_path = None
        for font in font_candidates:
            if os.path.exists(font):
                try:
                    # 测试字体是否可以正常加载
                    test_font = pygame.font.Font(font, 24)
                    font_path = font
                    print(f"成功找到字体: {font}")
                    break
                except Exception as e:
                    print(f"字体加载失败 {font}: {e}")
                    continue
        
        # 加载字体
        if font_path:
            try:
                self.font = pygame.font.Font(font_path, FONT_SIZE_MEDIUM)
                self.font_large = pygame.font.Font(font_path, FONT_SIZE_LARGE)
                self.font_medium = pygame.font.Font(font_path, FONT_SIZE_MEDIUM)
                self.font_small = pygame.font.Font(font_path, FONT_SIZE_SMALL)
                self.use_chinese = False  # 系统没有中文字体，使用英文
                print(f"使用字体文件: {font_path}")
            except Exception as e:
                print(f"字体文件加载失败: {e}")
                # 回退到默认字体
                self._load_default_fonts()
        else:
            # 使用pygame默认字体
            self._load_default_fonts()
        
        # 测试字体渲染
        try:
            test_surface = self.font.render("Test", True, WHITE)
            print(f"字体渲染测试成功，文字尺寸: {test_surface.get_size()}")
        except Exception as e:
            print(f"字体渲染测试失败: {e}")
        
        # 加载背景图像
        self._load_background()
    
    def _load_default_fonts(self):
        """加载默认字体"""
        self.font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.use_chinese = False
        print("使用pygame默认字体")
    
    def _load_background(self):
        """加载背景图像"""
        bg_img_path = os.path.join('resources', 'images', 'background.png')
        if os.path.exists(bg_img_path):
            self.background = pygame.image.load(bg_img_path).convert()
        else:
            # 如果背景图像不存在，使用纯色背景
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill(BLACK)
    
    def render(self, game_data):
        """根据游戏状态绘制画面 - 使用状态机模式"""
        # 绘制背景
        self.screen.blit(self.background, (0, 0))
        
        # 获取当前状态（优先使用状态机状态）
        current_state = game_data.get('current_state', None)
        if current_state is None:
            # 回退到旧的状态系统
            game_status = game_data['game_status']
            current_state = self._convert_legacy_status(game_status)
        
        # 根据状态机状态进行渲染
        if current_state == GameState.INIT:
            # 绘制游戏初始界面
            self.draw_start_screen(game_data)
        
        elif current_state == GameState.PLAYING:
            # 绘制游戏进行界面
            if game_data['all_sprites']:
                game_data['all_sprites'].draw(self.screen)
            
            # 绘制游戏UI面板
            self.draw_game_ui(game_data)
        
        elif current_state == GameState.PAUSED:
            # 绘制暂停状态下的游戏画面
            if game_data['all_sprites']:
                game_data['all_sprites'].draw(self.screen)
            
            # 绘制游戏UI面板
            self.draw_game_ui(game_data)
            
            # 绘制暂停提示
            self.draw_pause_screen()
        
        elif current_state == GameState.GAME_OVER:
            # 绘制游戏结束界面
            self.draw_start_screen(game_data)
        
        elif current_state == GameState.INSTRUCTIONS:
            # 绘制操作说明界面
            self.draw_instructions_screen(game_data)
        
        # 绘制状态信息（调试用）
        if current_state:
            self.draw_state_info(current_state)
        
        # 更新屏幕显示
        pygame.display.flip()
    
    def draw_start_screen(self, game_data):
        """绘制游戏开始界面"""
        # 创建渐变背景
        for y in range(SCREEN_HEIGHT):
            color_intensity = int(20 + (y / SCREEN_HEIGHT) * 40)
            color = (0, 0, color_intensity)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # 游戏标题
        if self.use_chinese:
            title_text = self.font_large.render("飞机大战", True, WHITE)
            shadow_text = self.font_large.render("飞机大战", True, (50, 50, 50))
        else:
            title_text = self.font_large.render("Plane War", True, WHITE)
            shadow_text = self.font_large.render("Plane War", True, (50, 50, 50))
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        
        # 添加标题阴影效果
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 3, SCREEN_HEIGHT//2 - 97))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        if game_data['score'] > 0:
            # 显示最终分数
            if self.use_chinese:
                score_text = self.font_medium.render(f"最终分数: {game_data['score']}", True, (255, 255, 0))
            else:
                score_text = self.font_medium.render(f"Final Score: {game_data['score']}", True, (255, 255, 0))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(score_text, score_rect)
        
        # 操作提示
        if not game_data['show_instructions']:
            if self.use_chinese:
                start_text = self.font.render("按空格键开始游戏", True, (0, 255, 0))
                help_text = self.font_small.render("按H键查看操作说明", True, WHITE)
            else:
                start_text = self.font.render("Press SPACE to Start", True, (0, 255, 0))
                help_text = self.font_small.render("Press H for Instructions", True, WHITE)
            
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
            help_rect = help_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70))
            
            self.screen.blit(start_text, start_rect)
            self.screen.blit(help_text, help_rect)
        else:
            # 显示操作说明
            self._draw_instructions()
    
    def _draw_instructions(self):
        """绘制操作说明"""
        if self.use_chinese:
            instructions = [
                "操作说明:",
                "← → 方向键: 移动飞机",
                "空格键: 射击",
                "P键: 暂停/继续游戏",
                "H键: 显示/隐藏说明",
                "",
                "按空格键开始游戏"
            ]
        else:
            instructions = [
                "Instructions:",
                "← → Arrow Keys: Move Plane",
                "SPACE: Shoot",
                "P: Pause/Resume Game",
                "H: Show/Hide Instructions",
                "",
                "Press SPACE to Start"
            ]
        
        for i, instruction in enumerate(instructions):
            if i == 0:  # 标题
                text = self.font.render(instruction, True, (255, 255, 0))
            elif i == len(instructions) - 1:  # 开始提示
                text = self.font.render(instruction, True, (0, 255, 0))
            else:
                text = self.font_small.render(instruction, True, WHITE)
            
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20 + i * 25))
            self.screen.blit(text, text_rect)
    
    def draw_game_ui(self, game_data):
        """绘制游戏UI界面"""
        # 绘制分数
        if self.use_chinese:
            score_text = self.font.render(f"分数: {game_data['score']}", True, WHITE)
            lives_text = self.font.render(f"生命: {game_data['player_lives']}", True, WHITE)
            difficulty_text = self.font.render(f"难度: {game_data['difficulty_level']}", True, WHITE)
        else:
            score_text = self.font.render(f"Score: {game_data['score']}", True, WHITE)
            lives_text = self.font.render(f"Lives: {game_data['player_lives']}", True, WHITE)
            difficulty_text = self.font.render(f"Level: {game_data['difficulty_level']}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        
        # 绘制生命值
        self.screen.blit(lives_text, (10, 40))
        
        # 绘制难度等级
        self.screen.blit(difficulty_text, (10, 70))
    
    def draw_pause_screen(self):
        """绘制暂停画面"""
        # 创建半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 暂停文本
        if self.use_chinese:
            pause_text = self.font_large.render("游戏暂停", True, WHITE)
            resume_text = self.font.render("按P键继续", True, (0, 255, 0))
        else:
            pause_text = self.font_large.render("PAUSED", True, WHITE)
            resume_text = self.font.render("Press P to Continue", True, (0, 255, 0))
        
        # 居中显示文本
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 25))
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 25))
        
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(resume_text, resume_rect)
    
    def _convert_legacy_status(self, game_status):
        """将旧的游戏状态转换为新的状态机状态"""
        status_map = {
            GAME_INIT: GameState.INIT,
            GAME_START: GameState.PLAYING,
            GAME_PAUSED: GameState.PAUSED,
            GAME_OVER: GameState.GAME_OVER
        }
        return status_map.get(game_status, GameState.INIT)
    
    def draw_instructions_screen(self, game_data):
        """绘制操作说明界面"""
        # 创建渐变背景
        for y in range(SCREEN_HEIGHT):
            color_intensity = int(20 + (y / SCREEN_HEIGHT) * 40)
            color = (0, 0, color_intensity)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # 显示操作说明
        self._draw_instructions()
        
        # 返回提示
        if self.use_chinese:
            back_text = self.font.render("按H键返回", True, (255, 255, 0))
        else:
            back_text = self.font.render("Press H to Go Back", True, (255, 255, 0))
        
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)
    
    def draw_state_info(self, current_state):
        """绘制状态信息（调试用）"""
        # 在屏幕右上角显示当前状态
        state_name = current_state.name if hasattr(current_state, 'name') else str(current_state)
        state_text = self.font_small.render(f"State: {state_name}", True, (255, 255, 0))
        state_rect = state_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        
        # 添加半透明背景
        bg_rect = pygame.Rect(state_rect.left - 5, state_rect.top - 2, 
                             state_rect.width + 10, state_rect.height + 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(128)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        self.screen.blit(state_text, state_rect)