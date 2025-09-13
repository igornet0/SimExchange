import random
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Order:
    id: int
    price: float
    quantity: int
    order_type: OrderType
    agent_id: int
    timestamp: float

@dataclass
class Trade:
    id: int
    price: float
    quantity: int
    buyer_id: int
    seller_id: int
    timestamp: float

class OrderBook:
    def __init__(self, initial_price: float):
        self.initial_price = initial_price
        self.current_price = initial_price
        self.buy_orders: List[Order] = []  # Сортированы по убыванию цены
        self.sell_orders: List[Order] = []  # Сортированы по возрастанию цены
        self.trades: List[Trade] = []
        self.next_order_id = 1
        self.next_trade_id = 1
        
    def add_order(self, order: Order) -> List[Trade]:
        """Добавляет ордер в стакан и выполняет сделки"""
        new_trades = []
        
        if order.order_type == OrderType.BUY:
            # Ищем подходящие ордера на продажу
            remaining_quantity = order.quantity
            orders_to_remove = []
            
            for i, sell_order in enumerate(self.sell_orders):
                if sell_order.price <= order.price and remaining_quantity > 0:
                    trade_quantity = min(remaining_quantity, sell_order.quantity)
                    
                    # Создаем сделку
                    trade = Trade(
                        id=self.next_trade_id,
                        price=sell_order.price,
                        quantity=trade_quantity,
                        buyer_id=order.agent_id,
                        seller_id=sell_order.agent_id,
                        timestamp=time.time()
                    )
                    new_trades.append(trade)
                    self.trades.append(trade)
                    self.next_trade_id += 1
                    
                    # Обновляем цены
                    self.current_price = sell_order.price
                    
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
                self.buy_orders.append(order)
                self.buy_orders.sort(key=lambda x: x.price, reverse=True)
        
        else:  # SELL
            # Ищем подходящие ордера на покупку
            remaining_quantity = order.quantity
            orders_to_remove = []
            
            for i, buy_order in enumerate(self.buy_orders):
                if buy_order.price >= order.price and remaining_quantity > 0:
                    trade_quantity = min(remaining_quantity, buy_order.quantity)
                    
                    # Создаем сделку
                    trade = Trade(
                        id=self.next_trade_id,
                        price=buy_order.price,
                        quantity=trade_quantity,
                        buyer_id=buy_order.agent_id,
                        seller_id=order.agent_id,
                        timestamp=time.time()
                    )
                    new_trades.append(trade)
                    self.trades.append(trade)
                    self.next_trade_id += 1
                    
                    # Обновляем цены
                    self.current_price = buy_order.price
                    
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
                self.sell_orders.append(order)
                self.sell_orders.sort(key=lambda x: x.price)
        
        return new_trades
    
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
    
    def get_order_book_data(self, levels: int = 10) -> Dict:
        """Возвращает данные стакана для отображения"""
        buy_levels = []
        sell_levels = []
        
        # Топ уровни покупки (по убыванию цены)
        for order in self.buy_orders[:levels]:
            buy_levels.append({
                'price': order.price,
                'quantity': order.quantity,
                'agent_id': order.agent_id
            })
        
        # Топ уровни продажи (по возрастанию цены)
        for order in self.sell_orders[:levels]:
            sell_levels.append({
                'price': order.price,
                'quantity': order.quantity,
                'agent_id': order.agent_id
            })
        
        return {
            'buy_levels': buy_levels,
            'sell_levels': sell_levels,
            'current_price': self.current_price,
            'best_bid': self.get_best_bid(),
            'best_ask': self.get_best_ask(),
            'spread': self.get_spread(),
            'total_trades': len(self.trades)
        }

