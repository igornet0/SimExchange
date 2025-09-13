"""
Базовые тесты для проверки функциональности новой архитектуры
"""

import unittest
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from simexchange.core.models import (
    Order, OrderType, Trade, Agent, MarketData, SimulationConfig
)
from simexchange.core.services import TradingSimulator


class TestModels(unittest.TestCase):
    """Тесты для моделей данных"""
    
    def test_order_creation(self):
        """Тест создания ордера"""
        order = Order.create_buy_order(1, 100.0, 10, 0)
        
        self.assertEqual(order.id, 1)
        self.assertEqual(order.price, 100.0)
        self.assertEqual(order.quantity, 10)
        self.assertEqual(order.order_type, OrderType.BUY)
        self.assertEqual(order.agent_id, 0)
    
    def test_order_validation(self):
        """Тест валидации ордера"""
        with self.assertRaises(ValueError):
            Order.create_buy_order(1, -100.0, 10, 0)  # Отрицательная цена
        
        with self.assertRaises(ValueError):
            Order.create_buy_order(1, 100.0, -10, 0)  # Отрицательное количество
    
    def test_trade_creation(self):
        """Тест создания сделки"""
        buy_order = Order.create_buy_order(1, 100.0, 10, 0)
        sell_order = Order.create_sell_order(2, 99.0, 10, 1)
        
        trade = Trade.create_from_orders(1, buy_order, sell_order, 5)
        
        self.assertEqual(trade.id, 1)
        self.assertEqual(trade.price, 99.0)  # Цена продавца
        self.assertEqual(trade.quantity, 5)
        self.assertEqual(trade.buyer_id, 0)
        self.assertEqual(trade.seller_id, 1)
    
    def test_agent_creation(self):
        """Тест создания агента"""
        agent = Agent(0, 10000.0)
        
        self.assertEqual(agent.id, 0)
        self.assertEqual(agent.balance, 10000.0)
        self.assertEqual(agent.position, 0)
        self.assertTrue(0 <= agent.risk_tolerance <= 1)
    
    def test_agent_trading(self):
        """Тест торговли агента"""
        agent = Agent(0, 10000.0)
        
        # Проверяем возможность покупки
        self.assertTrue(agent.can_buy(100.0, 10))
        self.assertFalse(agent.can_buy(100.0, 200))  # Недостаточно денег
        
        # Проверяем возможность продажи
        self.assertFalse(agent.can_sell(10))  # Нет акций
        agent.position = 20
        self.assertTrue(agent.can_sell(10))
        self.assertFalse(agent.can_sell(30))  # Недостаточно акций
    
    def test_market_data_creation(self):
        """Тест создания рыночных данных"""
        market_data = MarketData(
            current_price=100.0,
            price_history=[99.0, 100.0, 101.0],
            volume_history=[10, 20, 15],
            volatility=0.01
        )
        
        self.assertEqual(market_data.current_price, 100.0)
        self.assertEqual(len(market_data.price_history), 3)
        self.assertEqual(market_data.volatility, 0.01)
    
    def test_simulation_config(self):
        """Тест конфигурации симуляции"""
        config = SimulationConfig(
            initial_price=100.0,
            num_agents=10,
            initial_balance=5000.0
        )
        
        self.assertEqual(config.initial_price, 100.0)
        self.assertEqual(config.num_agents, 10)
        self.assertEqual(config.initial_balance, 5000.0)


class TestServices(unittest.TestCase):
    """Тесты для сервисов"""
    
    def setUp(self):
        """Настройка для тестов"""
        self.config = SimulationConfig(
            initial_price=100.0,
            num_agents=5,
            initial_balance=10000.0
        )
        self.simulator = TradingSimulator(self.config)
    
    def test_simulator_creation(self):
        """Тест создания симулятора"""
        self.assertEqual(self.simulator.cycle, 0)
        self.assertEqual(len(self.simulator.agent_service.get_agents()), 5)
        self.assertEqual(self.simulator.simulation_service.get_current_price(), 100.0)
    
    def test_single_cycle(self):
        """Тест выполнения одного цикла"""
        initial_cycle = self.simulator.cycle
        trades = self.simulator.run_cycle()
        
        self.assertEqual(self.simulator.cycle, initial_cycle + 1)
        self.assertIsInstance(trades, list)
    
    def test_simulation_data(self):
        """Тест получения данных симуляции"""
        data = self.simulator.get_simulation_data()
        
        self.assertIn('cycle', data)
        self.assertIn('order_book', data)
        self.assertIn('agents', data)
        self.assertIn('price_history', data)
        self.assertEqual(len(data['agents']), 5)
    
    def test_reset(self):
        """Тест сброса симуляции"""
        # Выполняем несколько циклов
        for _ in range(5):
            self.simulator.run_cycle()
        
        # Сбрасываем
        self.simulator.reset()
        
        self.assertEqual(self.simulator.cycle, 0)
        self.assertEqual(len(self.simulator.agent_service.get_agents()), 5)


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def test_full_simulation_cycle(self):
        """Тест полного цикла симуляции"""
        config = SimulationConfig(
            initial_price=100.0,
            num_agents=10,
            initial_balance=10000.0
        )
        simulator = TradingSimulator(config)
        
        # Выполняем 10 циклов
        for i in range(10):
            trades = simulator.run_cycle()
            self.assertIsInstance(trades, list)
        
        # Проверяем, что данные обновились
        data = simulator.get_simulation_data()
        self.assertEqual(data['cycle'], 10)
        self.assertGreater(len(data['price_history']), 1)
        self.assertGreater(data['total_trades'], 0)


if __name__ == '__main__':
    # Запускаем тесты
    unittest.main(verbosity=2)
