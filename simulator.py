import time
import random
from typing import List, Optional
from order_book import OrderBook, Order, Trade
from trading_agent import Agent
from trading_strategies import MarketData, get_strategy_distribution
from trading_bot import TradingBot

class TradingSimulator:
    def __init__(self, initial_price: float, num_agents: int, initial_balance: float):
        self.order_book = OrderBook(initial_price)
        self.agents: List[Agent] = []
        self.cycle = 0
        self.is_running = False
        
        # Создаем агентов с разными стратегиями
        strategy_distribution = get_strategy_distribution(num_agents)
        for i in range(num_agents):
            strategy_type = strategy_distribution[i]
            agent = Agent(i, initial_balance, strategy_type)
            self.agents.append(agent)
        
        # Создаем торгового бота
        self.trading_bot = TradingBot(bot_id=-1)
        
        # Статистика
        self.price_history = [initial_price]
        self.volume_history = [0]
        self.trade_count_history = [0]
        self.spread_history = []
        self.avg_spread_cycles = 50  # Количество циклов для расчета среднего спреда
        
        # Механизм увеличения баланса
        self.balance_increase_cycles = 100  # Каждые N циклов
        self.balance_increase_amount = 1000.0  # На M денег
        self.last_balance_increase_cycle = 0
        
    def run_cycle(self) -> List[Trade]:
        """Выполняет один цикл симуляции"""
        self.cycle += 1
        current_price = self.order_book.current_price
        
        # Вычисляем волатильность на основе истории цен
        price_volatility = self._calculate_volatility()
        
        # Создаем данные о рынке для агентов
        market_data = MarketData(
            current_price=current_price,
            price_history=self.price_history[-50:],  # Последние 50 цен
            volume_history=self.volume_history[-50:],  # Последние 50 объемов
            volatility=price_volatility,
            spread=self.order_book.get_spread(),
            best_bid=self.order_book.get_best_bid(),
            best_ask=self.order_book.get_best_ask()
        )
        
        # Агенты генерируют ордера
        new_trades = []
        for agent in self.agents:
            order = agent.generate_order(current_price, price_volatility, market_data)
            if order:
                order.id = self.order_book.next_order_id
                self.order_book.next_order_id += 1
                
                # Добавляем ордер в стакан
                trades = self.order_book.add_order(order)
                new_trades.extend(trades)
                
                # Обновляем состояние агентов после сделок
                for trade in trades:
                    if trade.buyer_id == agent.id:
                        agent.update_after_trade(trade.price, trade.quantity, True)
                    elif trade.seller_id == agent.id:
                        agent.update_after_trade(trade.price, trade.quantity, False)
        
        # Торговый бот генерирует ордера
        bot_order = self.trading_bot.generate_order(current_price, self.cycle, market_data)
        if bot_order:
            bot_order.id = self.order_book.next_order_id
            self.order_book.next_order_id += 1
            
            # Добавляем ордер бота в стакан
            bot_trades = self.order_book.add_order(bot_order)
            new_trades.extend(bot_trades)
            
            # Обновляем статистику бота после сделок
            for trade in bot_trades:
                if trade.buyer_id == self.trading_bot.bot_id:
                    self.trading_bot.total_volume += trade.quantity
                elif trade.seller_id == self.trading_bot.bot_id:
                    self.trading_bot.total_volume += trade.quantity
        
        # Проверяем, нужно ли увеличить баланс агентов
        self._check_balance_increase()
        
        # Обновляем статистику
        self._update_statistics(new_trades)
        
        return new_trades
    
    def _calculate_volatility(self) -> float:
        """Вычисляет волатильность на основе истории цен"""
        if len(self.price_history) < 2:
            return 0.01  # Базовая волатильность
        
        # Используем последние 10 цен для расчета волатильности
        recent_prices = self.price_history[-10:]
        returns = []
        
        for i in range(1, len(recent_prices)):
            return_rate = (recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
            returns.append(return_rate)
        
        if not returns:
            return 0.01
        
        # Вычисляем стандартное отклонение доходности
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = variance ** 0.5
        
        return max(0.005, min(0.05, volatility))  # Ограничиваем разумными пределами
    
    def get_average_spread(self) -> Optional[float]:
        """Возвращает средний спред за последние N циклов"""
        if not self.spread_history:
            return None
        
        # Берем последние N циклов или все доступные
        cycles_to_use = min(self.avg_spread_cycles, len(self.spread_history))
        recent_spreads = self.spread_history[-cycles_to_use:]
        
        return sum(recent_spreads) / len(recent_spreads)
    
    def set_avg_spread_cycles(self, cycles: int):
        """Устанавливает количество циклов для расчета среднего спреда"""
        self.avg_spread_cycles = max(1, min(cycles, 1000))  # Ограничиваем от 1 до 1000
    
    def _check_balance_increase(self):
        """Проверяет и выполняет увеличение баланса агентов"""
        if self.cycle - self.last_balance_increase_cycle >= self.balance_increase_cycles:
            # Увеличиваем баланс всех агентов
            for agent in self.agents:
                agent.balance += self.balance_increase_amount
            
            self.last_balance_increase_cycle = self.cycle
            print(f"Цикл {self.cycle}: Баланс всех агентов увеличен на {self.balance_increase_amount}")
    
    def set_balance_increase_settings(self, cycles: int, amount: float):
        """Устанавливает параметры увеличения баланса"""
        self.balance_increase_cycles = max(1, min(cycles, 10000))  # От 1 до 10000 циклов
        self.balance_increase_amount = max(0, amount)  # Неотрицательная сумма
        print(f"Настройки увеличения баланса: каждые {self.balance_increase_cycles} циклов на {self.balance_increase_amount}")
    
    def set_bot_config(self, **kwargs):
        """Устанавливает конфигурацию торгового бота"""
        self.trading_bot.update_config(**kwargs)
        print(f"Настройки бота обновлены: {kwargs}")
    
    def toggle_bot(self, enabled: bool = None):
        """Включает/выключает торгового бота"""
        if enabled is None:
            self.trading_bot.config.enabled = not self.trading_bot.config.enabled
        else:
            self.trading_bot.config.enabled = enabled
        
        status = "включен" if self.trading_bot.config.enabled else "выключен"
        print(f"Торговый бот {status}")
    
    def get_bot_statistics(self) -> dict:
        """Возвращает статистику торгового бота"""
        return self.trading_bot.get_statistics()
    
    def _update_statistics(self, new_trades: List[Trade]):
        """Обновляет статистику симуляции"""
        current_price = self.order_book.current_price
        self.price_history.append(current_price)
        
        # Объем торгов
        total_volume = sum(trade.quantity for trade in new_trades)
        self.volume_history.append(total_volume)
        
        # Количество сделок
        self.trade_count_history.append(len(new_trades))
        
        # Спред
        current_spread = self.order_book.get_spread()
        if current_spread is not None:
            self.spread_history.append(current_spread)
        
        # Ограничиваем размер истории
        max_history = 1000
        if len(self.price_history) > max_history:
            self.price_history = self.price_history[-max_history:]
            self.volume_history = self.volume_history[-max_history:]
            self.trade_count_history = self.trade_count_history[-max_history:]
            self.spread_history = self.spread_history[-max_history:]
    
    def get_simulation_data(self) -> dict:
        """Возвращает данные для отображения"""
        order_book_data = self.order_book.get_order_book_data()
        
        # Статистика агентов
        agent_stats = []
        initial_portfolio_value = 10000.0  # Начальная стоимость портфеля
        
        for agent in self.agents:
            portfolio_value = agent.get_portfolio_value(self.order_book.current_price)
            profit = portfolio_value - initial_portfolio_value
            profit_percent = (profit / initial_portfolio_value) * 100
            
            agent_stats.append({
                'id': agent.id,
                'strategy': agent.strategy.strategy_type.value,
                'balance': agent.balance,
                'position': agent.position,
                'portfolio_value': portfolio_value,
                'profit': profit,
                'profit_percent': profit_percent,
                'risk_tolerance': agent.risk_tolerance,
                'buy_orders': agent.buy_orders_count,
                'sell_orders': agent.sell_orders_count,
                'total_orders': agent.total_orders_count
            })
        
        # Сортируем по убыванию профита
        agent_stats.sort(key=lambda x: x['profit'], reverse=True)
        
        return {
            'cycle': self.cycle,
            'order_book': order_book_data,
            'agents': agent_stats,
            'price_history': self.price_history[-50:],  # Последние 50 точек
            'volume_history': self.volume_history[-50:],
            'trade_count_history': self.trade_count_history[-50:],
            'total_trades': len(self.order_book.trades),
            'total_volume': sum(self.volume_history),
            'average_spread': self.get_average_spread(),
            'avg_spread_cycles': self.avg_spread_cycles,
            'balance_increase_cycles': self.balance_increase_cycles,
            'balance_increase_amount': self.balance_increase_amount,
            'next_balance_increase': self.balance_increase_cycles - (self.cycle - self.last_balance_increase_cycle),
            'bot_statistics': self.get_bot_statistics()
        }
    
    def get_price_chart_data(self) -> dict:
        """Возвращает данные для построения графика цены"""
        return {
            'prices': self.price_history,
            'volumes': self.volume_history,
            'cycles': list(range(len(self.price_history)))
        }
