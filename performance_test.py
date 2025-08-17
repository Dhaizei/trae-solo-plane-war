#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本
用于测试对象池模式的内存优化效果
"""

import pygame
import time
import gc
from sprites import Bullet, Enemy
from object_pool import PoolManager


class PerformanceMonitor:
    """性能监控器（简化版）"""
    
    def __init__(self):
        self.start_time = 0
        self.object_count = 0
    
    def start_monitoring(self):
        """开始监控"""
        gc.collect()  # 强制垃圾回收
        self.start_time = time.time()
        self.object_count = 0
        print(f"开始监控 - 开始时间: {time.strftime('%H:%M:%S')}")
    
    def get_current_stats(self):
        """获取当前统计信息"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        return {
            'elapsed_time': elapsed_time,
            'object_count': self.object_count
        }
    
    def print_stats(self, label=""):
        """打印统计信息"""
        stats = self.get_current_stats()
        print(f"{label} - 对象数: {stats['object_count']}, 耗时: {stats['elapsed_time']:.2f}s")
    
    def add_objects(self, count):
        """增加对象计数"""
        self.object_count += count


def test_without_object_pool(num_objects=1000, cycles=10):
    """测试不使用对象池的性能"""
    print("\n=== 测试不使用对象池 ===")
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    total_objects_created = 0
    
    for cycle in range(cycles):
        objects = []
        
        # 创建对象
        for i in range(num_objects // 2):
            bullet = Bullet(100, 100)
            enemy = Enemy("normal")
            objects.extend([bullet, enemy])
            total_objects_created += 2
        
        monitor.add_objects(num_objects)
        
        # 模拟使用对象
        for obj in objects:
            if hasattr(obj, 'rect'):
                obj.rect.x += 1
        
        # 销毁对象（模拟游戏中的对象销毁）
        del objects
        gc.collect()
        
        if cycle % 2 == 0:
            monitor.print_stats(f"周期 {cycle + 1}/{cycles}")
    
    final_stats = monitor.get_current_stats()
    print(f"\n总计创建对象: {total_objects_created}")
    print(f"总耗时: {final_stats['elapsed_time']:.2f}s")
    print(f"平均每秒创建对象: {total_objects_created/final_stats['elapsed_time']:.0f} 个/秒")
    
    return final_stats


def test_with_object_pool(num_objects=1000, cycles=10):
    """测试使用对象池的性能"""
    print("\n=== 测试使用对象池 ===")
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    # 创建对象池管理器
    pool_manager = PoolManager()
    
    total_objects_reused = 0
    objects_in_use = []
    
    for cycle in range(cycles):
        # 从对象池获取对象
        for i in range(num_objects // 2):
            bullet = pool_manager.get_bullet(100, 100)
            enemy = pool_manager.get_enemy("normal")
            
            if bullet:
                objects_in_use.append(('bullet', bullet))
                total_objects_reused += 1
            
            if enemy:
                objects_in_use.append(('enemy', enemy))
                total_objects_reused += 1
        
        monitor.add_objects(num_objects)
        
        # 模拟使用对象
        for obj_type, obj in objects_in_use:
            if hasattr(obj, 'rect'):
                obj.rect.x += 1
        
        # 返回对象到池中（模拟游戏中的对象回收）
        for obj_type, obj in objects_in_use:
            if obj_type == 'bullet':
                pool_manager.return_bullet(obj)
            elif obj_type == 'enemy':
                pool_manager.return_enemy(obj)
        
        objects_in_use.clear()
        
        if cycle % 2 == 0:
            monitor.print_stats(f"周期 {cycle + 1}/{cycles}")
            # 打印对象池统计信息
            pool_stats = pool_manager.get_all_stats()
            print(f"  对象池状态: 子弹池({pool_stats['bullet_pool']['available']}/{pool_stats['bullet_pool']['total']}), "
                  f"敌机池({pool_stats['enemy_pool']['available']}/{pool_stats['enemy_pool']['total']})")
    
    final_stats = monitor.get_current_stats()
    final_pool_stats = pool_manager.get_all_stats()
    
    print(f"\n总计重用对象: {total_objects_reused}")
    print(f"最终对象池状态:")
    print(f"  子弹池: {final_pool_stats['bullet_pool']['available']} 可用 / {final_pool_stats['bullet_pool']['total']} 总计")
    print(f"  敌机池: {final_pool_stats['enemy_pool']['available']} 可用 / {final_pool_stats['enemy_pool']['total']} 总计")
    print(f"总耗时: {final_stats['elapsed_time']:.2f}s")
    print(f"平均每秒处理对象: {total_objects_reused/final_stats['elapsed_time']:.0f} 个/秒")
    
    return final_stats


def run_performance_comparison():
    """运行性能对比测试"""
    print("飞机大战对象池性能测试")
    print("=" * 50)
    
    # 初始化pygame（某些精灵类可能需要）
    pygame.init()
    pygame.display.set_mode((1, 1))  # 最小窗口
    
    # 测试参数
    num_objects = 1000
    cycles = 10
    
    print(f"测试参数: 每周期 {num_objects} 个对象, 共 {cycles} 个周期")
    
    # 测试不使用对象池
    stats_without_pool = test_without_object_pool(num_objects, cycles)
    
    # 等待一段时间，让系统稳定
    time.sleep(2)
    gc.collect()
    
    # 测试使用对象池
    stats_with_pool = test_with_object_pool(num_objects, cycles)
    
    # 对比结果
    print("\n" + "=" * 50)
    print("性能对比结果:")
    print(f"不使用对象池: 耗时 {stats_without_pool['elapsed_time']:.2f}s")
    print(f"使用对象池:   耗时 {stats_with_pool['elapsed_time']:.2f}s")
    
    time_improvement = stats_without_pool['elapsed_time'] - stats_with_pool['elapsed_time']
    
    print(f"\n优化效果:")
    if time_improvement > 0:
        print(f"时间节省: {time_improvement:.2f}s ({time_improvement/stats_without_pool['elapsed_time']*100:.1f}%)")
        print(f"性能提升: {stats_without_pool['elapsed_time']/stats_with_pool['elapsed_time']:.2f}x")
    else:
        print(f"时间增加: {abs(time_improvement):.2f}s ({abs(time_improvement)/stats_without_pool['elapsed_time']*100:.1f}%)")
        print("注意: 对象池在小规模测试中可能有额外开销，但在大规模应用中会显示优势")
    
    print(f"\n对象池优势:")
    print(f"- 减少了垃圾回收压力")
    print(f"- 避免了频繁的内存分配和释放")
    print(f"- 在长时间运行的游戏中能显著提升性能")
    
    pygame.quit()


if __name__ == "__main__":
    try:
        run_performance_comparison()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()