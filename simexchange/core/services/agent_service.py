"""
Сервис для управления агентами
"""

import random
from typing import List, Optional, Dict, Any, Tuple
from ..models import Agent, Order, OrderType, MarketData, SimulationConfig


class AgentService:
    """Сервис для управления агентами"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.agents: List[Agent] = []
        self.initial_balance = config.initial_balance
    
    def create_agents(self, num_agents: int) -> List[Agent]:
        """Создает агентов с различными характеристиками"""
        self.agents.clear()
        
        for i in range(num_agents):
            agent = self._create_agent(i)
            self.agents.append(agent)
        
        return self.agents.copy()
    
    def _create_agent(self, agent_id: int) -> Agent:
        """Создает одного агента с случайными характеристиками"""
        return Agent(
            id=agent_id,
            balance=self.initial_balance,
            position=0,
            risk_tolerance=self.config.get_agent_risk_tolerance(),
            trading_frequency=self.config.get_agent_trading_frequency(),
            price_sensitivity=self.config.get_agent_price_sensitivity(),
            trade_cooldown=self.config.get_agent_trade_cooldown()
        )
    
    def get_agents(self) -> List[Agent]:
        """Возвращает список всех агентов"""
        return self.agents.copy()
    
    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Возвращает агента по ID"""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def get_agent_count(self) -> int:
        """Возвращает количество агентов"""
        return len(self.agents)
    
    def update_agent_after_trade(self, agent_id: int, trade_price: float, 
                                trade_quantity: int, is_buyer: bool):
        """Обновляет состояние агента после сделки"""
        agent = self.get_agent(agent_id)
        if agent:
            agent.update_after_trade(trade_price, trade_quantity, is_buyer)
    
    def add_agent_order_statistics(self, agent_id: int, order_type: OrderType):
        """Добавляет статистику по ордеру агента"""
        agent = self.get_agent(agent_id)
        if agent:
            agent.add_order_statistics(order_type)
    
    def increase_all_balances(self, amount: float):
        """Увеличивает баланс всех агентов"""
        for agent in self.agents:
            agent.balance += amount
    
    def get_agent_statistics(self, current_price: float) -> List[Dict[str, Any]]:
        """Возвращает статистику всех агентов"""
        agent_stats = []
        
        for agent in self.agents:
            portfolio_value = agent.get_portfolio_value(current_price)
            profit = agent.get_profit(self.initial_balance, current_price)
            profit_percent = agent.get_profit_percentage(self.initial_balance, current_price)
            
            agent_stats.append({
                'id': agent.id,
                'balance': agent.balance,
                'position': agent.position,
                'portfolio_value': portfolio_value,
                'profit': profit,
                'profit_percent': profit_percent,
                'risk_tolerance': agent.risk_tolerance,
                'trading_frequency': agent.trading_frequency,
                'price_sensitivity': agent.price_sensitivity,
                'buy_orders': agent.buy_orders_count,
                'sell_orders': agent.sell_orders_count,
                'total_orders': agent.total_orders_count,
                'total_volume': agent.total_volume_traded,
                'total_value': agent.total_value_traded,
                'last_trade_time': agent.last_trade_time
            })
        
        # Сортируем по прибыли (убыванию)
        agent_stats.sort(key=lambda x: x['profit'], reverse=True)
        
        return agent_stats
    
    def get_top_agents(self, current_price: float, count: int = 10) -> List[Dict[str, Any]]:
        """Возвращает топ агентов по прибыли"""
        all_stats = self.get_agent_statistics(current_price)
        return all_stats[:count]
    
    def get_worst_agents(self, current_price: float, count: int = 10) -> List[Dict[str, Any]]:
        """Возвращает худших агентов по прибыли"""
        all_stats = self.get_agent_statistics(current_price)
        return all_stats[-count:]
    
    def get_agent_performance_summary(self, current_price: float) -> Dict[str, Any]:
        """Возвращает сводку по производительности агентов"""
        if not self.agents:
            return {
                'total_agents': 0,
                'profitable_agents': 0,
                'losing_agents': 0,
                'break_even_agents': 0,
                'total_profit': 0.0,
                'average_profit': 0.0,
                'best_profit': 0.0,
                'worst_profit': 0.0,
                'total_volume': 0,
                'total_orders': 0
            }
        
        agent_stats = self.get_agent_statistics(current_price)
        
        profitable = sum(1 for agent in agent_stats if agent['profit'] > 0)
        losing = sum(1 for agent in agent_stats if agent['profit'] < 0)
        break_even = sum(1 for agent in agent_stats if agent['profit'] == 0)
        
        total_profit = sum(agent['profit'] for agent in agent_stats)
        average_profit = total_profit / len(agent_stats) if agent_stats else 0.0
        
        best_profit = max(agent['profit'] for agent in agent_stats) if agent_stats else 0.0
        worst_profit = min(agent['profit'] for agent in agent_stats) if agent_stats else 0.0
        
        total_volume = sum(agent['total_volume'] for agent in agent_stats)
        total_orders = sum(agent['total_orders'] for agent in agent_stats)
        
        return {
            'total_agents': len(agent_stats),
            'profitable_agents': profitable,
            'losing_agents': losing,
            'break_even_agents': break_even,
            'profitable_percentage': (profitable / len(agent_stats)) * 100,
            'losing_percentage': (losing / len(agent_stats)) * 100,
            'total_profit': total_profit,
            'average_profit': average_profit,
            'best_profit': best_profit,
            'worst_profit': worst_profit,
            'total_volume': total_volume,
            'total_orders': total_orders,
            'average_volume_per_agent': total_volume / len(agent_stats) if agent_stats else 0,
            'average_orders_per_agent': total_orders / len(agent_stats) if agent_stats else 0
        }
    
    def get_agents_by_strategy_performance(self, current_price: float) -> Dict[str, Dict[str, Any]]:
        """Возвращает производительность агентов по стратегиям"""
        # Пока что все агенты имеют одинаковую стратегию (noise trader)
        # В будущем здесь будет группировка по реальным стратегиям
        agent_stats = self.get_agent_statistics(current_price)
        
        strategy_performance = {}
        
        for agent in agent_stats:
            strategy = "noise_trader"  # Пока что все агенты используют эту стратегию
            
            if strategy not in strategy_performance:
                strategy_performance[strategy] = {
                    'count': 0,
                    'total_profit': 0.0,
                    'average_profit': 0.0,
                    'best_profit': float('-inf'),
                    'worst_profit': float('inf'),
                    'total_volume': 0,
                    'total_orders': 0
                }
            
            perf = strategy_performance[strategy]
            perf['count'] += 1
            perf['total_profit'] += agent['profit']
            perf['best_profit'] = max(perf['best_profit'], agent['profit'])
            perf['worst_profit'] = min(perf['worst_profit'], agent['profit'])
            perf['total_volume'] += agent['total_volume']
            perf['total_orders'] += agent['total_orders']
        
        # Вычисляем средние значения
        for strategy, perf in strategy_performance.items():
            if perf['count'] > 0:
                perf['average_profit'] = perf['total_profit'] / perf['count']
                perf['average_volume'] = perf['total_volume'] / perf['count']
                perf['average_orders'] = perf['total_orders'] / perf['count']
        
        return strategy_performance
    
    def reset_agent_statistics(self):
        """Сбрасывает статистику всех агентов"""
        for agent in self.agents:
            agent.reset_statistics()
    
    def reset_agent_balances(self):
        """Сбрасывает балансы всех агентов к начальному значению"""
        for agent in self.agents:
            agent.balance = self.initial_balance
            agent.position = 0
    
    def reset_all_agents(self):
        """Полностью сбрасывает всех агентов"""
        self.agents.clear()
        self.create_agents(self.config.num_agents)
    
    def get_agent_risk_distribution(self) -> Dict[str, int]:
        """Возвращает распределение агентов по уровням риска"""
        risk_distribution = {
            'low': 0,      # 0.0 - 0.3
            'medium': 0,   # 0.3 - 0.7
            'high': 0      # 0.7 - 1.0
        }
        
        for agent in self.agents:
            if agent.risk_tolerance < 0.3:
                risk_distribution['low'] += 1
            elif agent.risk_tolerance < 0.7:
                risk_distribution['medium'] += 1
            else:
                risk_distribution['high'] += 1
        
        return risk_distribution
    
    def get_agent_trading_frequency_distribution(self) -> Dict[str, int]:
        """Возвращает распределение агентов по частоте торговли"""
        freq_distribution = {
            'low': 0,      # 0.0 - 0.2
            'medium': 0,   # 0.2 - 0.5
            'high': 0      # 0.5 - 1.0
        }
        
        for agent in self.agents:
            if agent.trading_frequency < 0.2:
                freq_distribution['low'] += 1
            elif agent.trading_frequency < 0.5:
                freq_distribution['medium'] += 1
            else:
                freq_distribution['high'] += 1
        
        return freq_distribution
    
    def __str__(self) -> str:
        """Строковое представление сервиса"""
        return f"AgentService(agents={len(self.agents)})"
    
    def __repr__(self) -> str:
        """Детальное строковое представление"""
        return (f"AgentService(config={self.config}, "
                f"agents_count={len(self.agents)}, "
                f"initial_balance={self.initial_balance})")
