import pygame
import sys
import time
from typing import List, Dict
from simulator import TradingSimulator
from dialog import show_input_dialog
from bot_config_window import show_bot_config_window

# Цвета - современная темная тема
BLACK = (15, 15, 20)
WHITE = (255, 255, 255)
GREEN = (46, 204, 113)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
GRAY = (149, 165, 166)
DARK_GRAY = (44, 62, 80)
LIGHT_GRAY = (189, 195, 199)
YELLOW = (241, 196, 15)
CYAN = (26, 188, 156)
PURPLE = (155, 89, 182)
ORANGE = (230, 126, 34)

# Дополнительные цвета для красивого интерфейса
BACKGROUND = (20, 25, 30)
PANEL_BG = (30, 35, 40)
BORDER = (60, 70, 80)
ACCENT = (52, 152, 219)
SUCCESS = (46, 204, 113)
WARNING = (241, 196, 15)
ERROR = (231, 76, 60)
INFO = (26, 188, 156)

class TradingVisualizer:
    def __init__(self, simulator: TradingSimulator):
        pygame.init()
        self.simulator = simulator
        self.screen_width = 1400
        self.screen_height = 900
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Симулятор биржевого стакана")
        
        # Улучшенные шрифты
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 42)
        
        # Области отображения с отступами
        margin = 20
        self.order_book_rect = pygame.Rect(margin, 80, 450, 500)
        self.price_chart_rect = pygame.Rect(500, 80, 880, 350)
        self.agent_stats_rect = pygame.Rect(500, 450, 880, 400)
        self.control_panel_rect = pygame.Rect(margin, 600, 450, 280)  # Увеличили высоту для кнопки
        
        # Кнопка переключения бота
        self.bot_toggle_button = pygame.Rect(margin + 15, 600 + 200, 200, 50)
        self.bot_toggle_hover = False
        
        self.is_running = False
        self.cycle_delay = 0.1  # Задержка между циклами в секундах
        
    def run(self):
        """Основной цикл визуализации"""
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_running = not self.is_running
                    elif event.key == pygame.K_RIGHT:
                        # Один шаг симуляции
                        self.simulator.run_cycle()
                    elif event.key == pygame.K_r:
                        # Сброс симуляции
                        self.reset_simulation()
                    elif event.key == pygame.K_s:
                        # Настройка циклов для среднего спреда
                        self._show_spread_cycles_dialog()
                    elif event.key == pygame.K_b:
                        # Настройка увеличения баланса
                        self._show_balance_increase_dialog()
                    elif event.key == pygame.K_t:
                        # Настройка бота
                        self._show_bot_config_dialog()
                    elif event.key == pygame.K_c:
                        # Переключение бота
                        self.simulator.toggle_bot()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка мыши
                        mouse_pos = event.pos
                        if self.bot_toggle_button.collidepoint(mouse_pos):
                            # Переключение бота
                            self.simulator.toggle_bot()
                            bot_status = "включен" if self.simulator.trading_bot.config.enabled else "выключен"
                            print(f"🤖 Торговый бот {bot_status}")
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos
                    self.bot_toggle_hover = self.bot_toggle_button.collidepoint(mouse_pos)
            
            if self.is_running:
                self.simulator.run_cycle()
                time.sleep(self.cycle_delay)
            
            self.draw()
            clock.tick(60)
    
    def draw(self):
        """Отрисовывает все элементы интерфейса"""
        # Градиентный фон
        self.screen.fill(BACKGROUND)
        
        # Рисуем красивые панели с тенями
        self.draw_panel(self.order_book_rect, "[СТАКАН] БИРЖЕВОЙ СТАКАН")
        self.draw_panel(self.price_chart_rect, "[ГРАФИК] ГРАФИК ЦЕНЫ")
        self.draw_panel(self.agent_stats_rect, "[АГЕНТЫ] СТАТИСТИКА АГЕНТОВ")
        self.draw_panel(self.control_panel_rect, "[УПРАВЛЕНИЕ] ПАНЕЛЬ УПРАВЛЕНИЯ")
        
        # Отрисовываем содержимое
        self.draw_order_book()
        self.draw_price_chart()
        self.draw_agent_stats()
        self.draw_control_panel()
        
        # Статус-бар внизу
        self.draw_status_bar()
        
        pygame.display.flip()
    
    def draw_panel(self, rect, title):
        """Рисует красивую панель с тенью и заголовком"""
        # Тень
        shadow_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        # Основная панель
        pygame.draw.rect(self.screen, PANEL_BG, rect, border_radius=8)
        pygame.draw.rect(self.screen, BORDER, rect, 2, border_radius=8)
        
        # Заголовок с иконкой
        title_rect = pygame.Rect(rect.x + 15, rect.y - 35, rect.width - 30, 30)
        pygame.draw.rect(self.screen, ACCENT, title_rect, border_radius=6)
        self.draw_text(title, rect.x + 20, rect.y - 30, self.large_font, WHITE)
    
    def draw_status_bar(self):
        """Рисует статус-бар внизу экрана"""
        status_rect = pygame.Rect(0, self.screen_height - 40, self.screen_width, 40)
        pygame.draw.rect(self.screen, DARK_GRAY, status_rect)
        pygame.draw.rect(self.screen, BORDER, status_rect, 1)
        
        # Статус симуляции
        data = self.simulator.get_simulation_data()
        status = "[RUN] ЗАПУЩЕНА" if self.is_running else "[STOP] ОСТАНОВЛЕНА"
        status_color = SUCCESS if self.is_running else ERROR
        
        self.draw_text(f"Статус: {status}", 20, self.screen_height - 30, self.small_font, status_color)
        self.draw_text(f"Цикл: {data['cycle']}", 200, self.screen_height - 30, self.small_font, WHITE)
        self.draw_text(f"Сделок: {data['total_trades']}", 350, self.screen_height - 30, self.small_font, WHITE)
        self.draw_text(f"Объем: {data['total_volume']}", 500, self.screen_height - 30, self.small_font, WHITE)
    
    def draw_order_book(self):
        """Отрисовывает стакан заявок"""
        data = self.simulator.get_simulation_data()
        order_book = data['order_book']
        
        y_offset = 20
        
        # Текущая цена с красивым оформлением
        current_price = order_book['current_price']
        price_rect = pygame.Rect(self.order_book_rect.x + 15, self.order_book_rect.y + y_offset, 200, 35)
        pygame.draw.rect(self.screen, ACCENT, price_rect, border_radius=6)
        self.draw_text(f"ЦЕНА: {current_price:.2f}", 
                      self.order_book_rect.x + 25, self.order_book_rect.y + y_offset + 8, self.large_font, WHITE)
        y_offset += 45
        
        # Спред
        spread = order_book['spread']
        if spread:
            spread_color = SUCCESS if spread < 1.0 else WARNING if spread < 5.0 else ERROR
            self.draw_text(f"СПРЕД: {spread:.2f}", 
                          self.order_book_rect.x + 15, self.order_book_rect.y + y_offset, self.small_font, spread_color)
            y_offset += 25
        
        # Средний спред
        avg_spread = data.get('average_spread')
        if avg_spread is not None:
            cycles = data.get('avg_spread_cycles', 50)
            self.draw_text(f"СР.СПРЕД ({cycles}): {avg_spread:.2f}", 
                          self.order_book_rect.x + 15, self.order_book_rect.y + y_offset, self.small_font, INFO)
            y_offset += 25
        
        # Информация об увеличении баланса
        balance_cycles = data.get('balance_increase_cycles', 100)
        balance_amount = data.get('balance_increase_amount', 1000)
        next_increase = data.get('next_balance_increase', 0)
        self.draw_text(f"БАЛАНС+: каждые {balance_cycles} циклов", 
                      self.order_book_rect.x + 15, self.order_book_rect.y + y_offset, self.small_font, CYAN)
        y_offset += 20
        self.draw_text(f"СУММА: {balance_amount:.0f}", 
                      self.order_book_rect.x + 15, self.order_book_rect.y + y_offset, self.small_font, CYAN)
        y_offset += 20
        self.draw_text(f"ОСТАЛОСЬ: {next_increase} циклов", 
                      self.order_book_rect.x + 15, self.order_book_rect.y + y_offset, self.small_font, WARNING)
        y_offset += 30
        
        # Заголовки колонок с красивым оформлением
        header_rect = pygame.Rect(self.order_book_rect.x + 15, self.order_book_rect.y + y_offset, self.order_book_rect.width - 30, 25)
        pygame.draw.rect(self.screen, DARK_GRAY, header_rect, border_radius=4)
        self.draw_text("ЦЕНА", self.order_book_rect.x + 20, self.order_book_rect.y + y_offset + 3, self.small_font, WHITE)
        self.draw_text("КОЛ-ВО", self.order_book_rect.x + 160, self.order_book_rect.y + y_offset + 3, self.small_font, WHITE)
        self.draw_text("АГЕНТ", self.order_book_rect.x + 260, self.order_book_rect.y + y_offset + 3, self.small_font, WHITE)
        y_offset += 30
        
        # Ордера на продажу (ASK)
        ask_header_rect = pygame.Rect(self.order_book_rect.x + 15, self.order_book_rect.y + y_offset, self.order_book_rect.width - 30, 20)
        pygame.draw.rect(self.screen, (231, 76, 60, 50), ask_header_rect, border_radius=3)
        self.draw_text("[ПРОДАЖА] ASK", self.order_book_rect.x + 20, self.order_book_rect.y + y_offset + 2, self.small_font, RED)
        y_offset += 25
        
        for i, level in enumerate(order_book['sell_levels'][:6]):  # Показываем топ-6
            # Чередующиеся цвета строк
            row_color = (40, 45, 50) if i % 2 == 0 else (35, 40, 45)
            row_rect = pygame.Rect(self.order_book_rect.x + 15, self.order_book_rect.y + y_offset - 2, self.order_book_rect.width - 30, 18)
            pygame.draw.rect(self.screen, row_color, row_rect, border_radius=2)
            
            self.draw_text(f"{level['price']:.2f}", self.order_book_rect.x + 20, self.order_book_rect.y + y_offset, self.small_font, RED)
            self.draw_text(f"{level['quantity']}", self.order_book_rect.x + 160, self.order_book_rect.y + y_offset, self.small_font, WHITE)
            self.draw_text(f"{level['agent_id']}", self.order_book_rect.x + 260, self.order_book_rect.y + y_offset, self.small_font, LIGHT_GRAY)
            y_offset += 20
        
        y_offset += 10
        
        # Ордера на покупку (BID)
        bid_header_rect = pygame.Rect(self.order_book_rect.x + 15, self.order_book_rect.y + y_offset, self.order_book_rect.width - 30, 20)
        pygame.draw.rect(self.screen, (46, 204, 113, 50), bid_header_rect, border_radius=3)
        self.draw_text("[ПОКУПКА] BID", self.order_book_rect.x + 20, self.order_book_rect.y + y_offset + 2, self.small_font, GREEN)
        y_offset += 25
        
        for i, level in enumerate(order_book['buy_levels'][:6]):  # Показываем топ-6
            # Чередующиеся цвета строк
            row_color = (40, 45, 50) if i % 2 == 0 else (35, 40, 45)
            row_rect = pygame.Rect(self.order_book_rect.x + 15, self.order_book_rect.y + y_offset - 2, self.order_book_rect.width - 30, 18)
            pygame.draw.rect(self.screen, row_color, row_rect, border_radius=2)
            
            self.draw_text(f"{level['price']:.2f}", self.order_book_rect.x + 20, self.order_book_rect.y + y_offset, self.small_font, GREEN)
            self.draw_text(f"{level['quantity']}", self.order_book_rect.x + 160, self.order_book_rect.y + y_offset, self.small_font, WHITE)
            self.draw_text(f"{level['agent_id']}", self.order_book_rect.x + 260, self.order_book_rect.y + y_offset, self.small_font, LIGHT_GRAY)
            y_offset += 20
    
    def draw_price_chart(self):
        """Отрисовывает график цены"""
        data = self.simulator.get_simulation_data()
        prices = data['price_history']
        
        if len(prices) < 2:
            return
        
        # Находим диапазон цен
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = 1
        
        # Масштабируем цены для отображения
        chart_width = self.price_chart_rect.width - 40
        chart_height = self.price_chart_rect.height - 60
        
        # Рисуем фон графика
        chart_bg_rect = pygame.Rect(self.price_chart_rect.x + 20, self.price_chart_rect.y + 30, chart_width, chart_height)
        pygame.draw.rect(self.screen, (25, 30, 35), chart_bg_rect, border_radius=6)
        pygame.draw.rect(self.screen, BORDER, chart_bg_rect, 1, border_radius=6)
        
        # Рисуем сетку
        for i in range(5):
            y = self.price_chart_rect.y + 30 + (i * chart_height) // 4
            pygame.draw.line(self.screen, (50, 55, 60), 
                           (self.price_chart_rect.x + 20, y), 
                           (self.price_chart_rect.x + 20 + chart_width, y), 1)
        
        # Рисуем вертикальные линии
        for i in range(10):
            x = self.price_chart_rect.x + 20 + (i * chart_width) // 9
            pygame.draw.line(self.screen, (50, 55, 60), 
                           (x, self.price_chart_rect.y + 30), 
                           (x, self.price_chart_rect.y + 30 + chart_height), 1)
        
        # Подготавливаем точки для графика
        points = []
        for i, price in enumerate(prices):
            x = self.price_chart_rect.x + 20 + (i * chart_width) // len(prices)
            y = self.price_chart_rect.y + 30 + chart_height - int(((price - min_price) / price_range) * chart_height)
            points.append((x, y))
        
        # Рисуем область под графиком (градиент)
        if len(points) > 1:
            # Создаем полигон для заливки
            polygon_points = [(self.price_chart_rect.x + 20, self.price_chart_rect.y + 30 + chart_height)]
            polygon_points.extend(points)
            polygon_points.append((self.price_chart_rect.x + 20 + chart_width, self.price_chart_rect.y + 30 + chart_height))
            
            # Рисуем заливку
            pygame.draw.polygon(self.screen, (52, 152, 219, 30), polygon_points)
            
            # Рисуем линию графика
            pygame.draw.lines(self.screen, ACCENT, False, points, 3)
            
            # Рисуем точки
            for point in points[::max(1, len(points)//20)]:  # Показываем каждую 20-ю точку
                pygame.draw.circle(self.screen, ACCENT, point, 3)
        
        # Подписи цен
        for i in range(5):
            price = min_price + (i * price_range) // 4
            y = self.price_chart_rect.y + 30 + (i * chart_height) // 4
            price_text = f"{price:.1f}"
            text_surface = self.small_font.render(price_text, True, LIGHT_GRAY)
            text_rect = text_surface.get_rect()
            self.draw_text(price_text, self.price_chart_rect.x + 5, y - text_rect.height//2, self.small_font, LIGHT_GRAY)
        
        # Текущая цена
        if prices:
            current_price = prices[-1]
            current_y = self.price_chart_rect.y + 30 + chart_height - int(((current_price - min_price) / price_range) * chart_height)
            pygame.draw.line(self.screen, WARNING, 
                           (self.price_chart_rect.x + 20, current_y), 
                           (self.price_chart_rect.x + 20 + chart_width, current_y), 2)
    
    def draw_agent_stats(self):
        """Отрисовывает статистику агентов"""
        data = self.simulator.get_simulation_data()
        agents = data['agents']
        
        # Заголовки с красивым оформлением
        y_offset = 20
        header_rect = pygame.Rect(self.agent_stats_rect.x + 15, self.agent_stats_rect.y + y_offset, self.agent_stats_rect.width - 30, 30)
        pygame.draw.rect(self.screen, DARK_GRAY, header_rect, border_radius=6)
        
        # Заголовки колонок
        self.draw_text("ID", self.agent_stats_rect.x + 25, self.agent_stats_rect.y + y_offset + 5, self.small_font, WHITE)
        self.draw_text("СТР", self.agent_stats_rect.x + 60, self.agent_stats_rect.y + y_offset + 5, self.small_font, WHITE)
        self.draw_text("БАЛ", self.agent_stats_rect.x + 110, self.agent_stats_rect.y + y_offset + 5, self.small_font, WHITE)
        self.draw_text("ПОЗ", self.agent_stats_rect.x + 190, self.agent_stats_rect.y + y_offset + 5, self.small_font, WHITE)
        self.draw_text("ПОРТ", self.agent_stats_rect.x + 260, self.agent_stats_rect.y + y_offset + 5, self.small_font, WHITE)
        self.draw_text("ПРОФ", self.agent_stats_rect.x + 340, self.agent_stats_rect.y + y_offset + 5, self.small_font, WHITE)
        self.draw_text("ЗАЯВ", self.agent_stats_rect.x + 430, self.agent_stats_rect.y + y_offset + 5, self.small_font, WHITE)
        self.draw_text("РИСК", self.agent_stats_rect.x + 510, self.agent_stats_rect.y + y_offset + 5, self.small_font, WHITE)
        
        y_offset += 25
        
        # Данные агентов
        for i, agent in enumerate(agents[:15]):  # Показываем топ-15 агентов
            # Чередующиеся цвета строк
            row_color = (40, 45, 50) if i % 2 == 0 else (35, 40, 45)
            row_rect = pygame.Rect(self.agent_stats_rect.x + 15, self.agent_stats_rect.y + y_offset - 2, self.agent_stats_rect.width - 30, 20)
            pygame.draw.rect(self.screen, row_color, row_rect, border_radius=3)
            
            # ID с рангом
            rank_text = "1st" if i == 0 else "2nd" if i == 1 else "3rd" if i == 2 else f"{i+1:2d}"
            self.draw_text(rank_text, self.agent_stats_rect.x + 20, self.agent_stats_rect.y + y_offset, self.small_font, WHITE)
            
            # Стратегия
            strategy_name = agent.get('strategy', 'UNKNOWN')[:4]  # Первые 4 символа
            strategy_color = self._get_strategy_color(strategy_name)
            self.draw_text(strategy_name, self.agent_stats_rect.x + 60, self.agent_stats_rect.y + y_offset, self.small_font, strategy_color)
            
            # Баланс
            balance_color = SUCCESS if agent['balance'] > 0 else ERROR
            self.draw_text(f"{agent['balance']:.0f}", self.agent_stats_rect.x + 110, self.agent_stats_rect.y + y_offset, self.small_font, balance_color)
            
            # Позиция
            position_color = SUCCESS if agent['position'] > 0 else ERROR if agent['position'] < 0 else LIGHT_GRAY
            position_symbol = "+" if agent['position'] > 0 else "" if agent['position'] < 0 else "0"
            self.draw_text(f"{position_symbol}{agent['position']}", self.agent_stats_rect.x + 190, self.agent_stats_rect.y + y_offset, self.small_font, position_color)
            
            # Портфель
            portfolio_color = SUCCESS if agent['portfolio_value'] > 0 else ERROR
            self.draw_text(f"{agent['portfolio_value']:.0f}", self.agent_stats_rect.x + 260, self.agent_stats_rect.y + y_offset, self.small_font, portfolio_color)
            
            # Профит
            profit = agent.get('profit', 0)
            profit_percent = agent.get('profit_percent', 0)
            profit_color = SUCCESS if profit > 0 else ERROR if profit < 0 else LIGHT_GRAY
            profit_symbol = "+" if profit > 0 else "" if profit < 0 else "0"
            profit_text = f"{profit_symbol}{profit:+.0f} ({profit_percent:+.1f}%)"
            self.draw_text(profit_text, self.agent_stats_rect.x + 340, self.agent_stats_rect.y + y_offset, self.small_font, profit_color)
            
            # Заявки (покупка/продажа/всего)
            buy_orders = agent.get('buy_orders', 0)
            sell_orders = agent.get('sell_orders', 0)
            total_orders = agent.get('total_orders', 0)
            orders_text = f"{buy_orders}/{sell_orders}/{total_orders}"
            orders_color = SUCCESS if total_orders > 0 else GRAY
            self.draw_text(orders_text, self.agent_stats_rect.x + 430, self.agent_stats_rect.y + y_offset, self.small_font, orders_color)
            
            # Риск
            risk = agent['risk_tolerance']
            risk_color = ERROR if risk > 0.7 else WARNING if risk > 0.4 else SUCCESS
            risk_symbol = "H" if risk > 0.7 else "M" if risk > 0.4 else "L"
            self.draw_text(f"{risk_symbol}{risk:.2f}", self.agent_stats_rect.x + 510, self.agent_stats_rect.y + y_offset, self.small_font, risk_color)
            
            y_offset += 22
        
        # Общая статистика
        y_offset += 20
        total_volume = data['total_volume']
        self.draw_text(f"Общий объем торгов: {total_volume}", 
                      self.agent_stats_rect.x + 10, self.agent_stats_rect.y + y_offset, self.small_font, WHITE)
        
        # Лучший и худший агенты
        if agents:
            best_agent = agents[0]  # Первый в отсортированном списке
            worst_agent = agents[-1]  # Последний в отсортированном списке
            
            y_offset += 20
            best_orders = f"{best_agent['buy_orders']}/{best_agent['sell_orders']}/{best_agent['total_orders']}"
            self.draw_text(f"Лучший: ID{best_agent['id']} ({best_agent['strategy'][:4]}) {best_agent['profit']:+.0f} [{best_orders}]", 
                          self.agent_stats_rect.x + 10, self.agent_stats_rect.y + y_offset, self.small_font, GREEN)
            
            y_offset += 15
            worst_orders = f"{worst_agent['buy_orders']}/{worst_agent['sell_orders']}/{worst_agent['total_orders']}"
            self.draw_text(f"Худший: ID{worst_agent['id']} ({worst_agent['strategy'][:4]}) {worst_agent['profit']:+.0f} [{worst_orders}]", 
                          self.agent_stats_rect.x + 10, self.agent_stats_rect.y + y_offset, self.small_font, RED)
    
    def draw_control_panel(self):
        """Отрисовывает панель управления"""
        y_offset = 20
        
        # Статус симуляции с красивым оформлением
        status_rect = pygame.Rect(self.control_panel_rect.x + 15, self.control_panel_rect.y + y_offset, self.control_panel_rect.width - 30, 40)
        status_color = SUCCESS if self.is_running else ERROR
        pygame.draw.rect(self.screen, status_color, status_rect, border_radius=8)
        
        status = "[RUN] ЗАПУЩЕНА" if self.is_running else "[STOP] ОСТАНОВЛЕНА"
        self.draw_text(f"Статус: {status}", self.control_panel_rect.x + 25, self.control_panel_rect.y + y_offset + 12, self.font, WHITE)
        y_offset += 50
        
        # Управление с иконками
        self.draw_text("[УПРАВЛЕНИЕ]:", self.control_panel_rect.x + 15, self.control_panel_rect.y + y_offset, self.small_font, WHITE)
        y_offset += 25
        
        # Кнопки управления
        controls = [
            ("[>]", "ПРОБЕЛ", "Запуск/Остановка"),
            ("[>]", "СТРЕЛКА ВПРАВО", "Один шаг"),
            ("[R]", "R", "Сброс симуляции"),
            ("[S]", "S", "Настройка среднего спреда"),
            ("[B]", "B", "Настройка увеличения баланса"),
            ("[T]", "T", "Настройка бота"),
            ("[C]", "C", "Переключение бота")
        ]
        
        for symbol, key, description in controls:
            # Фон для кнопки
            button_rect = pygame.Rect(self.control_panel_rect.x + 15, self.control_panel_rect.y + y_offset - 2, self.control_panel_rect.width - 30, 25)
            pygame.draw.rect(self.screen, (40, 45, 50), button_rect, border_radius=4)
            
            self.draw_text(f"{symbol} {key}", self.control_panel_rect.x + 20, self.control_panel_rect.y + y_offset, self.small_font, ACCENT)
            self.draw_text(description, self.control_panel_rect.x + 120, self.control_panel_rect.y + y_offset, self.small_font, LIGHT_GRAY)
            y_offset += 28
        
        # Статистика бота
        y_offset += 10
        self.draw_text("[БОТ]:", self.control_panel_rect.x + 15, self.control_panel_rect.y + y_offset, self.small_font, WHITE)
        y_offset += 20
        
        # Получаем статистику бота
        data = self.simulator.get_simulation_data()
        bot_stats = data.get('bot_statistics', {})
        
        # Статус бота
        bot_status = "ВКЛ" if bot_stats.get('enabled', False) else "ВЫКЛ"
        bot_status_color = SUCCESS if bot_stats.get('enabled', False) else ERROR
        self.draw_text(f"Статус: {bot_status}", self.control_panel_rect.x + 20, self.control_panel_rect.y + y_offset, self.small_font, bot_status_color)
        y_offset += 20
        
        # Интервал заявок
        interval = bot_stats.get('order_interval', 10)
        self.draw_text(f"Интервал: {interval} циклов", self.control_panel_rect.x + 20, self.control_panel_rect.y + y_offset, self.small_font, LIGHT_GRAY)
        y_offset += 18
        
        # Тип заявок
        order_type = bot_stats.get('order_type', 'random')
        self.draw_text(f"Тип: {order_type}", self.control_panel_rect.x + 20, self.control_panel_rect.y + y_offset, self.small_font, LIGHT_GRAY)
        y_offset += 18
        
        # Количество заявок
        orders_placed = bot_stats.get('orders_placed', 0)
        buy_orders = bot_stats.get('buy_orders', 0)
        sell_orders = bot_stats.get('sell_orders', 0)
        self.draw_text(f"Заявки: {buy_orders}/{sell_orders}/{orders_placed}", self.control_panel_rect.x + 20, self.control_panel_rect.y + y_offset, self.small_font, LIGHT_GRAY)
        y_offset += 18
        
        # Объем торгов
        total_volume = bot_stats.get('total_volume', 0)
        self.draw_text(f"Объем: {total_volume}", self.control_panel_rect.x + 20, self.control_panel_rect.y + y_offset, self.small_font, LIGHT_GRAY)
        
        # Кнопка переключения бота
        y_offset += 30
        self._draw_bot_toggle_button()
    
    def _draw_bot_toggle_button(self):
        """Отрисовывает кнопку переключения бота"""
        # Получаем текущий статус бота
        bot_stats = self.simulator.get_simulation_data()
        bot_enabled = bot_stats.get('bot_statistics', {}).get('enabled', False)
        
        # Цвет кнопки в зависимости от статуса и hover
        if self.bot_toggle_hover:
            button_color = self.button_hover_color
        else:
            button_color = SUCCESS if bot_enabled else ERROR
        
        # Рисуем кнопку
        pygame.draw.rect(self.screen, button_color, self.bot_toggle_button, border_radius=8)
        pygame.draw.rect(self.screen, BORDER, self.bot_toggle_button, 2, border_radius=8)
        
        # Текст кнопки
        button_text = "🤖 ВЫКЛЮЧИТЬ БОТА" if bot_enabled else "🤖 ВКЛЮЧИТЬ БОТА"
        text_surface = self.text_font.render(button_text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.bot_toggle_button.center)
        self.screen.blit(text_surface, text_rect)
        
        # Подсказка
        hint_text = "Кликните для переключения"
        hint_surface = self.small_font.render(hint_text, True, LIGHT_GRAY)
        hint_rect = hint_surface.get_rect()
        hint_x = self.bot_toggle_button.right + 10
        hint_y = self.bot_toggle_button.centery - hint_rect.height // 2
        self.screen.blit(hint_surface, (hint_x, hint_y))
    
    def draw_text(self, text, x, y, font, color):
        """Вспомогательная функция для отрисовки текста"""
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def _get_strategy_color(self, strategy_name: str) -> tuple:
        """Возвращает цвет для стратегии"""
        strategy_colors = {
            'MOME': YELLOW,      # Momentum
            'MEAN': CYAN,        # Mean Reversion
            'MARK': GREEN,       # Market Maker
            'SCAL': RED,         # Scalper
            'VALU': BLUE,        # Value Investor
            'NOIS': GRAY,        # Noise Trader
        }
        return strategy_colors.get(strategy_name, WHITE)
    
    def _show_spread_cycles_dialog(self):
        """Показывает диалог для ввода количества циклов среднего спреда"""
        current_cycles = self.simulator.avg_spread_cycles
        result = show_input_dialog(
            self.screen,
            "Настройка среднего спреда",
            f"Введите количество циклов (1-1000):",
            str(current_cycles)
        )
        
        if result:
            try:
                cycles = int(result)
                if 1 <= cycles <= 1000:
                    self.simulator.set_avg_spread_cycles(cycles)
                    print(f"Установлено {cycles} циклов для расчета среднего спреда")
                else:
                    print("Количество циклов должно быть от 1 до 1000")
            except ValueError:
                print("Неверный формат числа")
    
    def _show_balance_increase_dialog(self):
        """Показывает диалог для настройки увеличения баланса"""
        data = self.simulator.get_simulation_data()
        current_cycles = data.get('balance_increase_cycles', 100)
        current_amount = data.get('balance_increase_amount', 1000)
        
        # Диалог для циклов
        cycles_result = show_input_dialog(
            self.screen,
            "Настройка увеличения баланса",
            f"Введите количество циклов (1-10000):",
            str(current_cycles)
        )
        
        if cycles_result:
            try:
                cycles = int(cycles_result)
                if 1 <= cycles <= 10000:
                    # Диалог для суммы
                    amount_result = show_input_dialog(
                        self.screen,
                        "Настройка увеличения баланса",
                        f"Введите сумму увеличения (0-100000):",
                        str(int(current_amount))
                    )
                    
                    if amount_result:
                        try:
                            amount = float(amount_result)
                            if 0 <= amount <= 100000:
                                self.simulator.set_balance_increase_settings(cycles, amount)
                            else:
                                print("Сумма должна быть от 0 до 100000")
                        except ValueError:
                            print("Неверный формат суммы")
                else:
                    print("Количество циклов должно быть от 1 до 10000")
            except ValueError:
                print("Неверный формат числа")
    
    def _show_bot_config_dialog(self):
        """Показывает единое окно настройки бота"""
        # Получаем текущую конфигурацию бота
        bot_config = self.simulator.trading_bot.config
        
        # Callback для обновления конфигурации
        def on_config_changed(config_updates):
            print("🤖 Настройки бота обновлены:")
            for key, value in config_updates.items():
                print(f"  {key}: {value}")
        
        # Показываем окно настройки
        result = show_bot_config_window(
            self.screen, 
            bot_config, 
            on_config_changed
        )
        
        if result:
            print("✅ Конфигурация бота успешно сохранена!")
        else:
            print("❌ Настройка бота отменена")
    
    def reset_simulation(self):
        """Сбрасывает симуляцию"""
        # Останавливаем симуляцию
        self.is_running = False
        
        # Создаем новый симулятор с теми же параметрами
        initial_price = self.simulator.order_book.initial_price
        num_agents = len(self.simulator.agents)
        initial_balance = self.simulator.agents[0].balance if self.simulator.agents else 10000.0
        
        # Создаем новый симулятор
        from simulator import TradingSimulator
        self.simulator = TradingSimulator(initial_price, num_agents, initial_balance)
        
        print("Симуляция сброшена!")
