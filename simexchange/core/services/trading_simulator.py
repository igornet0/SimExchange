"""
Основной сервис-координатор для симуляции торговли
"""

from typing import List, Dict, Any, Optional
from ..models import (
    Order, Trade, Agent, MarketData, SimulationConfig,
    OrderType
)
from .simulation_service import SimulationService
from .order_book_service import OrderBookService
from .agent_service import AgentService


class TradingSimulator:
    """Основной сервис-координатор для симуляции торговли"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        
        # Инициализируем сервисы
        self.simulation_service = SimulationService(config)
        self.order_book_service = OrderBookService(
            config.initial_price, 
            config.max_trades_history
        )
        self.agent_service = AgentService(config)
        
        # Создаем агентов
        self.agent_service.create_agents(config.num_agents)
        
        # Торговый бот (пока что заглушка)
        self.trading_bot = None  # Будет добавлен позже
    
    def run_cycle(self) -> List[Trade]:
        """Выполняет один цикл симуляции"""
        # Увеличиваем счетчик циклов
        self.simulation_service.increment_cycle()
        
        # Получаем текущую цену
        current_price = self.simulation_service.get_current_price()
        
        # Создаем данные о рынке
        market_data = self.simulation_service.create_market_data(
            current_price,
            self.order_book_service.get_spread(),
            self.order_book_service.get_best_bid(),
            self.order_book_service.get_best_ask()
        )
        
        # Агенты генерируют ордера
        new_trades = []
        for agent in self.agent_service.get_agents():
            order = self._generate_agent_order(agent, market_data)
            if order:
                # Добавляем ордер в стакан
                trades = self.order_book_service.add_order(order)
                new_trades.extend(trades)
                
                # Обновляем статистику агента
                self.agent_service.add_agent_order_statistics(agent.id, order.order_type)
                
                # Обновляем состояние агентов после сделок
                for trade in trades:
                    if trade.buyer_id == agent.id:
                        self.agent_service.update_agent_after_trade(
                            agent.id, trade.price, trade.quantity, True
                        )
                    elif trade.seller_id == agent.id:
                        self.agent_service.update_agent_after_trade(
                            agent.id, trade.price, trade.quantity, False
                        )
        
        # Проверяем увеличение баланса
        if self.simulation_service.should_increase_balance():
            self.agent_service.increase_all_balances(self.config.balance_increase_amount)
            self.simulation_service.mark_balance_increased()
        
        # Обновляем статистику симуляции
        self._update_simulation_statistics(new_trades)
        
        return new_trades
    
    def _generate_agent_order(self, agent: Agent, market_data: MarketData) -> Optional[Order]:
        """Генерирует ордер для агента (упрощенная версия)"""
        import time
        import random
        
        current_time = time.time()
        
        # Проверяем, должен ли агент торговать
        if not agent.should_trade(current_time):
            return None
        
        # Простая логика генерации ордеров (заглушка)
        # В будущем здесь будет использоваться стратегия агента
        if random.random() > agent.trading_frequency:
            return None
        
        # Определяем тип ордера
        if random.random() < 0.5:
            order_type = OrderType.BUY
        else:
            order_type = OrderType.SELL
        
        # Генерируем цену
        price_variation = random.uniform(0.95, 1.05) * agent.price_sensitivity
        price = market_data.current_price * price_variation
        
        # Генерируем количество
        if order_type == OrderType.BUY:
            max_quantity = int((agent.balance * agent.risk_tolerance) / price)
            if max_quantity <= 0:
                return None
            quantity = random.randint(1, max(1, max_quantity))
        else:  # SELL
            # Для продажи используем короткие продажи если нет позиции
            if agent.position <= 0:
                max_quantity = 10  # Ограничиваем короткие продажи
            else:
                max_quantity = agent.position
            if max_quantity <= 0:
                return None
            quantity = random.randint(1, max(1, max_quantity))
        
        # Проверяем возможность торговли
        if order_type == OrderType.BUY:
            if not agent.can_buy(price, quantity):
                return None
        else:  # SELL
            # Разрешаем короткие продажи
            if not agent.can_short_sell(quantity):
                return None
        
        # Создаем ордер
        order = Order(
            id=self.order_book_service.next_order_id,
            price=price,
            quantity=quantity,
            order_type=order_type,
            agent_id=agent.id,
            timestamp=current_time
        )
        
        self.order_book_service.next_order_id += 1
        
        return order
    
    def _update_simulation_statistics(self, new_trades: List[Trade]):
        """Обновляет статистику симуляции"""
        # Обновляем цену
        current_price = self.order_book_service.current_price
        self.simulation_service.update_price(current_price)
        
        # Обновляем объем
        total_volume = sum(trade.quantity for trade in new_trades)
        self.simulation_service.update_volume(total_volume)
        
        # Обновляем количество сделок
        self.simulation_service.update_trade_count(len(new_trades))
        
        # Обновляем спред
        spread = self.order_book_service.get_spread()
        if spread is not None:
            self.simulation_service.update_spread(spread)
    
    def get_simulation_data(self) -> Dict[str, Any]:
        """Возвращает данные для отображения"""
        current_price = self.simulation_service.get_current_price()
        
        # Получаем данные стакана
        order_book_data = self.order_book_service.get_order_book_data()
        
        # Получаем статистику агентов
        agent_stats = self.agent_service.get_agent_statistics(current_price)
        
        # Получаем статистику симуляции
        sim_stats = self.simulation_service.get_simulation_statistics()
        
        return {
            'cycle': self.simulation_service.cycle,
            'order_book': order_book_data,
            'agents': agent_stats,
            'price_history': self.simulation_service.get_price_history(50),
            'volume_history': self.simulation_service.get_volume_history(50),
            'trade_count_history': self.simulation_service.get_trade_count_history(50),
            'total_trades': len(self.order_book_service.trades),
            'total_volume': self.order_book_service.get_total_volume(),
            'average_spread': self.simulation_service.get_average_spread(),
            'avg_spread_cycles': self.config.avg_spread_cycles,
            'balance_increase_info': self.simulation_service.get_balance_increase_info(),
            'simulation_stats': sim_stats
        }
    
    def get_agent_performance_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по производительности агентов"""
        current_price = self.simulation_service.get_current_price()
        return self.agent_service.get_agent_performance_summary(current_price)
    
    def get_price_chart_data(self) -> Dict[str, Any]:
        """Возвращает данные для построения графика цены"""
        return {
            'prices': self.simulation_service.get_price_history(),
            'volumes': self.simulation_service.get_volume_history(),
            'cycles': list(range(len(self.simulation_service.price_history)))
        }
    
    def reset(self):
        """Сбрасывает симуляцию"""
        self.simulation_service.reset()
        self.order_book_service.reset()
        self.agent_service.reset_all_agents()
    
    def set_performance_mode(self, enabled: bool, skip_volatility: bool = False):
        """Устанавливает режим производительности"""
        self.config.performance_mode = enabled
        self.config.skip_volatility_calculation = skip_volatility
    
    def set_balance_increase_settings(self, cycles: int, amount: float):
        """Устанавливает параметры увеличения баланса"""
        self.config.balance_increase_cycles = max(1, min(cycles, 10000))
        self.config.balance_increase_amount = max(0, amount)
    
    def set_avg_spread_cycles(self, cycles: int):
        """Устанавливает количество циклов для расчета среднего спреда"""
        self.config.avg_spread_cycles = max(1, min(cycles, 1000))
    
    def get_config(self) -> SimulationConfig:
        """Возвращает конфигурацию симуляции"""
        return self.config
    
    def update_config(self, **kwargs):
        """Обновляет конфигурацию симуляции"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    @property
    def cycle(self) -> int:
        """Возвращает текущий цикл"""
        return self.simulation_service.cycle
    
    @property
    def is_running(self) -> bool:
        """Возвращает статус выполнения"""
        return self.simulation_service.is_running
    
    @is_running.setter
    def is_running(self, value: bool):
        """Устанавливает статус выполнения"""
        self.simulation_service.is_running = value
    
    def __str__(self) -> str:
        """Строковое представление симулятора"""
        return (f"TradingSimulator(cycle={self.cycle}, "
                f"agents={self.agent_service.get_agent_count()}, "
                f"price={self.simulation_service.get_current_price():.2f})")
    
    def __repr__(self) -> str:
        """Детальное строковое представление"""
        return (f"TradingSimulator(config={self.config}, "
                f"cycle={self.cycle}, "
                f"agents_count={self.agent_service.get_agent_count()})")
