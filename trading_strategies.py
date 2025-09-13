import random
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from order_book import Order, OrderType

class StrategyType(Enum):
    MOMENTUM = "MOMENTUM"           # Следование тренду
    MEAN_REVERSION = "MEAN_REVERSION"  # Возврат к среднему
    ARBITRAGE = "ARBITRAGE"         # Арбитраж
    MARKET_MAKER = "MARKET_MAKER"   # Маркет-мейкер
    SCALPER = "SCALPER"            # Скальпер
    SWING_TRADER = "SWING_TRADER"   # Свинг-трейдер
    VALUE_INVESTOR = "VALUE_INVESTOR"  # Инвестор по стоимости
    NOISE_TRADER = "NOISE_TRADER"   # Шумовой трейдер

@dataclass
class MarketData:
    current_price: float
    price_history: List[float]
    volume_history: List[int]
    volatility: float
    spread: Optional[float]
    best_bid: Optional[float]
    best_ask: Optional[float]

class TradingStrategy:
    """Базовый класс для торговых стратегий"""
    
    def __init__(self, strategy_type: StrategyType, agent_id: int):
        self.strategy_type = strategy_type
        self.agent_id = agent_id
        self.last_action_time = 0
        self.position_history = []
        self.price_history = []
        
    def should_trade(self, market_data: MarketData, agent_balance: float, agent_position: int) -> bool:
        """Определяет, должен ли агент торговать"""
        return True
    
    def generate_order(self, market_data: MarketData, agent_balance: float, agent_position: int) -> Optional[Order]:
        """Генерирует ордер на основе стратегии"""
        raise NotImplementedError

class MomentumStrategy(TradingStrategy):
    """Стратегия следования тренду"""
    
    def __init__(self, agent_id: int):
        super().__init__(StrategyType.MOMENTUM, agent_id)
        self.lookback_period = 10
        self.momentum_threshold = 0.02
        
    def should_trade(self, market_data: MarketData, agent_balance: float, agent_position: int) -> bool:
        if len(market_data.price_history) < self.lookback_period:
            return False
        
        # Проверяем тренд
        recent_prices = market_data.price_history[-self.lookback_period:]
        price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        return abs(price_change) > self.momentum_threshold
    
    def generate_order(self, market_data: MarketData, agent_balance: float, agent_position: int) -> Optional[Order]:
        if len(market_data.price_history) < self.lookback_period:
            return None
        
        recent_prices = market_data.price_history[-self.lookback_period:]
        price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        # Определяем направление тренда
        if price_change > self.momentum_threshold:
            # Восходящий тренд - покупаем
            order_type = OrderType.BUY
            price = market_data.current_price * 1.01  # Немного выше текущей цены
        elif price_change < -self.momentum_threshold:
            # Нисходящий тренд - продаем
            order_type = OrderType.SELL
            price = market_data.current_price * 0.99  # Немного ниже текущей цены
        else:
            return None
        
        # Размер позиции зависит от силы тренда
        base_quantity = int(agent_balance * 0.1 / market_data.current_price)
        quantity = int(base_quantity * min(abs(price_change) * 10, 2))
        
        if order_type == OrderType.BUY and agent_balance < price * quantity:
            quantity = int(agent_balance / price)
        elif order_type == OrderType.SELL and agent_position < quantity:
            quantity = max(0, agent_position)
        
        if quantity <= 0:
            return None
        
        return Order(
            id=0,
            price=price,
            quantity=quantity,
            order_type=order_type,
            agent_id=self.agent_id,
            timestamp=time.time()
        )

class MeanReversionStrategy(TradingStrategy):
    """Стратегия возврата к среднему"""
    
    def __init__(self, agent_id: int):
        super().__init__(StrategyType.MEAN_REVERSION, agent_id)
        self.lookback_period = 20
        self.deviation_threshold = 0.05
        
    def should_trade(self, market_data: MarketData, agent_balance: float, agent_position: int) -> bool:
        if len(market_data.price_history) < self.lookback_period:
            return False
        
        # Вычисляем среднюю цену
        recent_prices = market_data.price_history[-self.lookback_period:]
        mean_price = sum(recent_prices) / len(recent_prices)
        current_deviation = abs(market_data.current_price - mean_price) / mean_price
        
        return current_deviation > self.deviation_threshold
    
    def generate_order(self, market_data: MarketData, agent_balance: float, agent_position: int) -> Optional[Order]:
        if len(market_data.price_history) < self.lookback_period:
            return None
        
        recent_prices = market_data.price_history[-self.lookback_period:]
        mean_price = sum(recent_prices) / len(recent_prices)
        
        # Если цена выше среднего - продаем, если ниже - покупаем
        if market_data.current_price > mean_price * 1.02:
            order_type = OrderType.SELL
            price = market_data.current_price * 0.99
        elif market_data.current_price < mean_price * 0.98:
            order_type = OrderType.BUY
            price = market_data.current_price * 1.01
        else:
            return None
        
        quantity = int(agent_balance * 0.15 / market_data.current_price)
        
        if order_type == OrderType.BUY and agent_balance < price * quantity:
            quantity = int(agent_balance / price)
        elif order_type == OrderType.SELL and agent_position < quantity:
            quantity = max(0, agent_position)
        
        if quantity <= 0:
            return None
        
        return Order(
            id=0,
            price=price,
            quantity=quantity,
            order_type=order_type,
            agent_id=self.agent_id,
            timestamp=time.time()
        )

class MarketMakerStrategy(TradingStrategy):
    """Стратегия маркет-мейкера"""
    
    def __init__(self, agent_id: int):
        super().__init__(StrategyType.MARKET_MAKER, agent_id)
        self.spread_target = 0.02  # 2% спред
        self.max_position = 100
        
    def should_trade(self, market_data: MarketData, agent_balance: float, agent_position: int) -> bool:
        # Маркет-мейкеры торгуют постоянно
        return True
    
    def generate_order(self, market_data: MarketData, agent_balance: float, agent_position: int) -> Optional[Order]:
        # Размещаем ордера с обеих сторон
        if random.random() < 0.5:
            # Ордер на покупку
            if agent_position < self.max_position and agent_balance > market_data.current_price * 10:
                price = market_data.current_price * (1 - self.spread_target / 2)
                quantity = min(10, int(agent_balance * 0.05 / price))
                
                if quantity > 0:
                    return Order(
                        id=0,
                        price=price,
                        quantity=quantity,
                        order_type=OrderType.BUY,
                        agent_id=self.agent_id,
                        timestamp=time.time()
                    )
        else:
            # Ордер на продажу
            if agent_position > -self.max_position:
                price = market_data.current_price * (1 + self.spread_target / 2)
                quantity = min(10, abs(agent_position) if agent_position < 0 else 10)
                
                if quantity > 0:
                    return Order(
                        id=0,
                        price=price,
                        quantity=quantity,
                        order_type=OrderType.SELL,
                        agent_id=self.agent_id,
                        timestamp=time.time()
                    )
        
        return None

class ScalperStrategy(TradingStrategy):
    """Стратегия скальпера"""
    
    def __init__(self, agent_id: int):
        super().__init__(StrategyType.SCALPER, agent_id)
        self.profit_target = 0.005  # 0.5% прибыль
        self.stop_loss = 0.01  # 1% стоп-лосс
        
    def should_trade(self, market_data: MarketData, agent_balance: float, agent_position: int) -> bool:
        # Скальперы торгуют часто
        return random.random() < 0.8
    
    def generate_order(self, market_data: MarketData, agent_balance: float, agent_position: int) -> Optional[Order]:
        if market_data.spread and market_data.spread < market_data.current_price * 0.01:
            # Если спред маленький, пытаемся заработать на нем
            if agent_position == 0:
                # Покупаем по лучшей цене
                price = market_data.current_price * 1.001
                quantity = min(5, int(agent_balance * 0.1 / price))
                
                if quantity > 0 and agent_balance >= price * quantity:
                    return Order(
                        id=0,
                        price=price,
                        quantity=quantity,
                        order_type=OrderType.BUY,
                        agent_id=self.agent_id,
                        timestamp=time.time()
                    )
            elif agent_position > 0:
                # Продаем с прибылью
                price = market_data.current_price * (1 + self.profit_target)
                quantity = min(5, agent_position)
                
                if quantity > 0:
                    return Order(
                        id=0,
                        price=price,
                        quantity=quantity,
                        order_type=OrderType.SELL,
                        agent_id=self.agent_id,
                        timestamp=time.time()
                    )
        
        return None

class ValueInvestorStrategy(TradingStrategy):
    """Стратегия инвестора по стоимости"""
    
    def __init__(self, agent_id: int):
        super().__init__(StrategyType.VALUE_INVESTOR, agent_id)
        self.fair_value = 100.0  # Справедливая стоимость
        self.value_threshold = 0.1  # 10% отклонение
        
    def should_trade(self, market_data: MarketData, agent_balance: float, agent_position: int) -> bool:
        # Инвесторы торгуют редко
        return random.random() < 0.1
    
    def generate_order(self, market_data: MarketData, agent_balance: float, agent_position: int) -> Optional[Order]:
        price_deviation = (market_data.current_price - self.fair_value) / self.fair_value
        
        if price_deviation < -self.value_threshold:
            # Цена ниже справедливой - покупаем
            order_type = OrderType.BUY
            price = market_data.current_price * 1.005
            quantity = int(agent_balance * 0.2 / price)
        elif price_deviation > self.value_threshold:
            # Цена выше справедливой - продаем
            order_type = OrderType.SELL
            price = market_data.current_price * 0.995
            quantity = min(int(agent_position * 0.5), agent_position)
        else:
            return None
        
        if order_type == OrderType.BUY and agent_balance < price * quantity:
            quantity = int(agent_balance / price)
        elif order_type == OrderType.SELL and agent_position < quantity:
            quantity = max(0, agent_position)
        
        if quantity <= 0:
            return None
        
        return Order(
            id=0,
            price=price,
            quantity=quantity,
            order_type=order_type,
            agent_id=self.agent_id,
            timestamp=time.time()
        )

class NoiseTraderStrategy(TradingStrategy):
    """Стратегия шумового трейдера"""
    
    def __init__(self, agent_id: int):
        super().__init__(StrategyType.NOISE_TRADER, agent_id)
        
    def should_trade(self, market_data: MarketData, agent_balance: float, agent_position: int) -> bool:
        # Шумовые трейдеры торгуют случайно
        return random.random() < 0.3
    
    def generate_order(self, market_data: MarketData, agent_balance: float, agent_position: int) -> Optional[Order]:
        # Случайный выбор направления
        order_type = OrderType.BUY if random.random() < 0.5 else OrderType.SELL
        
        # Случайная цена
        price_variation = random.uniform(0.95, 1.05)
        price = market_data.current_price * price_variation
        
        # Случайное количество
        quantity = random.randint(1, 20)
        
        if order_type == OrderType.BUY and agent_balance < price * quantity:
            quantity = int(agent_balance / price)
        elif order_type == OrderType.SELL and agent_position < quantity:
            quantity = max(0, agent_position)
        
        if quantity <= 0:
            return None
        
        return Order(
            id=0,
            price=price,
            quantity=quantity,
            order_type=order_type,
            agent_id=self.agent_id,
            timestamp=time.time()
        )

def create_strategy(agent_id: int, strategy_type: StrategyType) -> TradingStrategy:
    """Создает стратегию для агента"""
    if strategy_type == StrategyType.MOMENTUM:
        return MomentumStrategy(agent_id)
    elif strategy_type == StrategyType.MEAN_REVERSION:
        return MeanReversionStrategy(agent_id)
    elif strategy_type == StrategyType.MARKET_MAKER:
        return MarketMakerStrategy(agent_id)
    elif strategy_type == StrategyType.SCALPER:
        return ScalperStrategy(agent_id)
    elif strategy_type == StrategyType.VALUE_INVESTOR:
        return ValueInvestorStrategy(agent_id)
    elif strategy_type == StrategyType.NOISE_TRADER:
        return NoiseTraderStrategy(agent_id)
    else:
        return NoiseTraderStrategy(agent_id)  # По умолчанию

def get_strategy_distribution(num_agents: int) -> List[StrategyType]:
    """Возвращает распределение стратегий для агентов"""
    strategies = []
    
    for i in range(num_agents):
        if i % 10 == 0:
            strategies.append(StrategyType.MOMENTUM)
        elif i % 10 == 1:
            strategies.append(StrategyType.MEAN_REVERSION)
        elif i % 10 == 2:
            strategies.append(StrategyType.MARKET_MAKER)
        elif i % 10 == 3:
            strategies.append(StrategyType.SCALPER)
        elif i % 10 == 4:
            strategies.append(StrategyType.VALUE_INVESTOR)
        else:
            strategies.append(StrategyType.NOISE_TRADER)
    
    return strategies

