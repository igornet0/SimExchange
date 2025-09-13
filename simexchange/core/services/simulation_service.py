"""
Сервис для управления симуляцией
"""

import time
from typing import List, Optional, Dict, Any
from ..models import (
    Order, Trade, Agent, MarketData, SimulationConfig,
    OrderType
)


class SimulationService:
    """Сервис для управления симуляцией"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.cycle = 0
        self.is_running = False
        
        # История данных
        self.price_history: List[float] = [config.initial_price]
        self.volume_history: List[int] = [0]
        self.trade_count_history: List[int] = [0]
        self.spread_history: List[float] = []
        
        # Кэш для оптимизации
        self._cached_data: Optional[Dict[str, Any]] = None
        self._last_data_update_cycle = -1
        
        # Настройки увеличения баланса
        self.last_balance_increase_cycle = 0
    
    def get_current_price(self) -> float:
        """Возвращает текущую цену"""
        return self.price_history[-1] if self.price_history else self.config.initial_price
    
    def get_price_history(self, limit: Optional[int] = None) -> List[float]:
        """Возвращает историю цен"""
        if limit is None:
            return self.price_history.copy()
        return self.price_history[-limit:] if limit > 0 else []
    
    def get_volume_history(self, limit: Optional[int] = None) -> List[int]:
        """Возвращает историю объемов"""
        if limit is None:
            return self.volume_history.copy()
        return self.volume_history[-limit:] if limit > 0 else []
    
    def get_trade_count_history(self, limit: Optional[int] = None) -> List[int]:
        """Возвращает историю количества сделок"""
        if limit is None:
            return self.trade_count_history.copy()
        return self.trade_count_history[-limit:] if limit > 0 else []
    
    def get_spread_history(self, limit: Optional[int] = None) -> List[float]:
        """Возвращает историю спредов"""
        if limit is None:
            return self.spread_history.copy()
        return self.spread_history[-limit:] if limit > 0 else []
    
    def calculate_volatility(self) -> float:
        """Вычисляет волатильность на основе истории цен"""
        if len(self.price_history) < 2:
            return 0.01  # Базовая волатильность
        
        if self.config.skip_volatility_calculation:
            return 0.01  # Фиксированная волатильность для производительности
        
        # Используем только последние 5 цен для быстрого расчета
        recent_prices = self.price_history[-5:]
        if len(recent_prices) < 2:
            return 0.01
        
        # Упрощенный расчет волатильности
        price_changes = []
        for i in range(1, len(recent_prices)):
            change = (recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
            price_changes.append(change)
        
        if not price_changes:
            return 0.01
        
        # Простое среднее абсолютных изменений
        avg_change = sum(abs(c) for c in price_changes) / len(price_changes)
        volatility = min(avg_change * 2, 0.05)  # Ограничиваем максимумом
        
        return max(0.005, volatility)
    
    def get_average_spread(self) -> Optional[float]:
        """Возвращает средний спред за последние N циклов"""
        if not self.spread_history:
            return None
        
        # Берем последние N циклов или все доступные
        cycles_to_use = min(self.config.avg_spread_cycles, len(self.spread_history))
        recent_spreads = self.spread_history[-cycles_to_use:]
        
        return sum(recent_spreads) / len(recent_spreads)
    
    def update_price(self, new_price: float):
        """Обновляет текущую цену"""
        self.price_history.append(new_price)
        
        # Ограничиваем размер истории
        if len(self.price_history) > self.config.max_history_size:
            keep_size = self.config.max_history_size // 2
            self.price_history = self.price_history[-keep_size:]
    
    def update_volume(self, volume: int):
        """Обновляет объем торгов"""
        self.volume_history.append(volume)
        
        # Ограничиваем размер истории
        if len(self.volume_history) > self.config.max_history_size:
            keep_size = self.config.max_history_size // 2
            self.volume_history = self.volume_history[-keep_size:]
    
    def update_trade_count(self, count: int):
        """Обновляет количество сделок"""
        self.trade_count_history.append(count)
        
        # Ограничиваем размер истории
        if len(self.trade_count_history) > self.config.max_history_size:
            keep_size = self.config.max_history_size // 2
            self.trade_count_history = self.trade_count_history[-keep_size:]
    
    def update_spread(self, spread: float):
        """Обновляет спред"""
        self.spread_history.append(spread)
        
        # Ограничиваем размер истории
        if len(self.spread_history) > self.config.max_history_size:
            keep_size = self.config.max_history_size // 2
            self.spread_history = self.spread_history[-keep_size:]
    
    def increment_cycle(self):
        """Увеличивает счетчик циклов"""
        self.cycle += 1
    
    def should_increase_balance(self) -> bool:
        """Проверяет, нужно ли увеличить баланс агентов"""
        return (self.cycle - self.last_balance_increase_cycle >= 
                self.config.balance_increase_cycles)
    
    def mark_balance_increased(self):
        """Отмечает, что баланс был увеличен"""
        self.last_balance_increase_cycle = self.cycle
    
    def get_balance_increase_info(self) -> Dict[str, Any]:
        """Возвращает информацию об увеличении баланса"""
        cycles_remaining = (self.config.balance_increase_cycles - 
                          (self.cycle - self.last_balance_increase_cycle))
        
        return {
            'cycles': self.config.balance_increase_cycles,
            'amount': self.config.balance_increase_amount,
            'next_increase': cycles_remaining,
            'last_increase_cycle': self.last_balance_increase_cycle
        }
    
    def create_market_data(self, current_price: float, spread: Optional[float] = None,
                          best_bid: Optional[float] = None, best_ask: Optional[float] = None) -> MarketData:
        """Создает объект MarketData для текущего состояния рынка"""
        volatility = self.calculate_volatility()
        
        return MarketData(
            current_price=current_price,
            price_history=self.get_price_history(20),  # Последние 20 цен
            volume_history=self.get_volume_history(20),  # Последние 20 объемов
            volatility=volatility,
            spread=spread,
            best_bid=best_bid,
            best_ask=best_ask
        )
    
    def get_simulation_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику симуляции"""
        return {
            'cycle': self.cycle,
            'current_price': self.get_current_price(),
            'price_history_length': len(self.price_history),
            'volume_history_length': len(self.volume_history),
            'trade_count_history_length': len(self.trade_count_history),
            'spread_history_length': len(self.spread_history),
            'average_spread': self.get_average_spread(),
            'volatility': self.calculate_volatility(),
            'balance_increase_info': self.get_balance_increase_info(),
            'performance_mode': self.config.performance_mode,
            'skip_volatility_calculation': self.config.skip_volatility_calculation
        }
    
    def reset(self):
        """Сбрасывает симуляцию к начальному состоянию"""
        self.cycle = 0
        self.is_running = False
        self.price_history = [self.config.initial_price]
        self.volume_history = [0]
        self.trade_count_history = [0]
        self.spread_history = []
        self.last_balance_increase_cycle = 0
        self._cached_data = None
        self._last_data_update_cycle = -1
    
    def __str__(self) -> str:
        """Строковое представление сервиса"""
        return f"SimulationService(cycle={self.cycle}, price={self.get_current_price():.2f})"
    
    def __repr__(self) -> str:
        """Детальное строковое представление"""
        return (f"SimulationService(cycle={self.cycle}, is_running={self.is_running}, "
                f"price_history_len={len(self.price_history)}, "
                f"config={self.config})")
