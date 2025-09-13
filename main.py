#!/usr/bin/env python3
"""
Симулятор биржевого стакана

Использование:
    python main.py [параметры]

Параметры:
    -p, --price     Начальная цена акции (по умолчанию: 100.0)
    -c, --cycles    Количество циклов симуляции (по умолчанию: 1000)
    -a, --agents    Количество торговых агентов (по умолчанию: 20)
    -b, --balance   Начальный баланс каждого агента (по умолчанию: 10000.0)

Примеры:
    python main.py -a 100                    # 100 агентов
    python main.py -p 200 -a 50 -b 20000     # Цена 200, 50 агентов, баланс 20000
    python main.py --price 50 --agents 100   # Цена 50, 100 агентов
"""

import sys
import argparse
from simulator import TradingSimulator
from visualizer import TradingVisualizer

def main():
    parser = argparse.ArgumentParser(description='Симулятор биржевого стакана')
    parser.add_argument('-p', '--price', type=float, default=100.0,
                       help='Начальная цена акции (по умолчанию: 100.0)')
    parser.add_argument('-c', '--cycles', type=int, default=1000,
                       help='Количество циклов симуляции (по умолчанию: 1000)')
    parser.add_argument('-a', '--agents', type=int, default=20,
                       help='Количество торговых агентов (по умолчанию: 20)')
    parser.add_argument('-b', '--balance', type=float, default=10000.0,
                       help='Начальный баланс каждого агента (по умолчанию: 10000.0)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("СИМУЛЯТОР БИРЖЕВОГО СТАКАНА")
    print("=" * 60)
    print(f"Начальная цена: {args.price}")
    print(f"Количество циклов: {args.cycles}")
    print(f"Количество агентов: {args.agents}")
    print(f"Баланс агента: {args.balance}")
    print("=" * 60)
    print()
    print("УПРАВЛЕНИЕ:")
    print("  ПРОБЕЛ - Запуск/Остановка симуляции")
    print("  СТРЕЛКА ВПРАВО - Один шаг симуляции")
    print("  R - Сброс симуляции")
    print("  S - Настройка среднего спреда")
    print("  B - Настройка увеличения баланса")
    print("  T - Настройка торгового бота")
    print("  C - Переключение торгового бота")
    print("  ESC или закрытие окна - Выход")
    print()
    print("Запуск визуализации...")
    print()
    
    try:
        # Создаем симулятор
        simulator = TradingSimulator(
            initial_price=args.price,
            num_agents=args.agents,
            initial_balance=args.balance
        )
        
        # Создаем визуализатор
        visualizer = TradingVisualizer(simulator)
        
        # Запускаем визуализацию
        visualizer.run()
        
    except KeyboardInterrupt:
        print("\nСимуляция прервана пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
