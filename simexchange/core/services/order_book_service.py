"""
Сервис для работы со стаканом заявок
"""

import time
from typing import List, Optional, Dict, Any, Tuple
from ..models import Order, Trade, OrderType


class OrderBookService:
    """Сервис для работы со стаканом заявок"""
    
    def __init__(self, initial_price: float, max_trades_history: int = 5000):
        self.initial_price = initial_price
        self.current_price = initial_price
        self.max_trades_history = max_trades_history
        
        # Стакан заявок
        self.buy_orders: List[Order] = []  # Сортированы по убыванию цены
        self.sell_orders: List[Order] = []  # Сортированы по возрастанию цены
        
        # История сделок
        self.trades: List[Trade] = []
        
        # Счетчики
        self.next_order_id = 1
        self.next_trade_id = 1
    
    def add_order(self, order: Order) -> List[Trade]:
        """Добавляет ордер в стакан и выполняет сделки"""
        new_trades = []
        
        if order.order_type == OrderType.BUY:
            new_trades = self._process_buy_order(order)
        else:  # SELL
            new_trades = self._process_sell_order(order)
        
        # Обновляем цену на основе последней сделки
        if new_trades:
            self.current_price = new_trades[-1].price
        
        return new_trades
    
    def _process_buy_order(self, order: Order) -> List[Trade]:
        """Обрабатывает ордер на покупку"""
        new_trades = []
        remaining_quantity = order.quantity
        orders_to_remove = []
        
        # Ищем подходящие ордера на продажу
        for i, sell_order in enumerate(self.sell_orders):
            if sell_order.price <= order.price and remaining_quantity > 0:
                trade_quantity = min(remaining_quantity, sell_order.quantity)
                
                # Создаем сделку
                trade = Trade.create_from_orders(
                    self.next_trade_id,
                    order,
                    sell_order,
                    trade_quantity
                )
                new_trades.append(trade)
                self.trades.append(trade)
                self.next_trade_id += 1
                
                # Ограничиваем размер истории сделок
                if len(self.trades) > self.max_trades_history:
                    self.trades = self.trades[-self.max_trades_history:]
                
                # Уменьшаем количество в ордерах
                remaining_quantity -= trade_quantity
                sell_order.quantity -= trade_quantity
                
                if sell_order.quantity == 0:
                    orders_to_remove.append(i)
                
                if remaining_quantity == 0:
                    break
        
        # Удаляем исполненные ордера на продажу
        for i in reversed(orders_to_remove):
            self.sell_orders.pop(i)
        
        # Если остался объем, добавляем ордер на покупку
        if remaining_quantity > 0:
            order.quantity = remaining_quantity
            self._insert_buy_order(order)
        
        return new_trades
    
    def _process_sell_order(self, order: Order) -> List[Trade]:
        """Обрабатывает ордер на продажу"""
        new_trades = []
        remaining_quantity = order.quantity
        orders_to_remove = []
        
        # Ищем подходящие ордера на покупку
        for i, buy_order in enumerate(self.buy_orders):
            if buy_order.price >= order.price and remaining_quantity > 0:
                trade_quantity = min(remaining_quantity, buy_order.quantity)
                
                # Создаем сделку (buy_order - покупатель, order - продавец)
                trade = Trade.create_from_orders(
                    self.next_trade_id,
                    buy_order,
                    order,
                    trade_quantity
                )
                new_trades.append(trade)
                self.trades.append(trade)
                self.next_trade_id += 1
                
                # Ограничиваем размер истории сделок
                if len(self.trades) > self.max_trades_history:
                    self.trades = self.trades[-self.max_trades_history:]
                
                # Уменьшаем количество в ордерах
                remaining_quantity -= trade_quantity
                buy_order.quantity -= trade_quantity
                
                if buy_order.quantity == 0:
                    orders_to_remove.append(i)
                
                if remaining_quantity == 0:
                    break
        
        # Удаляем исполненные ордера на покупку
        for i in reversed(orders_to_remove):
            self.buy_orders.pop(i)
        
        # Если остался объем, добавляем ордер на продажу
        if remaining_quantity > 0:
            order.quantity = remaining_quantity
            self._insert_sell_order(order)
        
        return new_trades
    
    def _insert_buy_order(self, order: Order):
        """Вставляет ордер на покупку в отсортированный список"""
        # Вставляем в правильное место для поддержания сортировки по убыванию цены
        for i, existing_order in enumerate(self.buy_orders):
            if order.price > existing_order.price:
                self.buy_orders.insert(i, order)
                return
        self.buy_orders.append(order)
    
    def _insert_sell_order(self, order: Order):
        """Вставляет ордер на продажу в отсортированный список"""
        # Вставляем в правильное место для поддержания сортировки по возрастанию цены
        for i, existing_order in enumerate(self.sell_orders):
            if order.price < existing_order.price:
                self.sell_orders.insert(i, order)
                return
        self.sell_orders.append(order)
    
    def get_best_bid(self) -> Optional[float]:
        """Возвращает лучшую цену покупки"""
        return self.buy_orders[0].price if self.buy_orders else None
    
    def get_best_ask(self) -> Optional[float]:
        """Возвращает лучшую цену продажи"""
        return self.sell_orders[0].price if self.sell_orders else None
    
    def get_spread(self) -> Optional[float]:
        """Возвращает спред между лучшими ценами"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid and best_ask:
            return best_ask - best_bid
        return None
    
    def get_order_book_data(self, levels: int = 10) -> Dict[str, Any]:
        """Возвращает данные стакана для отображения"""
        buy_levels = []
        sell_levels = []
        
        # Топ уровни покупки (по убыванию цены)
        for order in self.buy_orders[:levels]:
            buy_levels.append({
                'price': order.price,
                'quantity': order.quantity,
                'agent_id': order.agent_id,
                'timestamp': order.timestamp
            })
        
        # Топ уровни продажи (по возрастанию цены)
        for order in self.sell_orders[:levels]:
            sell_levels.append({
                'price': order.price,
                'quantity': order.quantity,
                'agent_id': order.agent_id,
                'timestamp': order.timestamp
            })
        
        return {
            'buy_levels': buy_levels,
            'sell_levels': sell_levels,
            'current_price': self.current_price,
            'best_bid': self.get_best_bid(),
            'best_ask': self.get_best_ask(),
            'spread': self.get_spread(),
            'total_trades': len(self.trades),
            'total_buy_orders': len(self.buy_orders),
            'total_sell_orders': len(self.sell_orders)
        }
    
    def get_trades(self, limit: Optional[int] = None) -> List[Trade]:
        """Возвращает список сделок"""
        if limit is None:
            return self.trades.copy()
        return self.trades[-limit:] if limit > 0 else []
    
    def get_total_volume(self) -> int:
        """Возвращает общий объем торгов"""
        return sum(trade.quantity for trade in self.trades)
    
    def get_total_value(self) -> float:
        """Возвращает общую стоимость торгов"""
        return sum(trade.get_total_value() for trade in self.trades)
    
    def get_agent_trades(self, agent_id: int) -> List[Trade]:
        """Возвращает сделки конкретного агента"""
        return [trade for trade in self.trades if trade.involves_agent(agent_id)]
    
    def get_agent_volume(self, agent_id: int) -> int:
        """Возвращает объем торгов агента"""
        agent_trades = self.get_agent_trades(agent_id)
        return sum(trade.quantity for trade in agent_trades)
    
    def get_agent_value(self, agent_id: int) -> float:
        """Возвращает стоимость торгов агента"""
        agent_trades = self.get_agent_trades(agent_id)
        return sum(trade.get_total_value() for trade in agent_trades)
    
    def get_price_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику по ценам"""
        if not self.trades:
            return {
                'min_price': self.current_price,
                'max_price': self.current_price,
                'avg_price': self.current_price,
                'price_range': 0.0
            }
        
        prices = [trade.price for trade in self.trades]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        return {
            'min_price': min_price,
            'max_price': max_price,
            'avg_price': avg_price,
            'price_range': max_price - min_price,
            'current_price': self.current_price,
            'price_change': self.current_price - self.initial_price,
            'price_change_percent': ((self.current_price - self.initial_price) / self.initial_price) * 100
        }
    
    def clear_old_orders(self, max_age_seconds: float = 3600):
        """Удаляет старые ордера"""
        current_time = time.time()
        
        # Удаляем старые ордера на покупку
        self.buy_orders = [order for order in self.buy_orders 
                          if current_time - order.timestamp < max_age_seconds]
        
        # Удаляем старые ордера на продажу
        self.sell_orders = [order for order in self.sell_orders 
                           if current_time - order.timestamp < max_age_seconds]
    
    def reset(self):
        """Сбрасывает стакан заявок"""
        self.current_price = self.initial_price
        self.buy_orders.clear()
        self.sell_orders.clear()
        self.trades.clear()
        self.next_order_id = 1
        self.next_trade_id = 1
    
    def __str__(self) -> str:
        """Строковое представление сервиса"""
        return (f"OrderBookService(price={self.current_price:.2f}, "
                f"buy_orders={len(self.buy_orders)}, sell_orders={len(self.sell_orders)}, "
                f"trades={len(self.trades)})")
    
    def __repr__(self) -> str:
        """Детальное строковое представление"""
        return (f"OrderBookService(initial_price={self.initial_price}, "
                f"current_price={self.current_price}, "
                f"buy_orders_count={len(self.buy_orders)}, "
                f"sell_orders_count={len(self.sell_orders)}, "
                f"trades_count={len(self.trades)})")
