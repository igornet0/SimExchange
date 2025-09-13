"""
Утилиты для тестирования производительности
"""

import time
from typing import Dict, Any, List
from ..core.models import SimulationConfig
from ..core.services import TradingSimulator


class PerformanceTester:
    """Тестер производительности симулятора"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.results: List[Dict[str, Any]] = []
    
    def run_test(self):
        """Запускает полный тест производительности"""
        print("🧪 Тест производительности симулятора")
        print("=" * 50)
        
        # Тестируем разные количества циклов
        test_cycles = [100, 500, 1000, 2000, 5000]
        
        for cycles in test_cycles:
            print(f"\n📊 Тестирование {cycles} циклов...")
            result = self._test_cycles(cycles)
            self.results.append(result)
            
            print(f"✅ {cycles} циклов за {result['total_time']:.2f} сек "
                  f"({result['cycles_per_second']:.1f} циклов/сек)")
            print(f"   💾 Память: {result['memory_usage']:.1f} MB")
            print(f"   📈 Сделок: {result['total_trades']}")
            print(f"   💵 Объем: {result['total_volume']}")
        
        # Показываем сводку
        self._print_summary()
    
    def _test_cycles(self, cycles: int) -> Dict[str, Any]:
        """Тестирует указанное количество циклов"""
        # Создаем новый симулятор для каждого теста
        simulator = TradingSimulator(self.config)
        
        # Включаем режим высокой производительности
        simulator.set_performance_mode(True, skip_volatility=True)
        
        # Замеряем время и память
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Выполняем циклы
        for i in range(cycles):
            simulator.run_cycle()
            
            # Показываем прогресс каждые 100 циклов
            if (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                cycles_per_second = (i + 1) / elapsed
                print(f"  Цикл {i + 1}: {cycles_per_second:.1f} циклов/сек")
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        # Получаем статистику
        data = simulator.get_simulation_data()
        
        return {
            'cycles': cycles,
            'total_time': end_time - start_time,
            'cycles_per_second': cycles / (end_time - start_time),
            'memory_usage': end_memory - start_memory,
            'total_trades': data['total_trades'],
            'total_volume': data['total_volume'],
            'final_price': data['order_book']['current_price'],
            'agents_count': len(data['agents'])
        }
    
    def _get_memory_usage(self) -> float:
        """Возвращает использование памяти в MB"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Если psutil не установлен, возвращаем 0
            return 0.0
    
    def _print_summary(self):
        """Печатает сводку результатов"""
        print("\n" + "=" * 50)
        print("📈 СВОДКА РЕЗУЛЬТАТОВ")
        print("=" * 50)
        
        if not self.results:
            print("❌ Нет результатов для отображения")
            return
        
        # Находим лучшие и худшие результаты
        best_performance = max(self.results, key=lambda x: x['cycles_per_second'])
        worst_performance = min(self.results, key=lambda x: x['cycles_per_second'])
        
        print(f"🏆 Лучшая производительность: {best_performance['cycles_per_second']:.1f} циклов/сек "
              f"({best_performance['cycles']} циклов)")
        print(f"🐌 Худшая производительность: {worst_performance['cycles_per_second']:.1f} циклов/сек "
              f"({worst_performance['cycles']} циклов)")
        
        # Средняя производительность
        avg_performance = sum(r['cycles_per_second'] for r in self.results) / len(self.results)
        print(f"📊 Средняя производительность: {avg_performance:.1f} циклов/сек")
        
        # Использование памяти
        total_memory = sum(r['memory_usage'] for r in self.results)
        print(f"💾 Общее использование памяти: {total_memory:.1f} MB")
        
        # Статистика по сделкам
        total_trades = sum(r['total_trades'] for r in self.results)
        total_volume = sum(r['total_volume'] for r in self.results)
        print(f"📈 Общее количество сделок: {total_trades}")
        print(f"💵 Общий объем торгов: {total_volume}")
        
        print("\n🎉 Тест производительности завершен!")
    
    def save_results(self, filename: str = "performance_results.json"):
        """Сохраняет результаты в файл"""
        import json
        from datetime import datetime
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'initial_price': self.config.initial_price,
                'num_agents': self.config.num_agents,
                'initial_balance': self.config.initial_balance,
                'performance_mode': self.config.performance_mode
            },
            'results': self.results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Результаты сохранены в {filename}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении результатов: {e}")


def benchmark_simulation(config: SimulationConfig, cycles: int = 1000) -> Dict[str, Any]:
    """Быстрый бенчмарк симуляции"""
    simulator = TradingSimulator(config)
    simulator.set_performance_mode(True, skip_volatility=True)
    
    start_time = time.time()
    
    for _ in range(cycles):
        simulator.run_cycle()
    
    end_time = time.time()
    
    data = simulator.get_simulation_data()
    
    return {
        'cycles': cycles,
        'total_time': end_time - start_time,
        'cycles_per_second': cycles / (end_time - start_time),
        'total_trades': data['total_trades'],
        'total_volume': data['total_volume'],
        'final_price': data['order_book']['current_price']
    }
