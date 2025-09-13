import random
import time
from typing import Optional, List
from dataclasses import dataclass
from order_book import Order, OrderType
from trading_strategies import MarketData

@dataclass
class BotConfig:
    """Конфигурация бота"""
    enabled: bool = False
    order_interval: int = 10  # Каждые N циклов
    order_type: str = "random"  # "buy", "sell", "random", "both"
    price_offset: float = 0.01  # Отклонение от текущей цены (1%)
    quantity: int = 10  # Количество акций
    price_range_min: float = 0.95  # Минимальная цена (95% от текущей)
    price_range_max: float = 1.05  # Максимальная цена (105% от текущей)
    last_order_cycle: int = 0  # Последний цикл, когда была выставлена заявка

class TradingBot:
    """Бот для автоматического выставления заявок"""
    
    def __init__(self, bot_id: int = -1):
        self.bot_id = bot_id
        self.config = BotConfig()
        self.orders_placed = 0
        self.buy_orders = 0
        self.sell_orders = 0
        self.total_volume = 0
        
    def should_place_order(self, current_cycle: int) -> bool:
        """Определяет, должен ли бот выставить заявку в текущем цикле"""
        if not self.config.enabled:
            return False
        
        # Проверяем, прошло ли достаточно циклов с последней заявки
        cycles_since_last = current_cycle - self.config.last_order_cycle
        return cycles_since_last >= self.config.order_interval
    
    def generate_order(self, current_price: float, current_cycle: int, market_data: MarketData = None) -> Optional[Order]:
        """Генерирует заявку для бота"""
        if not self.should_place_order(current_cycle):
            return None
        
        # Определяем тип заявки
        order_type = self._determine_order_type()
        if order_type is None:
            return None
        
        # Генерируем цену
        price = self._generate_price(current_price, order_type)
        
        # Генерируем количество
        quantity = self._generate_quantity()
        
        # Создаем заявку
        order = Order(
            id=0,  # Будет установлен в симуляторе
            price=price,
            quantity=quantity,
            order_type=order_type,
            agent_id=self.bot_id,
            timestamp=time.time()
        )
        
        # Обновляем статистику
        self.orders_placed += 1
        self.total_volume += quantity
        if order_type == OrderType.BUY:
            self.buy_orders += 1
        else:
            self.sell_orders += 1
        
        # Обновляем последний цикл заявки
        self.config.last_order_cycle = current_cycle
        
        return order
    
    def _determine_order_type(self) -> Optional[OrderType]:
        """Определяет тип заявки на основе конфигурации"""
        if self.config.order_type == "buy":
            return OrderType.BUY
        elif self.config.order_type == "sell":
            return OrderType.SELL
        elif self.config.order_type == "random":
            return OrderType.BUY if random.random() < 0.5 else OrderType.SELL
        elif self.config.order_type == "both":
            # Выставляем заявки с обеих сторон
            return OrderType.BUY if random.random() < 0.5 else OrderType.SELL
        else:
            return None
    
    def _generate_price(self, current_price: float, order_type: OrderType) -> float:
        """Генерирует цену для заявки"""
        # Базовое отклонение
        base_offset = self.config.price_offset
        
        # Добавляем случайность
        random_factor = random.uniform(0.5, 1.5)
        offset = base_offset * random_factor
        
        if order_type == OrderType.BUY:
            # Для покупки - цена ниже текущей
            price = current_price * (1 - offset)
        else:
            # Для продажи - цена выше текущей
            price = current_price * (1 + offset)
        
        # Ограничиваем цену заданным диапазоном
        min_price = current_price * self.config.price_range_min
        max_price = current_price * self.config.price_range_max
        price = max(min_price, min(max_price, price))
        
        return round(price, 2)
    
    def _generate_quantity(self) -> int:
        """Генерирует количество для заявки"""
        # Базовое количество из конфигурации
        base_quantity = self.config.quantity
        
        # Добавляем небольшую случайность (±20%)
        variation = random.uniform(0.8, 1.2)
        quantity = int(base_quantity * variation)
        
        # Минимум 1 акция
        return max(1, quantity)
    
    def update_config(self, **kwargs):
        """Обновляет конфигурацию бота"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def get_statistics(self) -> dict:
        """Возвращает статистику бота"""
        return {
            'bot_id': self.bot_id,
            'enabled': self.config.enabled,
            'order_interval': self.config.order_interval,
            'order_type': self.config.order_type,
            'orders_placed': self.orders_placed,
            'buy_orders': self.buy_orders,
            'sell_orders': self.sell_orders,
            'total_volume': self.total_volume,
            'last_order_cycle': self.config.last_order_cycle,
            'price_offset': self.config.price_offset,
            'quantity': self.config.quantity
        }
    
    def reset_statistics(self):
        """Сбрасывает статистику бота"""
        self.orders_placed = 0
        self.buy_orders = 0
        self.sell_orders = 0
        self.total_volume = 0
        self.config.last_order_cycle = 0

