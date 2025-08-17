#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对象池模块
实现对象池模式，优化内存使用，减少频繁的对象创建和销毁
"""

import pygame
from typing import List, Optional, Type, Any
from abc import ABC, abstractmethod
from sprites import Bullet, Enemy


class ObjectPool(ABC):
    """对象池基类
    
    提供通用的对象池功能，包括对象的获取、回收和管理
    """
    
    def __init__(self, initial_size: int = 10, max_size: int = 100):
        """
        初始化对象池
        
        Args:
            initial_size: 初始池大小
            max_size: 最大池大小
        """
        self.initial_size = initial_size
        self.max_size = max_size
        self.available_objects: List[Any] = []
        self.active_objects: List[Any] = []
        
        # 预创建初始对象
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化对象池，预创建对象"""
        for _ in range(self.initial_size):
            obj = self._create_object()
            if obj:
                self.available_objects.append(obj)
    
    @abstractmethod
    def _create_object(self) -> Any:
        """创建新对象的抽象方法，由子类实现"""
        pass
    
    @abstractmethod
    def _reset_object(self, obj: Any, *args, **kwargs) -> Any:
        """重置对象状态的抽象方法，由子类实现"""
        pass
    
    def get_object(self, *args, **kwargs) -> Optional[Any]:
        """
        从对象池获取一个对象
        
        Returns:
            可用的对象，如果池为空且达到最大大小则返回None
        """
        if self.available_objects:
            # 从可用对象列表中取出一个对象
            obj = self.available_objects.pop()
            # 重置对象状态
            obj = self._reset_object(obj, *args, **kwargs)
            # 添加到活跃对象列表
            self.active_objects.append(obj)
            return obj
        elif len(self.active_objects) < self.max_size:
            # 如果没有可用对象但未达到最大大小，创建新对象
            obj = self._create_object()
            if obj:
                obj = self._reset_object(obj, *args, **kwargs)
                self.active_objects.append(obj)
                return obj
        
        # 池已满或创建失败
        return None
    
    def return_object(self, obj: Any):
        """
        将对象返回到对象池
        
        Args:
            obj: 要返回的对象
        """
        if obj in self.active_objects:
            self.active_objects.remove(obj)
            # 清理对象状态
            self._cleanup_object(obj)
            # 如果池未满，将对象放回可用列表
            if len(self.available_objects) < self.max_size:
                self.available_objects.append(obj)
    
    def _cleanup_object(self, obj: Any):
        """
        清理对象状态，准备回收
        
        Args:
            obj: 要清理的对象
        """
        # 如果是pygame精灵，从所有组中移除
        if isinstance(obj, pygame.sprite.Sprite):
            obj.kill()
    
    def get_pool_stats(self) -> dict:
        """
        获取对象池统计信息
        
        Returns:
            包含池统计信息的字典
        """
        return {
            'available': len(self.available_objects),
            'active': len(self.active_objects),
            'total': len(self.available_objects) + len(self.active_objects),
            'max_size': self.max_size
        }
    
    def clear_pool(self):
        """清空对象池"""
        # 清理所有活跃对象
        for obj in self.active_objects:
            self._cleanup_object(obj)
        
        # 清理所有可用对象
        for obj in self.available_objects:
            self._cleanup_object(obj)
        
        self.active_objects.clear()
        self.available_objects.clear()


class BulletPool(ObjectPool):
    """子弹对象池
    
    专门管理子弹对象的创建、回收和重用
    """
    
    def __init__(self, initial_size: int = 20, max_size: int = 100):
        """初始化子弹对象池"""
        super().__init__(initial_size, max_size)
    
    def _create_object(self) -> Bullet:
        """创建新的子弹对象"""
        # 创建一个默认位置的子弹，稍后会重置位置
        return Bullet(0, 0)
    
    def _reset_object(self, bullet: Bullet, x: int, y: int) -> Bullet:
        """
        重置子弹对象的状态
        
        Args:
            bullet: 要重置的子弹对象
            x: 子弹的x坐标
            y: 子弹的y坐标
        
        Returns:
            重置后的子弹对象
        """
        # 重置位置
        bullet.rect.centerx = x
        bullet.rect.bottom = y
        
        # 重置速度（确保子弹向上移动）
        from config import BULLET_SPEED
        bullet.speed = -BULLET_SPEED
        
        # 确保子弹可见
        bullet.image.set_alpha(255)
        
        return bullet


class EnemyPool(ObjectPool):
    """敌机对象池
    
    专门管理敌机对象的创建、回收和重用
    """
    
    def __init__(self, initial_size: int = 15, max_size: int = 50):
        """初始化敌机对象池"""
        super().__init__(initial_size, max_size)
    
    def _create_object(self) -> Enemy:
        """创建新的敌机对象"""
        # 创建一个默认类型的敌机，稍后会重置类型和位置
        return Enemy("normal")
    
    def _reset_object(self, enemy: Enemy, enemy_type: str = "normal") -> Enemy:
        """
        重置敌机对象的状态
        
        Args:
            enemy: 要重置的敌机对象
            enemy_type: 敌机类型
        
        Returns:
            重置后的敌机对象
        """
        import random
        from config import SCREEN_WIDTH
        
        # 重置敌机类型和属性
        enemy.enemy_type = enemy_type
        enemy.setup_enemy_properties()
        
        # 重置位置
        enemy.rect.x = random.randint(0, SCREEN_WIDTH - enemy.rect.width)
        enemy.rect.y = random.randrange(-100, -40)
        
        # 重置移动速度
        enemy.speed_y = enemy.base_speed_y + random.randrange(0, 2)
        enemy.speed_x = random.randrange(-1, 2)
        
        # 确保敌机可见
        enemy.image.set_alpha(255)
        
        return enemy


class PoolManager:
    """对象池管理器
    
    统一管理所有对象池，提供便捷的接口
    """
    
    def __init__(self):
        """初始化池管理器"""
        self.bullet_pool = BulletPool()
        self.enemy_pool = EnemyPool()
    
    def get_bullet(self, x: int, y: int) -> Optional[Bullet]:
        """
        获取一个子弹对象
        
        Args:
            x: 子弹的x坐标
            y: 子弹的y坐标
        
        Returns:
            子弹对象或None
        """
        return self.bullet_pool.get_object(x, y)
    
    def get_enemy(self, enemy_type: str = "normal") -> Optional[Enemy]:
        """
        获取一个敌机对象
        
        Args:
            enemy_type: 敌机类型
        
        Returns:
            敌机对象或None
        """
        return self.enemy_pool.get_object(enemy_type)
    
    def return_bullet(self, bullet: Bullet):
        """返回子弹到对象池"""
        self.bullet_pool.return_object(bullet)
    
    def return_enemy(self, enemy: Enemy):
        """返回敌机到对象池"""
        self.enemy_pool.return_object(enemy)
    
    def get_all_stats(self) -> dict:
        """获取所有对象池的统计信息"""
        return {
            'bullet_pool': self.bullet_pool.get_pool_stats(),
            'enemy_pool': self.enemy_pool.get_pool_stats()
        }
    
    def clear_all_pools(self):
        """清空所有对象池"""
        self.bullet_pool.clear_pool()
        self.enemy_pool.clear_pool()