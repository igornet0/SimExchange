"""
Модели для ордеров и типов ордеров
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OrderType(Enum):
    """Тип ордера"""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    """Ордер на покупку или продажу"""
    id: int
    price: float
    quantity: int
    order_type: OrderType
    agent_id: int
    timestamp: float
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if self.price <= 0:
            raise ValueError("Цена должна быть положительной")
        if self.quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        if self.agent_id < 0:
            raise ValueError("ID агента должен быть неотрицательным")
    
    @classmethod
    def create_buy_order(cls, order_id: int, price: float, quantity: int, agent_id: int) -> 'Order':
        """Создает ордер на покупку"""
        return cls(
            id=order_id,
            price=price,
            quantity=quantity,
            order_type=OrderType.BUY,
            agent_id=agent_id,
            timestamp=time.time()
        )
    
    @classmethod
    def create_sell_order(cls, order_id: int, price: float, quantity: int, agent_id: int) -> 'Order':
        """Создает ордер на продажу"""
        return cls(
            id=order_id,
            price=price,
            quantity=quantity,
            order_type=OrderType.SELL,
            agent_id=agent_id,
            timestamp=time.time()
        )
    
    def is_buy(self) -> bool:
        """Проверяет, является ли ордер ордером на покупку"""
        return self.order_type == OrderType.BUY
    
    def is_sell(self) -> bool:
        """Проверяет, является ли ордер ордером на продажу"""
        return self.order_type == OrderType.SELL
    
    def get_total_value(self) -> float:
        """Возвращает общую стоимость ордера"""
        return self.price * self.quantity
    
    def can_match_with(self, other: 'Order') -> bool:
        """Проверяет, может ли ордер совпасть с другим ордером"""
        if self.order_type == other.order_type:
            return False  # Одинаковые типы ордеров не могут совпасть
        
        if self.is_buy() and other.is_sell():
            return self.price >= other.price
        elif self.is_sell() and other.is_buy():
            return self.price <= other.price
        
        return False
    
    def __str__(self) -> str:
        """Строковое представление ордера"""
        return f"Order(id={self.id}, {self.order_type.value}, price={self.price:.2f}, qty={self.quantity}, agent={self.agent_id})"
    
    def __repr__(self) -> str:
        """Детальное строковое представление"""
        return (f"Order(id={self.id}, price={self.price}, quantity={self.quantity}, "
                f"order_type={self.order_type.value}, agent_id={self.agent_id}, "
                f"timestamp={self.timestamp})")
