"""
Менеджер конфигурации
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
from ..core.models import SimulationConfig


class ConfigManager:
    """Менеджер конфигурации приложения"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self._config_data: Optional[Dict[str, Any]] = None
        self._simulation_config: Optional[SimulationConfig] = None
    
    def _get_default_config_path(self) -> str:
        """Возвращает путь к файлу конфигурации по умолчанию"""
        current_dir = Path(__file__).parent
        return str(current_dir / "default_config.yaml")
    
    def load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию из файла"""
        if self._config_data is not None:
            return self._config_data
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config_data = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Файл конфигурации {self.config_file} не найден, используем значения по умолчанию")
            self._config_data = self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            self._config_data = self._get_default_config()
        
        return self._config_data
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию по умолчанию"""
        return {
            'simulation': {
                'initial_price': 100.0,
                'num_agents': 20,
                'initial_balance': 10000.0
            },
            'performance': {
                'max_history_size': 1000,
                'max_trades_history': 5000,
                'performance_mode': False,
                'skip_volatility_calculation': False
            },
            'balance_increase': {
                'cycles': 100,
                'amount': 1000.0
            },
            'spread': {
                'avg_cycles': 50
            },
            'agents': {
                'risk_tolerance_range': [0.3, 0.8],
                'trading_frequency_range': [0.1, 0.4],
                'price_sensitivity_range': [0.5, 1.0],
                'trade_cooldown_range': [0.5, 2.0]
            },
            'strategies': {
                'momentum': 0.1,
                'mean_reversion': 0.1,
                'market_maker': 0.1,
                'scalper': 0.1,
                'value_investor': 0.1,
                'noise_trader': 0.5
            }
        }
    
    def get_simulation_config(self) -> SimulationConfig:
        """Возвращает конфигурацию симуляции"""
        if self._simulation_config is not None:
            return self._simulation_config
        
        config_data = self.load_config()
        
        # Извлекаем параметры симуляции
        sim_data = config_data.get('simulation', {})
        perf_data = config_data.get('performance', {})
        balance_data = config_data.get('balance_increase', {})
        spread_data = config_data.get('spread', {})
        agents_data = config_data.get('agents', {})
        strategies_data = config_data.get('strategies', {})
        
        self._simulation_config = SimulationConfig(
            initial_price=sim_data.get('initial_price', 100.0),
            num_agents=sim_data.get('num_agents', 20),
            initial_balance=sim_data.get('initial_balance', 10000.0),
            max_history_size=perf_data.get('max_history_size', 1000),
            max_trades_history=perf_data.get('max_trades_history', 5000),
            performance_mode=perf_data.get('performance_mode', False),
            skip_volatility_calculation=perf_data.get('skip_volatility_calculation', False),
            balance_increase_cycles=balance_data.get('cycles', 100),
            balance_increase_amount=balance_data.get('amount', 1000.0),
            avg_spread_cycles=spread_data.get('avg_cycles', 50),
            agent_risk_tolerance_range=tuple(agents_data.get('risk_tolerance_range', [0.3, 0.8])),
            agent_trading_frequency_range=tuple(agents_data.get('trading_frequency_range', [0.1, 0.4])),
            agent_price_sensitivity_range=tuple(agents_data.get('price_sensitivity_range', [0.5, 1.0])),
            agent_trade_cooldown_range=tuple(agents_data.get('trade_cooldown_range', [0.5, 2.0])),
            strategy_distribution=strategies_data
        )
        
        return self._simulation_config
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию UI"""
        config_data = self.load_config()
        return config_data.get('ui', {})
    
    def get_colors_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию цветов"""
        config_data = self.load_config()
        return config_data.get('colors', {})
    
    def save_config(self, config_data: Dict[str, Any]):
        """Сохраняет конфигурацию в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            self._config_data = config_data
            self._simulation_config = None  # Сбрасываем кэш
        except Exception as e:
            print(f"Ошибка при сохранении конфигурации: {e}")
    
    def update_simulation_config(self, **kwargs):
        """Обновляет конфигурацию симуляции"""
        config_data = self.load_config()
        
        # Обновляем параметры симуляции
        if 'initial_price' in kwargs:
            config_data.setdefault('simulation', {})['initial_price'] = kwargs['initial_price']
        if 'num_agents' in kwargs:
            config_data.setdefault('simulation', {})['num_agents'] = kwargs['num_agents']
        if 'initial_balance' in kwargs:
            config_data.setdefault('simulation', {})['initial_balance'] = kwargs['initial_balance']
        
        # Обновляем параметры производительности
        if 'max_history_size' in kwargs:
            config_data.setdefault('performance', {})['max_history_size'] = kwargs['max_history_size']
        if 'performance_mode' in kwargs:
            config_data.setdefault('performance', {})['performance_mode'] = kwargs['performance_mode']
        
        # Обновляем параметры увеличения баланса
        if 'balance_increase_cycles' in kwargs:
            config_data.setdefault('balance_increase', {})['cycles'] = kwargs['balance_increase_cycles']
        if 'balance_increase_amount' in kwargs:
            config_data.setdefault('balance_increase', {})['amount'] = kwargs['balance_increase_amount']
        
        # Сохраняем обновленную конфигурацию
        self.save_config(config_data)
        self._simulation_config = None  # Сбрасываем кэш
    
    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """Получает значение конфигурации по пути (например, 'simulation.initial_price')"""
        config_data = self.load_config()
        
        keys = key_path.split('.')
        value = config_data
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_config_value(self, key_path: str, value: Any):
        """Устанавливает значение конфигурации по пути"""
        config_data = self.load_config()
        
        keys = key_path.split('.')
        current = config_data
        
        # Создаем вложенные словари если нужно
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Устанавливаем значение
        current[keys[-1]] = value
        
        # Сохраняем конфигурацию
        self.save_config(config_data)
        self._simulation_config = None  # Сбрасываем кэш
    
    def __str__(self) -> str:
        """Строковое представление менеджера конфигурации"""
        return f"ConfigManager(config_file={self.config_file})"
    
    def __repr__(self) -> str:
        """Детальное строковое представление"""
        return (f"ConfigManager(config_file={self.config_file}, "
                f"config_loaded={self._config_data is not None})")


# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()
