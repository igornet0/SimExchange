"""
Модель для рыночных данных
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class MarketData:
    """Данные о состоянии рынка"""
    current_price: float
    price_history: List[float]
    volume_history: List[int]
    volatility: float
    spread: Optional[float] = None
    best_bid: Optional[float] = None
    best_ask: Optional[float] = None
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if self.current_price <= 0:
            raise ValueError("Текущая цена должна быть положительной")
        if self.volatility < 0:
            raise ValueError("Волатильность не может быть отрицательной")
        if self.spread is not None and self.spread < 0:
            raise ValueError("Спред не может быть отрицательным")
        if self.best_bid is not None and self.best_bid <= 0:
            raise ValueError("Лучшая цена покупки должна быть положительной")
        if self.best_ask is not None and self.best_ask <= 0:
            raise ValueError("Лучшая цена продажи должна быть положительной")
    
    def get_price_change(self, periods: int = 1) -> Optional[float]:
        """Возвращает изменение цены за указанное количество периодов"""
        if len(self.price_history) < periods + 1:
            return None
        
        current = self.current_price
        previous = self.price_history[-(periods + 1)]
        return current - previous
    
    def get_price_change_percentage(self, periods: int = 1) -> Optional[float]:
        """Возвращает процентное изменение цены"""
        price_change = self.get_price_change(periods)
        if price_change is None:
            return None
        
        if len(self.price_history) < periods + 1:
            return None
        
        previous = self.price_history[-(periods + 1)]
        if previous == 0:
            return None
        
        return (price_change / previous) * 100
    
    def get_average_price(self, periods: int = None) -> Optional[float]:
        """Возвращает среднюю цену за указанное количество периодов"""
        if not self.price_history:
            return None
        
        if periods is None:
            prices = self.price_history
        else:
            prices = self.price_history[-periods:]
        
        if not prices:
            return None
        
        return sum(prices) / len(prices)
    
    def get_price_volatility(self, periods: int = None) -> Optional[float]:
        """Возвращает волатильность цены за указанное количество периодов"""
        if not self.price_history or len(self.price_history) < 2:
            return None
        
        if periods is None:
            prices = self.price_history
        else:
            prices = self.price_history[-periods:]
        
        if len(prices) < 2:
            return None
        
        # Простое вычисление волатильности как стандартное отклонение изменений
        price_changes = []
        for i in range(1, len(prices)):
            change = (prices[i] - prices[i-1]) / prices[i-1]
            price_changes.append(change)
        
        if not price_changes:
            return None
        
        mean_change = sum(price_changes) / len(price_changes)
        variance = sum((change - mean_change) ** 2 for change in price_changes) / len(price_changes)
        return variance ** 0.5
    
    def get_total_volume(self, periods: int = None) -> int:
        """Возвращает общий объем торгов за указанное количество периодов"""
        if not self.volume_history:
            return 0
        
        if periods is None:
            volumes = self.volume_history
        else:
            volumes = self.volume_history[-periods:]
        
        return sum(volumes)
    
    def get_average_volume(self, periods: int = None) -> Optional[float]:
        """Возвращает средний объем торгов за указанное количество периодов"""
        if not self.volume_history:
            return None
        
        if periods is None:
            volumes = self.volume_history
        else:
            volumes = self.volume_history[-periods:]
        
        if not volumes:
            return None
        
        return sum(volumes) / len(volumes)
    
    def is_trending_up(self, periods: int = 5, threshold: float = 0.01) -> bool:
        """Проверяет, есть ли восходящий тренд"""
        price_change_pct = self.get_price_change_percentage(periods)
        return price_change_pct is not None and price_change_pct > threshold
    
    def is_trending_down(self, periods: int = 5, threshold: float = 0.01) -> bool:
        """Проверяет, есть ли нисходящий тренд"""
        price_change_pct = self.get_price_change_percentage(periods)
        return price_change_pct is not None and price_change_pct < -threshold
    
    def is_sideways(self, periods: int = 5, threshold: float = 0.01) -> bool:
        """Проверяет, движется ли цена в боковом направлении"""
        price_change_pct = self.get_price_change_percentage(periods)
        return price_change_pct is not None and abs(price_change_pct) <= threshold
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по рынку"""
        return {
            'current_price': self.current_price,
            'price_change_1': self.get_price_change(1),
            'price_change_5': self.get_price_change(5),
            'price_change_pct_1': self.get_price_change_percentage(1),
            'price_change_pct_5': self.get_price_change_percentage(5),
            'average_price_10': self.get_average_price(10),
            'average_price_20': self.get_average_price(20),
            'volatility': self.volatility,
            'price_volatility_10': self.get_price_volatility(10),
            'spread': self.spread,
            'best_bid': self.best_bid,
            'best_ask': self.best_ask,
            'total_volume_10': self.get_total_volume(10),
            'average_volume_10': self.get_average_volume(10),
            'trending_up_5': self.is_trending_up(5),
            'trending_down_5': self.is_trending_down(5),
            'sideways_5': self.is_sideways(5)
        }
    
    def __str__(self) -> str:
        """Строковое представление рыночных данных"""
        return (f"MarketData(price={self.current_price:.2f}, "
                f"volatility={self.volatility:.4f}, spread={self.spread})")
    
    def __repr__(self) -> str:
        """Детальное строковое представление"""
        return (f"MarketData(current_price={self.current_price}, "
                f"price_history_len={len(self.price_history)}, "
                f"volume_history_len={len(self.volume_history)}, "
                f"volatility={self.volatility}, spread={self.spread}, "
                f"best_bid={self.best_bid}, best_ask={self.best_ask})")
