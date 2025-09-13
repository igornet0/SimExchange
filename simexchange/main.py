#!/usr/bin/env python3
"""
Главный файл для запуска SimExchange с новой архитектурой

Использование:
    python -m simexchange.main [параметры]

Параметры:
    -p, --price     Начальная цена акции (по умолчанию: 100.0)
    -c, --cycles    Количество циклов симуляции (по умолчанию: 1000)
    -a, --agents    Количество торговых агентов (по умолчанию: 20)
    -b, --balance   Начальный баланс каждого агента (по умолчанию: 10000.0)
    --config        Путь к файлу конфигурации
    --modern-ui     Использовать современный UI (по умолчанию: True)

Примеры:
    python -m simexchange.main -a 100                    # 100 агентов
    python -m simexchange.main -p 200 -a 50 -b 20000     # Цена 200, 50 агентов, баланс 20000
    python -m simexchange.main --config custom_config.yaml  # Пользовательская конфигурация
"""

import sys
import argparse
from pathlib import Path

# Добавляем корневую директорию в путь для импорта
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from simexchange.config.settings import ConfigManager
from simexchange.core.models import SimulationConfig
from simexchange.core.services import TradingSimulator


def create_simulation_config(args) -> SimulationConfig:
    """Создает конфигурацию симуляции из аргументов командной строки"""
    # Загружаем конфигурацию по умолчанию
    config_manager = ConfigManager(args.config) if args.config else ConfigManager()
    config = config_manager.get_simulation_config()
    
    # Переопределяем параметры из командной строки
    if args.price is not None:
        config.initial_price = args.price
    if args.agents is not None:
        config.num_agents = args.agents
    if args.balance is not None:
        config.initial_balance = args.balance
    
    return config


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='Симулятор биржевого стакана с модульной архитектурой',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('-p', '--price', type=float, default=None,
                       help='Начальная цена акции (по умолчанию: из конфигурации)')
    parser.add_argument('-c', '--cycles', type=int, default=1000,
                       help='Количество циклов симуляции (по умолчанию: 1000)')
    parser.add_argument('-a', '--agents', type=int, default=None,
                       help='Количество торговых агентов (по умолчанию: из конфигурации)')
    parser.add_argument('-b', '--balance', type=float, default=None,
                       help='Начальный баланс каждого агента (по умолчанию: из конфигурации)')
    parser.add_argument('--config', type=str, default=None,
                       help='Путь к файлу конфигурации')
    parser.add_argument('--modern-ui', action='store_true', default=True,
                       help='Использовать современный UI (по умолчанию: True)')
    parser.add_argument('--legacy-ui', action='store_true',
                       help='Использовать старый UI')
    parser.add_argument('--no-ui', action='store_true',
                       help='Запустить без UI (только консоль)')
    parser.add_argument('--performance-test', action='store_true',
                       help='Запустить тест производительности')
    
    args = parser.parse_args()
    
    # Определяем UI
    use_modern_ui = args.modern_ui and not args.legacy_ui and not args.no_ui
    use_legacy_ui = args.legacy_ui and not args.no_ui
    use_ui = not args.no_ui
    
    print("=" * 60)
    print("🚀 SIMEXCHANGE - СИМУЛЯТОР БИРЖЕВОГО СТАКАНА")
    print("=" * 60)
    print("📦 Модульная архитектура v0.2.0")
    print("=" * 60)
    
    try:
        # Создаем конфигурацию
        config = create_simulation_config(args)
        
        print(f"💰 Начальная цена: {config.initial_price}")
        print(f"🔄 Количество циклов: {args.cycles}")
        print(f"👥 Количество агентов: {config.num_agents}")
        print(f"💵 Баланс агента: {config.initial_balance}")
        print(f"⚡ Режим производительности: {'Включен' if config.performance_mode else 'Выключен'}")
        print("=" * 60)
        
        if args.performance_test:
            # Запускаем тест производительности
            run_performance_test(config)
        elif use_ui:
            # Запускаем с UI
            run_with_ui(config, use_modern_ui)
        else:
            # Запускаем в консольном режиме
            run_console_mode(config, args.cycles)
            
    except KeyboardInterrupt:
        print("\n⏹️  Симуляция прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_performance_test(config: SimulationConfig):
    """Запускает тест производительности"""
    print("🧪 Запуск теста производительности...")
    
    from simexchange.utils.performance import PerformanceTester
    
    tester = PerformanceTester(config)
    tester.run_test()


def run_with_ui(config: SimulationConfig, use_modern_ui: bool):
    """Запускает симуляцию с UI"""
    print("🖥️  Запуск с пользовательским интерфейсом...")
    
    # Создаем симулятор
    simulator = TradingSimulator(config)
    
    if use_modern_ui:
        print("🎨 Используется современный UI")
        from simexchange.ui.windows.modern_main_window import ModernMainWindow
        visualizer = ModernMainWindow(simulator)
    else:
        print("🎨 Используется классический UI")
        from simexchange.ui.windows.legacy_main_window import LegacyMainWindow
        visualizer = LegacyMainWindow(simulator)
    
    # Запускаем визуализацию
    visualizer.run()


def run_console_mode(config: SimulationConfig, cycles: int):
    """Запускает симуляцию в консольном режиме"""
    print("💻 Запуск в консольном режиме...")
    print("Управление:")
    print("  ENTER - Один шаг симуляции")
    print("  'r' + ENTER - Сброс симуляции")
    print("  'q' + ENTER - Выход")
    print("=" * 60)
    
    # Создаем симулятор
    simulator = TradingSimulator(config)
    
    cycle_count = 0
    
    while cycle_count < cycles:
        try:
            command = input(f"Цикл {cycle_count + 1}/{cycles} > ").strip().lower()
            
            if command == 'q':
                print("👋 Выход из симуляции")
                break
            elif command == 'r':
                print("🔄 Сброс симуляции")
                simulator.reset()
                cycle_count = 0
                continue
            elif command == '' or command == 's':
                # Выполняем один цикл
                trades = simulator.run_cycle()
                cycle_count += 1
                
                # Показываем статистику
                data = simulator.get_simulation_data()
                print(f"  💰 Цена: {data['order_book']['current_price']:.2f}")
                print(f"  📊 Сделок: {len(trades)}")
                print(f"  📈 Всего сделок: {data['total_trades']}")
                print(f"  💵 Объем: {data['total_volume']}")
                
                if data.get('average_spread'):
                    print(f"  📏 Средний спред: {data['average_spread']:.2f}")
                
                # Показываем топ-3 агентов
                agents = data['agents'][:3]
                print("  🏆 Топ агенты:")
                for i, agent in enumerate(agents, 1):
                    print(f"    {i}. ID{agent['id']}: {agent['profit']:+.0f} ({agent['profit_percent']:+.1f}%)")
            else:
                print("  ❓ Неизвестная команда. Используйте ENTER, 'r', или 'q'")
                
        except EOFError:
            print("\n👋 Выход из симуляции")
            break
        except KeyboardInterrupt:
            print("\n⏹️  Симуляция прервана")
            break
    
    print(f"\n✅ Симуляция завершена! Выполнено {cycle_count} циклов")


if __name__ == "__main__":
    main()
