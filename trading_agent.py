import random
import time
from typing import List, Optional
from dataclasses import dataclass
from order_book import Order, OrderType
from trading_strategies import TradingStrategy, StrategyType, MarketData, create_strategy, get_strategy_distribution

@dataclass
class Agent:
    id: int
    balance: float
    position: int  # Количество акций (может быть отрицательным)
    strategy: TradingStrategy  # Торговая стратегия
    risk_tolerance: float  # От 0 до 1
    trading_frequency: float  # Вероятность торговли за цикл
    price_sensitivity: float  # Чувствительность к изменениям цены
    
    def __init__(self, agent_id: int, initial_balance: float, strategy_type: StrategyType = None):
        self.id = agent_id
        self.balance = initial_balance
        self.position = 0
        
        # Выбираем стратегию
        if strategy_type is None:
            # Случайный выбор стратегии
            strategy_types = list(StrategyType)
            strategy_type = random.choice(strategy_types)
        
        self.strategy = create_strategy(agent_id, strategy_type)
        
        # Базовые параметры (могут быть переопределены стратегией)
        self.risk_tolerance = random.uniform(0.3, 0.8)
        self.trading_frequency = random.uniform(0.1, 0.4)
        self.price_sensitivity = random.uniform(0.5, 1.0)
        self.last_trade_time = 0
        self.trade_cooldown = random.uniform(0.5, 2.0)  # Минимальное время между сделками
        
        # Статистика заявок
        self.buy_orders_count = 0
        self.sell_orders_count = 0
        self.total_orders_count = 0
    
    def should_trade(self, current_time: float) -> bool:
        """Определяет, должен ли агент торговать в данный момент"""
        if current_time - self.last_trade_time < self.trade_cooldown:
            return False
        return random.random() < self.trading_frequency
    
    def generate_order(self, current_price: float, price_volatility: float, market_data: MarketData = None) -> Optional[Order]:
        """Генерирует ордер на основе стратегии"""
        if not self.should_trade(time.time()):
            return None
        
        # Создаем данные о рынке, если не переданы
        if market_data is None:
            market_data = MarketData(
                current_price=current_price,
                price_history=[current_price],
                volume_history=[0],
                volatility=price_volatility,
                spread=None,
                best_bid=None,
                best_ask=None
            )
        
        # Используем стратегию для генерации ордера
        order = self.strategy.generate_order(market_data, self.balance, self.position)
        
        if order:
            order.agent_id = self.id
            order.timestamp = time.time()
            self.last_trade_time = time.time()
            
            # Увеличиваем счетчики заявок
            self.total_orders_count += 1
            if order.order_type == OrderType.BUY:
                self.buy_orders_count += 1
            else:  # SELL
                self.sell_orders_count += 1
        
        return order
    
    def _decide_order_type(self, current_price: float, price_volatility: float) -> Optional[OrderType]:
        """Решает, какой тип ордера создать"""
        # Базовые вероятности
        buy_probability = 0.5
        sell_probability = 0.5
        
        # Влияние типа агента
        if self.id % 5 == 0:  # Агенты-продавцы
            sell_probability += 0.3
        elif self.id % 7 == 0:  # Агенты-покупатели
            buy_probability += 0.3
        
        # Влияние текущей позиции
        if self.position > 0:
            sell_probability += 0.3  # Больше склонны продавать при длинной позиции
        elif self.position < 0:
            buy_probability += 0.3  # Больше склонны покупать при короткой позиции
        else:
            # При нулевой позиции добавляем случайность
            if random.random() < 0.4:
                sell_probability += 0.2  # Иногда продаем даже без позиции (короткие продажи)
        
        # Влияние волатильности
        if price_volatility > 0.02:  # Высокая волатильность
            if self.risk_tolerance < 0.5:
                # Консервативные агенты меньше торгуют при высокой волатильности
                return None
            else:
                # Агрессивные агенты больше торгуют при высокой волатильности
                buy_probability *= 1.3
                sell_probability *= 1.3
        
        # Влияние баланса
        if self.balance < current_price * 10:  # Мало денег
            buy_probability *= 0.3
            sell_probability *= 1.5  # Больше склонны продавать при нехватке денег
        if self.position < -100:  # Большая короткая позиция
            sell_probability *= 0.3
        
        # Добавляем базовую вероятность продажи для всех агентов
        sell_probability += 0.15
        
        # Нормализуем вероятности
        total = buy_probability + sell_probability
        if total == 0:
            return None
        
        buy_probability /= total
        sell_probability /= total
        
        rand = random.random()
        if rand < buy_probability:
            return OrderType.BUY
        elif rand < buy_probability + sell_probability:
            return OrderType.SELL
        else:
            return None
    
    def _generate_price(self, current_price: float, price_volatility: float, order_type: OrderType) -> float:
        """Генерирует цену для ордера"""
        # Базовое отклонение от текущей цены
        base_deviation = current_price * price_volatility * self.price_sensitivity
        
        # Случайное отклонение
        deviation = random.gauss(0, base_deviation)
        
        # Направление отклонения в зависимости от типа ордера
        if order_type == OrderType.BUY:
            # Ордера на покупку обычно ниже текущей цены
            deviation = abs(deviation) * -0.5
        else:  # SELL
            # Ордера на продажу обычно выше текущей цены, но не слишком высоко
            deviation = abs(deviation) * random.uniform(0.3, 0.8)  # Более агрессивные цены продажи
        
        price = current_price + deviation
        
        # Ограничиваем цену разумными пределами
        min_price = current_price * 0.5
        max_price = current_price * 2.0
        price = max(min_price, min(max_price, price))
        
        return round(price, 2)
    
    def _generate_quantity(self, current_price: float) -> int:
        """Генерирует количество для ордера"""
        # Базовое количество зависит от баланса и риска
        base_quantity = int((self.balance * self.risk_tolerance) / current_price)
        
        # Добавляем случайность
        quantity = int(base_quantity * random.uniform(0.1, 1.0))
        
        # Ограничиваем разумными пределами
        quantity = max(1, min(quantity, 1000))
        
        return quantity
    
    def update_after_trade(self, trade_price: float, trade_quantity: int, is_buyer: bool):
        """Обновляет состояние агента после сделки"""
        if is_buyer:
            self.balance -= trade_price * trade_quantity
            self.position += trade_quantity
        else:
            self.balance += trade_price * trade_quantity
            self.position -= trade_quantity
    
    def get_portfolio_value(self, current_price: float) -> float:
        """Возвращает общую стоимость портфеля"""
        return self.balance + self.position * current_price
