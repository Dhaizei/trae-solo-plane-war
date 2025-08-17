#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
碰撞检测性能基准测试工具
用于测试和对比不同碰撞检测算法的性能
"""

import os
# 设置pygame为无头模式
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
import time
import random
from typing import List, Tuple
from sprites import Bullet, Enemy
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from optimized_collision import optimized_groupcollide, optimized_spritecollide, SpatialHash

class CollisionBenchmark:
    """碰撞检测性能基准测试类"""
    
    def __init__(self):
        """初始化测试环境"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("碰撞检测性能测试")
        
        # 测试数据
        self.test_results = {}
        
    def create_test_sprites(self, num_bullets=50, num_enemies=30):
        """创建测试用的精灵对象"""
        # 创建精灵组
        bullets = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        
        # 创建子弹
        for _ in range(num_bullets):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            bullet = Bullet(x, y)
            bullets.add(bullet)
        
        # 创建敌机
        for _ in range(num_enemies):
            enemy = Enemy()
            enemy.rect.x = random.randint(0, SCREEN_WIDTH - enemy.rect.width)
            enemy.rect.y = random.randint(0, SCREEN_HEIGHT - enemy.rect.height)
            enemies.add(enemy)
        
        return bullets, enemies
    
    def benchmark_basic_collision(self, bullets, enemies, iterations=1000):
        """测试基础碰撞检测性能（当前实现）"""
        print(f"测试基础碰撞检测，迭代次数: {iterations}")
        
        start_time = time.perf_counter()
        collision_count = 0
        
        for _ in range(iterations):
            # 使用当前的碰撞检测方法
            hits = pygame.sprite.groupcollide(bullets, enemies, False, False)
            collision_count += len(hits)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        result = {
            'method': '基础groupcollide',
            'total_time': total_time,
            'avg_time_per_iteration': total_time / iterations,
            'collisions_found': collision_count,
            'bullets_count': len(bullets),
            'enemies_count': len(enemies)
        }
        
        print(f"总时间: {total_time:.4f}秒")
        print(f"平均每次迭代: {result['avg_time_per_iteration']:.6f}秒")
        print(f"发现碰撞: {collision_count}次")
        
        return result
    
    def benchmark_optimized_collision(self, bullets, enemies, iterations=1000):
        """测试优化后的碰撞检测性能"""
        print(f"测试优化碰撞检测，迭代次数: {iterations}")
        
        start_time = time.perf_counter()
        collision_count = 0
        
        for _ in range(iterations):
            # 使用优化的碰撞检测方法
            hits = self._optimized_groupcollide(bullets, enemies)
            collision_count += len(hits)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        result = {
            'method': '优化groupcollide',
            'total_time': total_time,
            'avg_time_per_iteration': total_time / iterations,
            'collisions_found': collision_count,
            'bullets_count': len(bullets),
            'enemies_count': len(enemies)
        }
        
        print(f"总时间: {total_time:.4f}秒")
        print(f"平均每次迭代: {result['avg_time_per_iteration']:.6f}秒")
        print(f"发现碰撞: {collision_count}次")
        
        return result
    
    def _optimized_groupcollide(self, group1, group2):
        """优化的组碰撞检测算法"""
        hits = {}
        
        # 预先计算边界框，减少重复计算
        group1_rects = [(sprite, sprite.rect) for sprite in group1]
        group2_rects = [(sprite, sprite.rect) for sprite in group2]
        
        # 使用空间分割优化
        for sprite1, rect1 in group1_rects:
            for sprite2, rect2 in group2_rects:
                # 快速边界框检测
                if (rect1.right >= rect2.left and rect1.left <= rect2.right and
                    rect1.bottom >= rect2.top and rect1.top <= rect2.bottom):
                    
                    if sprite1 not in hits:
                        hits[sprite1] = []
                    hits[sprite1].append(sprite2)
        
        return hits
    
    def benchmark_spatial_hash_collision(self, bullets, enemies, iterations=1000):
        """测试空间哈希碰撞检测性能"""
        print(f"测试空间哈希碰撞检测，迭代次数: {iterations}")
        
        start_time = time.perf_counter()
        collision_count = 0
        
        # 创建空间哈希表
        cell_size = 64  # 网格大小
        
        for _ in range(iterations):
            hits = self._spatial_hash_collision(bullets, enemies, cell_size)
            collision_count += len(hits)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        result = {
            'method': '空间哈希',
            'total_time': total_time,
            'avg_time_per_iteration': total_time / iterations,
            'collisions_found': collision_count,
            'bullets_count': len(bullets),
            'enemies_count': len(enemies)
        }
        
        print(f"总时间: {total_time:.4f}秒")
        print(f"平均每次迭代: {result['avg_time_per_iteration']:.6f}秒")
        print(f"发现碰撞: {collision_count}次")
        
        return result
    
    def _spatial_hash_collision(self, group1, group2, cell_size):
        """空间哈希碰撞检测算法"""
        # 创建空间哈希表
        spatial_hash = {}
        
        # 将group2的精灵放入哈希表
        for sprite in group2:
            cells = self._get_cells(sprite.rect, cell_size)
            for cell in cells:
                if cell not in spatial_hash:
                    spatial_hash[cell] = []
                spatial_hash[cell].append(sprite)
        
        # 检测group1与哈希表中精灵的碰撞
        hits = {}
        for sprite1 in group1:
            cells = self._get_cells(sprite1.rect, cell_size)
            for cell in cells:
                if cell in spatial_hash:
                    for sprite2 in spatial_hash[cell]:
                        if sprite1.rect.colliderect(sprite2.rect):
                            if sprite1 not in hits:
                                hits[sprite1] = []
                            if sprite2 not in hits[sprite1]:
                                hits[sprite1].append(sprite2)
        
        return hits
    
    def _get_cells(self, rect, cell_size):
        """获取矩形覆盖的网格单元"""
        cells = []
        start_x = rect.left // cell_size
        end_x = rect.right // cell_size
        start_y = rect.top // cell_size
        end_y = rect.bottom // cell_size
        
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                cells.append((x, y))
        
        return cells
    
    def run_full_benchmark(self):
        """运行完整的性能基准测试"""
        print("=" * 60)
        print("碰撞检测性能基准测试")
        print("=" * 60)
        
        # 测试不同规模的数据
        test_cases = [
            (20, 15),   # 小规模
            (50, 30),   # 中等规模
            (100, 60),  # 大规模
        ]
        
        for bullets_count, enemies_count in test_cases:
            print(f"\n测试规模: {bullets_count}个子弹, {enemies_count}个敌机")
            print("-" * 50)
            
            bullets, enemies = self.create_test_sprites(bullets_count, enemies_count)
            
            # 测试基础方法
            basic_result = self.benchmark_basic_collision(bullets, enemies, 500)
            
            # 测试优化方法
            optimized_result = self.benchmark_optimized_collision(bullets, enemies, 500)
            
            # 测试空间哈希方法
            spatial_result = self.benchmark_spatial_hash_collision(bullets, enemies, 500)
            
            # 计算性能提升
            basic_time = basic_result['avg_time_per_iteration']
            optimized_improvement = (basic_time - optimized_result['avg_time_per_iteration']) / basic_time * 100
            spatial_improvement = (basic_time - spatial_result['avg_time_per_iteration']) / basic_time * 100
            
            print(f"\n性能对比:")
            print(f"优化方法提升: {optimized_improvement:.1f}%")
            print(f"空间哈希提升: {spatial_improvement:.1f}%")
            
            # 保存结果
            test_key = f"{bullets_count}_{enemies_count}"
            self.test_results[test_key] = {
                'basic': basic_result,
                'optimized': optimized_result,
                'spatial_hash': spatial_result,
                'optimized_improvement': optimized_improvement,
                'spatial_improvement': spatial_improvement
            }
        
        print("\n=" * 60)
        print("测试完成")
        print("=" * 60)
        
        return self.test_results

def main():
    """主函数"""
    benchmark = CollisionBenchmark()
    results = benchmark.run_full_benchmark()
    
    # 输出总结
    print("\n总结报告:")
    print("=" * 40)
    
    total_optimized_improvement = 0
    total_spatial_improvement = 0
    test_count = len(results)
    
    for test_key, result in results.items():
        total_optimized_improvement += result['optimized_improvement']
        total_spatial_improvement += result['spatial_improvement']
    
    avg_optimized_improvement = total_optimized_improvement / test_count
    avg_spatial_improvement = total_spatial_improvement / test_count
    
    print(f"平均优化方法性能提升: {avg_optimized_improvement:.1f}%")
    print(f"平均空间哈希性能提升: {avg_spatial_improvement:.1f}%")
    
    pygame.quit()

if __name__ == "__main__":
    main()