#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import sys
import os
import random
from sprites import Player, Enemy, Bullet, Explosion
from sounds import SoundManager

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 480  # 屏幕宽度
SCREEN_HEIGHT = 700  # 屏幕高度
FPS = 60  # 游戏帧率

# 颜色常量
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 游戏状态
GAME_INIT = 0  # 游戏初始化
GAME_START = 1  # 游戏开始
GAME_OVER = 2  # 游戏结束
GAME_PAUSED = 3  # 游戏暂停

class Game:
    """游戏主类，负责管理游戏主循环和状态"""
    
    def __init__(self):
        """初始化游戏"""
        # 创建游戏窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("飞机大战")
        
        # 创建时钟对象
        self.clock = pygame.time.Clock()
        
        # 游戏状态
        self.game_status = GAME_INIT
        self.show_instructions = False  # 是否显示操作说明
        
        # 游戏分数
        self.score = 0
        
        # 加载游戏资源
        self.load_resources()
    
    def load_resources(self):
        """加载游戏资源"""
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
                self.font = pygame.font.Font(font_path, 36)
                self.font_large = pygame.font.Font(font_path, 72)
                self.font_medium = pygame.font.Font(font_path, 48)
                self.font_small = pygame.font.Font(font_path, 24)
                self.use_chinese = False  # 系统没有中文字体，使用英文
                print(f"使用字体文件: {font_path}")
            except Exception as e:
                print(f"字体文件加载失败: {e}")
                # 回退到默认字体
                self.font = pygame.font.Font(None, 36)
                self.font_large = pygame.font.Font(None, 72)
                self.font_medium = pygame.font.Font(None, 48)
                self.font_small = pygame.font.Font(None, 24)
                self.use_chinese = False
                print("使用pygame默认字体")
        else:
            # 使用pygame默认字体
            self.font = pygame.font.Font(None, 36)
            self.font_large = pygame.font.Font(None, 72)
            self.font_medium = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 24)
            self.use_chinese = False
            print("未找到系统字体，使用pygame默认字体")
        
        # 测试字体渲染
        try:
            test_surface = self.font.render("Test", True, WHITE)
            print(f"字体渲染测试成功，文字尺寸: {test_surface.get_size()}")
        except Exception as e:
            print(f"字体渲染测试失败: {e}")
        
        # 加载背景图像
        bg_img_path = os.path.join('resources', 'images', 'background.png')
        if os.path.exists(bg_img_path):
            self.background = pygame.image.load(bg_img_path).convert()
        else:
            # 如果背景图像不存在，使用纯色背景
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill(BLACK)
        
        # 初始化音效系统
        try:
            self.sound_manager = SoundManager()
            self.sound_manager.load_sounds()
            self.sound_enabled = True
        except Exception as e:
            print(f"音效系统初始化失败: {e}")
            self.sound_manager = None
            self.sound_enabled = False
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            # 退出游戏
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 处理按键事件
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # 空格键开始游戏
                if event.key == pygame.K_SPACE and self.game_status != GAME_START:
                    self.start_game()
                elif event.key == pygame.K_p and self.game_status in [GAME_START, GAME_PAUSED]:
                    # 切换暂停状态
                    if self.game_status == GAME_START:
                        self.game_status = GAME_PAUSED
                    else:
                        self.game_status = GAME_START
                elif event.key == pygame.K_h and self.game_status in [GAME_INIT, GAME_OVER]:
                    # 切换操作说明显示
                    self.show_instructions = not self.show_instructions
            
            elif event.type == pygame.USEREVENT + 1:
                # 恢复受伤敌机的透明度
                for enemy in self.enemies:
                    if enemy.health > 0:
                        enemy.image.set_alpha(255)
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # 取消定时器
    
    def start_game(self):
        """开始游戏"""
        self.game_status = GAME_START
        self.score = 0
        
        # 敌机生成相关
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 60  # 初始敌机生成间隔
        self.base_enemy_spawn_delay = 60  # 基础敌机生成间隔
        self.difficulty_level = 1  # 难度等级
        
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
            
            # 处理玩家射击
            keystate = pygame.key.get_pressed()
            if keystate[pygame.K_SPACE]:
                bullet = self.player.shoot()
                if bullet:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
                    # 播放射击音效
                    if self.sound_enabled and self.sound_manager:
                        self.sound_manager.play_sound('shoot')
            
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
                        # 敌机受伤但未被摧毁，恢复透明度
                        pygame.time.set_timer(pygame.USEREVENT + 1, 200)  # 200ms后恢复
            
            # 检测玩家与敌机的碰撞
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
    
    def draw(self):
        """绘制游戏画面"""
        # 绘制背景
        self.screen.blit(self.background, (0, 0))
        
        if self.game_status == GAME_INIT:
            # 绘制游戏开始界面
            self.draw_start_screen()
        
        elif self.game_status == GAME_START:
            # 绘制所有精灵
            self.all_sprites.draw(self.screen)
            
            # 绘制游戏UI面板
            self.draw_game_ui()
        
        elif self.game_status == GAME_PAUSED:
            # 绘制暂停状态下的游戏画面
            self.all_sprites.draw(self.screen)
            
            # 绘制游戏UI面板
            self.draw_game_ui()
            
            # 绘制暂停提示
            self.draw_pause_screen()
        
        elif self.game_status == GAME_OVER:
            # 绘制游戏开始/结束界面
            self.draw_start_screen()
        
        # 更新屏幕显示
        pygame.display.flip()
    
    def run(self):
        """游戏主循环"""
        while True:
            # 处理事件
            self.handle_events()
            
            # 更新游戏状态
            self.update()
            
            # 绘制游戏画面
            self.draw()
            
            # 控制游戏帧率
            self.clock.tick(FPS)

    def draw_start_screen(self):
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
        
        if self.score > 0:
            # 显示最终分数
            if self.use_chinese:
                score_text = self.font_medium.render(f"最终分数: {self.score}", True, (255, 255, 0))
            else:
                score_text = self.font_medium.render(f"Final Score: {self.score}", True, (255, 255, 0))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(score_text, score_rect)
        
        # 操作提示
        if not self.show_instructions:
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
    
    def draw_game_ui(self):
        """绘制游戏UI界面"""
        # 绘制分数
        if self.use_chinese:
            score_text = self.font.render(f"分数: {self.score}", True, WHITE)
            lives_text = self.font.render(f"生命: {self.player.lives}", True, WHITE)
            difficulty_text = self.font.render(f"难度: {self.difficulty_level}", True, WHITE)
        else:
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
            difficulty_text = self.font.render(f"Level: {self.difficulty_level}", True, WHITE)
        
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
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)

# 游戏入口
if __name__ == "__main__":
    game = Game()
    game.run()