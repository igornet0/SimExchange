#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы торгового бота
"""

from simulator import TradingSimulator

def test_bot():
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ТОРГОВОГО БОТА")
    print("=" * 60)
    
    # Создаем симулятор
    simulator = TradingSimulator(initial_price=100.0, num_agents=5, initial_balance=10000.0)
    
    # Включаем бота
    simulator.toggle_bot(True)
    
    # Настраиваем бота
    simulator.set_bot_config(
        order_interval=5,  # Каждые 5 циклов
        order_type="random",  # Случайные заявки
        quantity=5,  # 5 акций
        price_offset=0.02  # 2% отклонение
    )
    
    print("Настройки бота:")
    bot_stats = simulator.get_bot_statistics()
    for key, value in bot_stats.items():
        print(f"  {key}: {value}")
    print()
    
    # Запускаем симуляцию на 50 циклов
    print("Запуск симуляции на 50 циклов...")
    print()
    
    for cycle in range(50):
        trades = simulator.run_cycle()
        
        # Показываем информацию каждые 10 циклов
        if cycle % 10 == 0:
            data = simulator.get_simulation_data()
            bot_stats = data['bot_statistics']
            
            print(f"Цикл {cycle}:")
            print(f"  Цена: {data['order_book']['current_price']:.2f}")
            print(f"  Сделок: {len(trades)}")
            print(f"  Бот заявок: {bot_stats['orders_placed']}")
            print(f"  Бот объем: {bot_stats['total_volume']}")
            print()
    
    # Финальная статистика
    print("=" * 60)
    print("ФИНАЛЬНАЯ СТАТИСТИКА")
    print("=" * 60)
    
    data = simulator.get_simulation_data()
    bot_stats = data['bot_statistics']
    
    print("Общая статистика:")
    print(f"  Циклов: {data['cycle']}")
    print(f"  Общих сделок: {data['total_trades']}")
    print(f"  Общий объем: {data['total_volume']}")
    print()
    
    print("Статистика бота:")
    print(f"  Заявок выставлено: {bot_stats['orders_placed']}")
    print(f"  Покупок: {bot_stats['buy_orders']}")
    print(f"  Продаж: {bot_stats['sell_orders']}")
    print(f"  Объем торгов: {bot_stats['total_volume']}")
    print(f"  Последняя заявка: цикл {bot_stats['last_order_cycle']}")
    print()
    
    # Тестируем разные типы заявок
    print("Тестирование разных типов заявок...")
    
    # Тест 1: Только покупки
    simulator.set_bot_config(order_type="buy", order_interval=3)
    print("  Тип: только покупки, интервал: 3 цикла")
    
    for cycle in range(10):
        simulator.run_cycle()
    
    bot_stats = simulator.get_bot_statistics()
    print(f"  Результат: {bot_stats['buy_orders']} покупок, {bot_stats['sell_orders']} продаж")
    
    # Тест 2: Только продажи
    simulator.set_bot_config(order_type="sell", order_interval=2)
    print("  Тип: только продажи, интервал: 2 цикла")
    
    for cycle in range(10):
        simulator.run_cycle()
    
    bot_stats = simulator.get_bot_statistics()
    print(f"  Результат: {bot_stats['buy_orders']} покупок, {bot_stats['sell_orders']} продаж")
    
    print()
    print("Тестирование завершено успешно!")

if __name__ == "__main__":
    test_bot()

