"""
Конфигурация симуляции
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class SimulationConfig:
    """Конфигурация симуляции"""
    # Основные параметры
    initial_price: float = 100.0
    num_agents: int = 20
    initial_balance: float = 10000.0
    
    # Настройки производительности
    max_history_size: int = 1000
    max_trades_history: int = 5000
    performance_mode: bool = False
    skip_volatility_calculation: bool = False
    
    # Настройки увеличения баланса
    balance_increase_cycles: int = 100
    balance_increase_amount: float = 1000.0
    
    # Настройки спреда
    avg_spread_cycles: int = 50
    
    # Настройки агентов
    agent_risk_tolerance_range: tuple = (0.3, 0.8)
    agent_trading_frequency_range: tuple = (0.1, 0.4)
    agent_price_sensitivity_range: tuple = (0.5, 1.0)
    agent_trade_cooldown_range: tuple = (0.5, 2.0)
    
    # Настройки стратегий
    strategy_distribution: Dict[str, float] = field(default_factory=lambda: {
        'momentum': 0.1,
        'mean_reversion': 0.1,
        'market_maker': 0.1,
        'scalper': 0.1,
        'value_investor': 0.1,
        'noise_trader': 0.5
    })
    
    def __post_init__(self):
        """Валидация конфигурации"""
        if self.initial_price <= 0:
            raise ValueError("Начальная цена должна быть положительной")
        if self.num_agents <= 0:
            raise ValueError("Количество агентов должно быть положительным")
        if self.initial_balance <= 0:
            raise ValueError("Начальный баланс должен быть положительным")
        if self.max_history_size <= 0:
            raise ValueError("Максимальный размер истории должен быть положительным")
        if self.max_trades_history <= 0:
            raise ValueError("Максимальный размер истории сделок должен быть положительным")
        if self.balance_increase_cycles <= 0:
            raise ValueError("Циклы увеличения баланса должны быть положительными")
        if self.balance_increase_amount < 0:
            raise ValueError("Сумма увеличения баланса не может быть отрицательной")
        if self.avg_spread_cycles <= 0:
            raise ValueError("Циклы для расчета спреда должны быть положительными")
        
        # Валидация диапазонов
        if not (0 <= self.agent_risk_tolerance_range[0] <= self.agent_risk_tolerance_range[1] <= 1):
            raise ValueError("Диапазон толерантности к риску должен быть от 0 до 1")
        if not (0 <= self.agent_trading_frequency_range[0] <= self.agent_trading_frequency_range[1] <= 1):
            raise ValueError("Диапазон частоты торговли должен быть от 0 до 1")
        if not (0 <= self.agent_price_sensitivity_range[0] <= self.agent_price_sensitivity_range[1] <= 1):
            raise ValueError("Диапазон чувствительности к цене должен быть от 0 до 1")
        if self.agent_trade_cooldown_range[0] < 0 or self.agent_trade_cooldown_range[1] < 0:
            raise ValueError("Диапазон кулдауна торговли не может быть отрицательным")
        
        # Валидация распределения стратегий
        total_probability = sum(self.strategy_distribution.values())
        if abs(total_probability - 1.0) > 0.001:
            raise ValueError(f"Сумма вероятностей стратегий должна быть равна 1.0, получено {total_probability}")
        
        for strategy, prob in self.strategy_distribution.items():
            if prob < 0 or prob > 1:
                raise ValueError(f"Вероятность стратегии '{strategy}' должна быть от 0 до 1")
    
    def get_agent_risk_tolerance(self) -> float:
        """Возвращает случайную толерантность к риску в заданном диапазоне"""
        import random
        return random.uniform(*self.agent_risk_tolerance_range)
    
    def get_agent_trading_frequency(self) -> float:
        """Возвращает случайную частоту торговли в заданном диапазоне"""
        import random
        return random.uniform(*self.agent_trading_frequency_range)
    
    def get_agent_price_sensitivity(self) -> float:
        """Возвращает случайную чувствительность к цене в заданном диапазоне"""
        import random
        return random.uniform(*self.agent_price_sensitivity_range)
    
    def get_agent_trade_cooldown(self) -> float:
        """Возвращает случайный кулдаун торговли в заданном диапазоне"""
        import random
        return random.uniform(*self.agent_trade_cooldown_range)
    
    def get_strategy_type(self) -> str:
        """Возвращает случайный тип стратегии согласно распределению"""
        import random
        strategies = list(self.strategy_distribution.keys())
        probabilities = list(self.strategy_distribution.values())
        return random.choices(strategies, weights=probabilities)[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует конфигурацию в словарь"""
        return {
            'initial_price': self.initial_price,
            'num_agents': self.num_agents,
            'initial_balance': self.initial_balance,
            'max_history_size': self.max_history_size,
            'max_trades_history': self.max_trades_history,
            'performance_mode': self.performance_mode,
            'skip_volatility_calculation': self.skip_volatility_calculation,
            'balance_increase_cycles': self.balance_increase_cycles,
            'balance_increase_amount': self.balance_increase_amount,
            'avg_spread_cycles': self.avg_spread_cycles,
            'agent_risk_tolerance_range': self.agent_risk_tolerance_range,
            'agent_trading_frequency_range': self.agent_trading_frequency_range,
            'agent_price_sensitivity_range': self.agent_price_sensitivity_range,
            'agent_trade_cooldown_range': self.agent_trade_cooldown_range,
            'strategy_distribution': self.strategy_distribution
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimulationConfig':
        """Создает конфигурацию из словаря"""
        return cls(**data)
    
    def __str__(self) -> str:
        """Строковое представление конфигурации"""
        return (f"SimulationConfig(price={self.initial_price}, "
                f"agents={self.num_agents}, balance={self.initial_balance})")
    
    def __repr__(self) -> str:
        """Детальное строковое представление"""
        return (f"SimulationConfig(initial_price={self.initial_price}, "
                f"num_agents={self.num_agents}, initial_balance={self.initial_balance}, "
                f"performance_mode={self.performance_mode})")
