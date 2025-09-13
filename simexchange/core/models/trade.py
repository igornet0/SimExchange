"""
Модель для сделок
"""

import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class Trade:
    """Сделка между двумя агентами"""
    id: int
    price: float
    quantity: int
    buyer_id: int
    seller_id: int
    timestamp: float
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if self.price <= 0:
            raise ValueError("Цена должна быть положительной")
        if self.quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        if self.buyer_id < 0:
            raise ValueError("ID покупателя должен быть неотрицательным")
        if self.seller_id < 0:
            raise ValueError("ID продавца должен быть неотрицательным")
        # Убираем проверку на одинаковых агентов, так как это может происходить в симуляции
    
    @classmethod
    def create_from_orders(cls, trade_id: int, buy_order: 'Order', sell_order: 'Order', 
                          quantity: int) -> 'Trade':
        """Создает сделку из двух ордеров"""
        if not buy_order.is_buy():
            raise ValueError("Первый ордер должен быть ордером на покупку")
        if not sell_order.is_sell():
            raise ValueError("Второй ордер должен быть ордером на продажу")
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        if quantity > min(buy_order.quantity, sell_order.quantity):
            raise ValueError("Количество сделки не может превышать количество в ордерах")
        
        # Цена сделки - это цена ордера на продажу (приоритет времени)
        return cls(
            id=trade_id,
            price=sell_order.price,
            quantity=quantity,
            buyer_id=buy_order.agent_id,
            seller_id=sell_order.agent_id,
            timestamp=time.time()
        )
    
    def get_total_value(self) -> float:
        """Возвращает общую стоимость сделки"""
        return self.price * self.quantity
    
    def get_buyer_value(self) -> float:
        """Возвращает стоимость для покупателя (отрицательная)"""
        return -self.get_total_value()
    
    def get_seller_value(self) -> float:
        """Возвращает стоимость для продавца (положительная)"""
        return self.get_total_value()
    
    def involves_agent(self, agent_id: int) -> bool:
        """Проверяет, участвует ли агент в сделке"""
        return self.buyer_id == agent_id or self.seller_id == agent_id
    
    def get_agent_role(self, agent_id: int) -> Optional[str]:
        """Возвращает роль агента в сделке"""
        if self.buyer_id == agent_id:
            return "buyer"
        elif self.seller_id == agent_id:
            return "seller"
        return None
    
    def get_agent_quantity_change(self, agent_id: int) -> int:
        """Возвращает изменение количества акций для агента"""
        if self.buyer_id == agent_id:
            return self.quantity  # Покупатель получает акции
        elif self.seller_id == agent_id:
            return -self.quantity  # Продавец отдает акции
        return 0
    
    def get_agent_value_change(self, agent_id: int) -> float:
        """Возвращает изменение баланса для агента"""
        if self.buyer_id == agent_id:
            return self.get_buyer_value()  # Покупатель тратит деньги
        elif self.seller_id == agent_id:
            return self.get_seller_value()  # Продавец получает деньги
        return 0.0
    
    def __str__(self) -> str:
        """Строковое представление сделки"""
        return (f"Trade(id={self.id}, price={self.price:.2f}, qty={self.quantity}, "
                f"buyer={self.buyer_id}, seller={self.seller_id})")
    
    def __repr__(self) -> str:
        """Детальное строковое представление"""
        return (f"Trade(id={self.id}, price={self.price}, quantity={self.quantity}, "
                f"buyer_id={self.buyer_id}, seller_id={self.seller_id}, "
                f"timestamp={self.timestamp})")
