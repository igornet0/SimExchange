"""
Модель для торгового агента
"""

import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .order import Order, OrderType


@dataclass
class Agent:
    """Торговый агент"""
    id: int
    balance: float
    position: int = 0  # Количество акций (может быть отрицательным)
    risk_tolerance: float = 0.5  # От 0 до 1
    trading_frequency: float = 0.3  # Вероятность торговли за цикл
    price_sensitivity: float = 0.8  # Чувствительность к изменениям цены
    
    # Статистика торговли
    buy_orders_count: int = 0
    sell_orders_count: int = 0
    total_orders_count: int = 0
    total_volume_traded: int = 0
    total_value_traded: float = 0.0
    
    # Внутреннее состояние
    last_trade_time: float = 0.0
    trade_cooldown: float = 1.0  # Минимальное время между сделками
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if self.balance < 0:
            raise ValueError("Баланс не может быть отрицательным")
        if not (0 <= self.risk_tolerance <= 1):
            raise ValueError("Толерантность к риску должна быть от 0 до 1")
        if not (0 <= self.trading_frequency <= 1):
            raise ValueError("Частота торговли должна быть от 0 до 1")
        if not (0 <= self.price_sensitivity <= 1):
            raise ValueError("Чувствительность к цене должна быть от 0 до 1")
    
    def should_trade(self, current_time: float) -> bool:
        """Определяет, должен ли агент торговать в данный момент"""
        if current_time - self.last_trade_time < self.trade_cooldown:
            return False
        return True  # Логика вероятности будет в стратегии
    
    def can_buy(self, price: float, quantity: int) -> bool:
        """Проверяет, может ли агент купить указанное количество по цене"""
        return self.balance >= price * quantity
    
    def can_sell(self, quantity: int) -> bool:
        """Проверяет, может ли агент продать указанное количество"""
        return self.position >= quantity
    
    def can_short_sell(self, quantity: int, max_short: int = 1000) -> bool:
        """Проверяет, может ли агент открыть короткую позицию"""
        return self.position - quantity >= -max_short
    
    def get_max_buy_quantity(self, price: float) -> int:
        """Возвращает максимальное количество акций, которое агент может купить"""
        if price <= 0:
            return 0
        return int(self.balance / price)
    
    def get_max_sell_quantity(self) -> int:
        """Возвращает максимальное количество акций, которое агент может продать"""
        return max(0, self.position)
    
    def get_portfolio_value(self, current_price: float) -> float:
        """Возвращает общую стоимость портфеля"""
        return self.balance + self.position * current_price
    
    def get_profit(self, initial_balance: float, current_price: float) -> float:
        """Возвращает прибыль/убыток относительно начального баланса"""
        current_value = self.get_portfolio_value(current_price)
        return current_value - initial_balance
    
    def get_profit_percentage(self, initial_balance: float, current_price: float) -> float:
        """Возвращает процент прибыли/убытка"""
        profit = self.get_profit(initial_balance, current_price)
        return (profit / initial_balance) * 100 if initial_balance > 0 else 0.0
    
    def update_after_trade(self, trade_price: float, trade_quantity: int, is_buyer: bool):
        """Обновляет состояние агента после сделки"""
        if is_buyer:
            # Покупатель тратит деньги и получает акции
            self.balance -= trade_price * trade_quantity
            self.position += trade_quantity
        else:
            # Продавец получает деньги и отдает акции
            self.balance += trade_price * trade_quantity
            self.position -= trade_quantity
        
        # Обновляем статистику
        self.total_volume_traded += trade_quantity
        self.total_value_traded += trade_price * trade_quantity
        self.last_trade_time = time.time()
    
    def add_order_statistics(self, order_type: OrderType):
        """Добавляет статистику по ордеру"""
        self.total_orders_count += 1
        if order_type == OrderType.BUY:
            self.buy_orders_count += 1
        else:
            self.sell_orders_count += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику агента"""
        return {
            'id': self.id,
            'balance': self.balance,
            'position': self.position,
            'risk_tolerance': self.risk_tolerance,
            'trading_frequency': self.trading_frequency,
            'price_sensitivity': self.price_sensitivity,
            'buy_orders': self.buy_orders_count,
            'sell_orders': self.sell_orders_count,
            'total_orders': self.total_orders_count,
            'total_volume': self.total_volume_traded,
            'total_value': self.total_value_traded,
            'last_trade_time': self.last_trade_time
        }
    
    def reset_statistics(self):
        """Сбрасывает статистику агента"""
        self.buy_orders_count = 0
        self.sell_orders_count = 0
        self.total_orders_count = 0
        self.total_volume_traded = 0
        self.total_value_traded = 0.0
        self.last_trade_time = 0.0
    
    def __str__(self) -> str:
        """Строковое представление агента"""
        return f"Agent(id={self.id}, balance={self.balance:.2f}, position={self.position})"
    
    def __repr__(self) -> str:
        """Детальное строковое представление"""
        return (f"Agent(id={self.id}, balance={self.balance}, position={self.position}, "
                f"risk_tolerance={self.risk_tolerance}, trading_frequency={self.trading_frequency})")
