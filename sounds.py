#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的音效系统
使用pygame内置功能创建简单音效，不依赖scipy
"""

import pygame
import numpy as np
import os
from config import SOUND_VOLUME, SOUND_FREQUENCY, SOUND_SAMPLE_RATE

class SoundManager:
    """音效管理器"""
    
    def __init__(self):
        """初始化音效管理器"""
        pygame.mixer.init(frequency=SOUND_SAMPLE_RATE, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.music_volume = SOUND_VOLUME
        self.sound_volume = SOUND_VOLUME
        
    def load_sounds(self):
        """加载所有音效"""
        sounds_dir = "resources/sounds"
        
        # 如果音效文件不存在，创建简单的音效
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir, exist_ok=True)
            
        # 创建简单的音效
        self._create_simple_sounds()
        
        # 尝试加载音效文件
        sound_files = {
            'shoot': 'shoot.wav',
            'explosion': 'explosion.wav',
            'hit': 'hit.wav',
            'game_over': 'game_over.wav',
            'level_up': 'level_up.wav'
        }
        
        for sound_name, filename in sound_files.items():
            filepath = os.path.join(sounds_dir, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(filepath)
                    self.sounds[sound_name].set_volume(self.sound_volume)
                except pygame.error:
                    # 如果加载失败，使用程序生成的音效
                    self.sounds[sound_name] = self._generate_sound(sound_name)
            else:
                # 文件不存在，使用程序生成的音效
                self.sounds[sound_name] = self._generate_sound(sound_name)
    
    def _create_simple_sounds(self):
        """创建简单的WAV音效文件"""
        sounds_dir = "resources/sounds"
        
        # 射击音效 - 短促的哔声
        shoot_sound = self._create_beep(frequency=800, duration=0.1)
        self._save_sound(shoot_sound, os.path.join(sounds_dir, "shoot.wav"))
        
        # 爆炸音效 - 噪音效果
        explosion_sound = self._create_noise(duration=0.3)
        self._save_sound(explosion_sound, os.path.join(sounds_dir, "explosion.wav"))
        
        # 被击中音效 - 低频哔声
        hit_sound = self._create_beep(frequency=200, duration=0.2)
        self._save_sound(hit_sound, os.path.join(sounds_dir, "hit.wav"))
        
        # 游戏结束音效 - 下降音调
        game_over_sound = self._create_sweep(start_freq=400, end_freq=100, duration=1.0)
        self._save_sound(game_over_sound, os.path.join(sounds_dir, "game_over.wav"))
        
        # 升级音效 - 上升音调
        level_up_sound = self._create_sweep(start_freq=200, end_freq=800, duration=0.5)
        self._save_sound(level_up_sound, os.path.join(sounds_dir, "level_up.wav"))
    
    def _create_beep(self, frequency=SOUND_FREQUENCY, duration=0.5, sample_rate=SOUND_SAMPLE_RATE):
        """创建哔声音效"""
        frames = int(duration * sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            # 生成正弦波
            arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
            # 添加衰减效果
            arr[i] *= (1 - i / frames) * 0.3
        
        return (arr * 32767).astype(np.int16)
    
    def _create_noise(self, duration=0.5, sample_rate=SOUND_SAMPLE_RATE):
        """创建噪音音效"""
        frames = int(duration * sample_rate)
        # 生成随机噪音
        arr = np.random.uniform(-1, 1, frames)
        
        # 添加衰减效果
        for i in range(frames):
            arr[i] *= (1 - i / frames) * 0.2
        
        return (arr * 32767).astype(np.int16)
    
    def _create_sweep(self, start_freq=200, end_freq=800, duration=0.5, sample_rate=SOUND_SAMPLE_RATE):
        """创建频率扫描音效"""
        frames = int(duration * sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            # 计算当前频率（线性插值）
            progress = i / frames
            current_freq = start_freq + (end_freq - start_freq) * progress
            
            # 生成正弦波
            arr[i] = np.sin(2 * np.pi * current_freq * i / sample_rate)
            # 添加包络
            envelope = np.sin(np.pi * progress) * 0.3
            arr[i] *= envelope
        
        return (arr * 32767).astype(np.int16)
    
    def _save_sound(self, sound_array, filepath):
        """保存音效到文件"""
        try:
            # 由于pygame.mixer.Sound没有直接的save方法
            # 我们只是创建Sound对象用于运行时播放
            # 实际的文件保存功能在这里被跳过
            pass
            
        except Exception as e:
            print(f"保存音效文件失败: {e}")
    
    def _generate_sound(self, sound_type):
        """根据类型生成音效"""
        if sound_type == 'shoot':
            arr = self._create_beep(frequency=800, duration=0.1)
        elif sound_type == 'explosion':
            arr = self._create_noise(duration=0.3)
        elif sound_type == 'hit':
            arr = self._create_beep(frequency=200, duration=0.2)
        elif sound_type == 'game_over':
            arr = self._create_sweep(start_freq=400, end_freq=100, duration=1.0)
        elif sound_type == 'level_up':
            arr = self._create_sweep(start_freq=200, end_freq=800, duration=0.5)
        else:
            arr = self._create_beep()
        
        # 转换为pygame Sound对象
        try:
            import pygame.sndarray
            # 确保数组是正确的格式：单声道为1D数组，立体声为2D数组
            if len(arr.shape) == 1:
                # 单声道，转换为立体声
                stereo_arr = np.column_stack((arr, arr))
            else:
                stereo_arr = arr
            
            sound = pygame.sndarray.make_sound(stereo_arr)
            sound.set_volume(self.sound_volume)
            return sound
        except Exception as e:
            print(f"生成音效失败: {e}")
            # 如果转换失败，返回None
            return None
    
    def play_sound(self, sound_name):
        """播放指定音效"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                pass  # 忽略播放错误
    
    def set_volume(self, volume):
        """设置音效音量"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.sound_volume)
    
    def stop_all(self):
        """停止所有音效"""
        pygame.mixer.stop()

# 测试函数
def main():
    """测试音效系统"""
    try:
        pygame.init()
        sound_manager = SoundManager()
        sound_manager.load_sounds()
        
        print("音效系统初始化成功！")
        print("可用音效:", list(sound_manager.sounds.keys()))
        
        # 测试播放音效
        print("测试播放射击音效...")
        sound_manager.play_sound('shoot')
        pygame.time.wait(500)
        
        print("测试播放爆炸音效...")
        sound_manager.play_sound('explosion')
        pygame.time.wait(1000)
        
        print("音效系统测试完成！")
        
    except Exception as e:
        print(f"音效系统初始化失败: {e}")
        print("游戏将在静音模式下运行")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()