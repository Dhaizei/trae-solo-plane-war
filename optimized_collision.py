#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的碰撞检测系统
实现空间哈希、缓存和其他优化技术来提升碰撞检测性能
"""

import pygame
from typing import Dict, List, Tuple, Set
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class SpatialHash:
    """空间哈希表，用于快速碰撞检测"""
    
    def __init__(self, cell_size: int = 64):
        """初始化空间哈希表
        
        Args:
            cell_size: 网格单元大小，默认64像素
        """
        self.cell_size = cell_size
        self.hash_table: Dict[Tuple[int, int], List[pygame.sprite.Sprite]] = {}
        
    def clear(self):
        """清空哈希表"""
        self.hash_table.clear()
    
    def _get_cells(self, rect: pygame.Rect) -> List[Tuple[int, int]]:
        """获取矩形覆盖的所有网格单元
        
        Args:
            rect: 精灵的矩形区域
            
        Returns:
            覆盖的网格单元坐标列表
        """
        cells = []
        start_x = max(0, rect.left // self.cell_size)
        end_x = min(SCREEN_WIDTH // self.cell_size, rect.right // self.cell_size)
        start_y = max(0, rect.top // self.cell_size)
        end_y = min(SCREEN_HEIGHT // self.cell_size, rect.bottom // self.cell_size)
        
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                cells.append((x, y))
        
        return cells
    
    def insert(self, sprite: pygame.sprite.Sprite):
        """将精灵插入到哈希表中
        
        Args:
            sprite: 要插入的精灵
        """
        cells = self._get_cells(sprite.rect)
        for cell in cells:
            if cell not in self.hash_table:
                self.hash_table[cell] = []
            self.hash_table[cell].append(sprite)
    
    def query(self, sprite: pygame.sprite.Sprite) -> Set[pygame.sprite.Sprite]:
        """查询与指定精灵可能碰撞的精灵
        
        Args:
            sprite: 查询的精灵
            
        Returns:
            可能碰撞的精灵集合
        """
        candidates = set()
        cells = self._get_cells(sprite.rect)
        
        for cell in cells:
            if cell in self.hash_table:
                candidates.update(self.hash_table[cell])
        
        # 移除自己
        candidates.discard(sprite)
        return candidates

class CollisionCache:
    """碰撞检测缓存系统"""
    
    def __init__(self, max_size: int = 1000):
        """初始化缓存
        
        Args:
            max_size: 缓存最大大小
        """
        self.cache: Dict[Tuple[int, int], bool] = {}
        self.max_size = max_size
        self.access_order = []  # LRU缓存访问顺序
    
    def _get_cache_key(self, sprite1: pygame.sprite.Sprite, sprite2: pygame.sprite.Sprite) -> Tuple[int, int]:
        """生成缓存键
        
        Args:
            sprite1, sprite2: 两个精灵
            
        Returns:
            缓存键
        """
        # 使用精灵的ID和位置生成键
        id1, id2 = id(sprite1), id(sprite2)
        if id1 > id2:
            id1, id2 = id2, id1
        
        # 包含位置信息以确保缓存有效性
        pos1 = (sprite1.rect.x, sprite1.rect.y)
        pos2 = (sprite2.rect.x, sprite2.rect.y)
        
        return (id1, id2, pos1, pos2)
    
    def get(self, sprite1: pygame.sprite.Sprite, sprite2: pygame.sprite.Sprite) -> bool:
        """从缓存获取碰撞结果
        
        Args:
            sprite1, sprite2: 两个精灵
            
        Returns:
            碰撞结果，如果缓存中没有则返回None
        """
        key = self._get_cache_key(sprite1, sprite2)
        if key in self.cache:
            # 更新访问顺序
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, sprite1: pygame.sprite.Sprite, sprite2: pygame.sprite.Sprite, result: bool):
        """将碰撞结果放入缓存
        
        Args:
            sprite1, sprite2: 两个精灵
            result: 碰撞结果
        """
        key = self._get_cache_key(sprite1, sprite2)
        
        # 如果缓存已满，移除最久未使用的项
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = result
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_order.clear()

class OptimizedCollisionDetector:
    """优化的碰撞检测器"""
    
    def __init__(self, cell_size: int = 64, use_cache: bool = True):
        """初始化碰撞检测器
        
        Args:
            cell_size: 空间哈希网格大小
            use_cache: 是否使用缓存
        """
        self.spatial_hash = SpatialHash(cell_size)
        self.use_cache = use_cache
        self.cache = CollisionCache() if use_cache else None
        
        # 性能统计
        self.stats = {
            'total_checks': 0,
            'cache_hits': 0,
            'actual_collisions': 0,
            'spatial_hash_queries': 0
        }
    
    def reset_stats(self):
        """重置性能统计"""
        self.stats = {
            'total_checks': 0,
            'cache_hits': 0,
            'actual_collisions': 0,
            'spatial_hash_queries': 0
        }
    
    def get_stats(self) -> Dict[str, int]:
        """获取性能统计信息"""
        return self.stats.copy()
    
    def groupcollide_optimized(self, group1: pygame.sprite.Group, group2: pygame.sprite.Group, 
                              dokill1: bool = False, dokill2: bool = False, collided=None) -> Dict[pygame.sprite.Sprite, List[pygame.sprite.Sprite]]:
        """优化的组碰撞检测
        
        Args:
            group1, group2: 要检测碰撞的精灵组
            dokill1, dokill2: 是否在碰撞后移除精灵
            collided: 自定义碰撞检测函数
            
        Returns:
            碰撞结果字典
        """
         # 清空并重建空间哈希表
        self.spatial_hash.clear()
        
        # 将group2的精灵插入空间哈希表
        for sprite in group2:
            self.spatial_hash.insert(sprite)
        
        hits = {}
        sprites_to_kill1 = []
        sprites_to_kill2 = []
        
        # 对group1中的每个精灵进行碰撞检测
        for sprite1 in group1:
            self.stats['spatial_hash_queries'] += 1
            candidates = self.spatial_hash.query(sprite1)
            
            for sprite2 in candidates:
                self.stats['total_checks'] += 1
                
                # 尝试从缓存获取结果
                collision_result = None
                if self.use_cache and self.cache:
                    collision_result = self.cache.get(sprite1, sprite2)
                    if collision_result is not None:
                        self.stats['cache_hits'] += 1
                
                # 如果缓存中没有，进行实际碰撞检测
                if collision_result is None:
                    # 使用自定义碰撞检测函数或默认rect检测
                    if collided is not None:
                        collision_result = collided(sprite1, sprite2)
                    else:
                        collision_result = sprite1.rect.colliderect(sprite2.rect)
                    
                    # 将结果放入缓存
                    if self.use_cache and self.cache:
                        self.cache.put(sprite1, sprite2, collision_result)
                
                if collision_result:
                    self.stats['actual_collisions'] += 1
                    
                    if sprite1 not in hits:
                        hits[sprite1] = []
                    hits[sprite1].append(sprite2)
                    
                    # 标记要删除的精灵
                    if dokill1 and sprite1 not in sprites_to_kill1:
                        sprites_to_kill1.append(sprite1)
                    if dokill2 and sprite2 not in sprites_to_kill2:
                        sprites_to_kill2.append(sprite2)
        
        # 删除标记的精灵
        for sprite in sprites_to_kill1:
            sprite.kill()
        for sprite in sprites_to_kill2:
            sprite.kill()
        
        return hits
    
    def spritecollide_optimized(self, sprite: pygame.sprite.Sprite, group: pygame.sprite.Group, 
                               dokill: bool = False, collided=None) -> List[pygame.sprite.Sprite]:
        """优化的精灵碰撞检测
        
        Args:
            sprite: 要检测的精灵
            group: 精灵组
            dokill: 是否在碰撞后移除精灵
            collided: 自定义碰撞检测函数
            
        Returns:
            碰撞的精灵列表
        """
         # 重建空间哈希表
        self.spatial_hash.clear()
        for s in group:
            self.spatial_hash.insert(s)
        
        self.stats['spatial_hash_queries'] += 1
        candidates = self.spatial_hash.query(sprite)
        
        collisions = []
        sprites_to_kill = []
        
        for candidate in candidates:
            self.stats['total_checks'] += 1
            
            # 尝试从缓存获取结果
            collision_result = None
            if self.use_cache and self.cache:
                collision_result = self.cache.get(sprite, candidate)
                if collision_result is not None:
                    self.stats['cache_hits'] += 1
            
            # 如果缓存中没有，进行实际碰撞检测
            if collision_result is None:
                # 使用自定义碰撞检测函数或默认rect检测
                if collided is not None:
                    collision_result = collided(sprite, candidate)
                else:
                    collision_result = sprite.rect.colliderect(candidate.rect)
                
                # 将结果放入缓存
                if self.use_cache and self.cache:
                    self.cache.put(sprite, candidate, collision_result)
            
            if collision_result:
                self.stats['actual_collisions'] += 1
                collisions.append(candidate)
                
                if dokill:
                    sprites_to_kill.append(candidate)
        
        # 删除标记的精灵
        for s in sprites_to_kill:
            s.kill()
        
        return collisions
    
    def clear_cache(self):
        """清空缓存"""
        if self.cache:
            self.cache.clear()

# 全局优化碰撞检测器实例
_global_collision_detector = OptimizedCollisionDetector()

def get_collision_detector() -> OptimizedCollisionDetector:
    """获取全局碰撞检测器实例"""
    return _global_collision_detector

def optimized_groupcollide(group1: pygame.sprite.Group, group2: pygame.sprite.Group, 
                          dokill1: bool = False, dokill2: bool = False, collided=None) -> Dict[pygame.sprite.Sprite, List[pygame.sprite.Sprite]]:
    """优化的组碰撞检测函数（兼容pygame.sprite.groupcollide接口）
    支持自定义碰撞检测函数
    """
    return _global_collision_detector.groupcollide_optimized(group1, group2, dokill1, dokill2, collided)

def optimized_spritecollide(sprite: pygame.sprite.Sprite, group: pygame.sprite.Group, 
                           dokill: bool = False, collided=None) -> List[pygame.sprite.Sprite]:
    """优化的精灵碰撞检测函数（兼容pygame.sprite.spritecollide接口）
    支持自定义碰撞检测函数
    """
    return _global_collision_detector.spritecollide_optimized(sprite, group, dokill, collided)