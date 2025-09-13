import pygame
import sys
from typing import Optional, Callable
from trading_bot import BotConfig

class BotConfigWindow:
    """Единое окно настройки торгового бота"""
    
    def __init__(self, screen, bot_config: BotConfig, on_config_changed: Callable = None):
        self.screen = screen
        self.bot_config = bot_config
        self.on_config_changed = on_config_changed
        self.running = True
        self.result = None
        
        # Размеры окна
        self.width = 600
        self.height = 500
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        # Шрифты
        self.title_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.input_font = pygame.font.Font(None, 22)
        
        # Цвета
        self.bg_color = (30, 35, 40)
        self.border_color = (60, 70, 80)
        self.text_color = (255, 255, 255)
        self.input_bg_color = (50, 55, 60)
        self.input_border_color = (100, 150, 200)
        self.input_active_color = (52, 152, 219)
        self.button_color = (70, 130, 180)
        self.button_hover_color = (100, 150, 200)
        self.success_color = (46, 204, 113)
        self.error_color = (231, 76, 60)
        self.warning_color = (241, 196, 15)
        
        # Прямоугольники
        self.dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Поля ввода
        self.input_fields = {}
        self.active_field = None
        self.field_values = {
            'enabled': str(bot_config.enabled).lower(),
            'order_interval': str(bot_config.order_interval),
            'order_type': bot_config.order_type,
            'quantity': str(bot_config.quantity),
            'price_offset': str(bot_config.price_offset),
            'price_range_min': str(bot_config.price_range_min),
            'price_range_max': str(bot_config.price_range_max)
        }
        
        # Кнопки
        self.buttons = {}
        self.button_hover = {}
        
        # Состояние
        self.error_message = ""
        self.success_message = ""
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настраивает элементы интерфейса"""
        # Поля ввода
        y_start = self.y + 80
        field_height = 35
        field_spacing = 50
        
        fields = [
            ('enabled', 'Включить бота (true/false)', self.y + 80),
            ('order_interval', 'Интервал заявок (1-1000)', self.y + 130),
            ('order_type', 'Тип заявок (buy/sell/random/both)', self.y + 180),
            ('quantity', 'Количество акций (1-1000)', self.y + 230),
            ('price_offset', 'Отклонение цены (0.001-0.1)', self.y + 280),
            ('price_range_min', 'Мин. цена (0.5-1.0)', self.y + 330),
            ('price_range_max', 'Макс. цена (1.0-2.0)', self.y + 380)
        ]
        
        for field_id, label, y_pos in fields:
            # Поле ввода
            input_rect = pygame.Rect(self.x + 250, y_pos, 200, field_height)
            self.input_fields[field_id] = {
                'rect': input_rect,
                'label': label,
                'label_y': y_pos + 8,
                'value': self.field_values[field_id]
            }
        
        # Кнопки
        button_y = self.y + 430
        self.buttons = {
            'save': pygame.Rect(self.x + 50, button_y, 100, 40),
            'reset': pygame.Rect(self.x + 170, button_y, 100, 40),
            'cancel': pygame.Rect(self.x + 450, button_y, 100, 40)
        }
        
        # Инициализируем состояние hover для кнопок
        for button_id in self.buttons:
            self.button_hover[button_id] = False
    
    def run(self) -> Optional[dict]:
        """Запускает окно настройки и возвращает конфигурацию или None"""
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None
                    elif event.key == pygame.K_RETURN:
                        self._save_config()
                    elif event.key == pygame.K_TAB:
                        self._switch_to_next_field()
                    elif event.key == pygame.K_BACKSPACE:
                        if self.active_field:
                            field = self.input_fields[self.active_field]
                            field['value'] = field['value'][:-1]
                    elif event.unicode.isprintable():
                        if self.active_field:
                            field = self.input_fields[self.active_field]
                            if len(field['value']) < 20:  # Ограничение длины
                                field['value'] += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка мыши
                        mouse_pos = event.pos
                        self._handle_mouse_click(mouse_pos)
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos
                    self._handle_mouse_motion(mouse_pos)
            
            self.draw()
            clock.tick(60)
        
        return self.result
    
    def _handle_mouse_click(self, mouse_pos):
        """Обрабатывает клики мыши"""
        # Проверяем клики по полям ввода
        for field_id, field_data in self.input_fields.items():
            if field_data['rect'].collidepoint(mouse_pos):
                self.active_field = field_id
                break
        else:
            self.active_field = None
        
        # Проверяем клики по кнопкам
        for button_id, button_rect in self.buttons.items():
            if button_rect.collidepoint(mouse_pos):
                if button_id == 'save':
                    self._save_config()
                elif button_id == 'reset':
                    self._reset_config()
                elif button_id == 'cancel':
                    self.running = False
                    return None
                break
    
    def _handle_mouse_motion(self, mouse_pos):
        """Обрабатывает движение мыши для hover эффектов"""
        for button_id, button_rect in self.buttons.items():
            self.button_hover[button_id] = button_rect.collidepoint(mouse_pos)
    
    def _switch_to_next_field(self):
        """Переключает на следующее поле ввода"""
        field_ids = list(self.input_fields.keys())
        if self.active_field:
            current_index = field_ids.index(self.active_field)
            next_index = (current_index + 1) % len(field_ids)
            self.active_field = field_ids[next_index]
        else:
            self.active_field = field_ids[0]
    
    def _save_config(self):
        """Сохраняет конфигурацию бота"""
        try:
            # Валидация и преобразование значений
            config_updates = {}
            
            # Включение бота
            enabled_str = self.input_fields['enabled']['value'].lower()
            if enabled_str in ['true', '1', 'yes', 'да', 'включить']:
                config_updates['enabled'] = True
            elif enabled_str in ['false', '0', 'no', 'нет', 'выключить']:
                config_updates['enabled'] = False
            else:
                raise ValueError("Неверное значение для включения бота")
            
            # Интервал заявок
            interval = int(self.input_fields['order_interval']['value'])
            if not (1 <= interval <= 1000):
                raise ValueError("Интервал должен быть от 1 до 1000")
            config_updates['order_interval'] = interval
            
            # Тип заявок
            order_type = self.input_fields['order_type']['value'].lower()
            if order_type not in ['buy', 'sell', 'random', 'both']:
                raise ValueError("Тип заявок должен быть: buy, sell, random или both")
            config_updates['order_type'] = order_type
            
            # Количество акций
            quantity = int(self.input_fields['quantity']['value'])
            if not (1 <= quantity <= 1000):
                raise ValueError("Количество должно быть от 1 до 1000")
            config_updates['quantity'] = quantity
            
            # Отклонение цены
            price_offset = float(self.input_fields['price_offset']['value'])
            if not (0.001 <= price_offset <= 0.1):
                raise ValueError("Отклонение цены должно быть от 0.001 до 0.1")
            config_updates['price_offset'] = price_offset
            
            # Диапазон цен
            price_range_min = float(self.input_fields['price_range_min']['value'])
            price_range_max = float(self.input_fields['price_range_max']['value'])
            if not (0.5 <= price_range_min <= 1.0):
                raise ValueError("Минимальная цена должна быть от 0.5 до 1.0")
            if not (1.0 <= price_range_max <= 2.0):
                raise ValueError("Максимальная цена должна быть от 1.0 до 2.0")
            if price_range_min >= price_range_max:
                raise ValueError("Минимальная цена должна быть меньше максимальной")
            config_updates['price_range_min'] = price_range_min
            config_updates['price_range_max'] = price_range_max
            
            # Обновляем конфигурацию
            for key, value in config_updates.items():
                setattr(self.bot_config, key, value)
            
            # Вызываем callback если есть
            if self.on_config_changed:
                self.on_config_changed(config_updates)
            
            self.success_message = "✅ Конфигурация сохранена!"
            self.error_message = ""
            
            # Закрываем окно через 1 секунду
            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
            
        except ValueError as e:
            self.error_message = f"❌ Ошибка: {str(e)}"
            self.success_message = ""
        except Exception as e:
            self.error_message = f"❌ Неожиданная ошибка: {str(e)}"
            self.success_message = ""
    
    def _reset_config(self):
        """Сбрасывает конфигурацию к исходным значениям"""
        self.field_values = {
            'enabled': str(self.bot_config.enabled).lower(),
            'order_interval': str(self.bot_config.order_interval),
            'order_type': self.bot_config.order_type,
            'quantity': str(self.bot_config.quantity),
            'price_offset': str(self.bot_config.price_offset),
            'price_range_min': str(self.bot_config.price_range_min),
            'price_range_max': str(self.bot_config.price_range_max)
        }
        
        # Обновляем поля ввода
        for field_id, field_data in self.input_fields.items():
            field_data['value'] = self.field_values[field_id]
        
        self.error_message = ""
        self.success_message = "🔄 Конфигурация сброшена к исходным значениям"
    
    def draw(self):
        """Отрисовывает окно настройки"""
        # Полупрозрачный фон
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Основное окно
        pygame.draw.rect(self.screen, self.bg_color, self.dialog_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.border_color, self.dialog_rect, 3, border_radius=10)
        
        # Заголовок
        title_rect = pygame.Rect(self.x + 20, self.y + 10, self.width - 40, 50)
        pygame.draw.rect(self.screen, (52, 152, 219), title_rect, border_radius=8)
        title_text = self.title_font.render("🤖 НАСТРОЙКА ТОРГОВОГО БОТА", True, self.text_color)
        title_text_rect = title_text.get_rect(center=title_rect.center)
        self.screen.blit(title_text, title_text_rect)
        
        # Поля ввода
        for field_id, field_data in self.input_fields.items():
            # Подпись поля
            label_text = self.text_font.render(field_data['label'] + ":", True, self.text_color)
            self.screen.blit(label_text, (self.x + 20, field_data['label_y']))
            
            # Поле ввода
            input_rect = field_data['rect']
            is_active = (self.active_field == field_id)
            
            # Цвет поля в зависимости от состояния
            if is_active:
                field_color = self.input_active_color
                border_color = self.input_active_color
            else:
                field_color = self.input_bg_color
                border_color = self.input_border_color
            
            pygame.draw.rect(self.screen, field_color, input_rect, border_radius=5)
            pygame.draw.rect(self.screen, border_color, input_rect, 2, border_radius=5)
            
            # Текст в поле
            text_surface = self.input_font.render(field_data['value'], True, self.text_color)
            text_rect = text_surface.get_rect(center=input_rect.center)
            self.screen.blit(text_surface, text_rect)
            
            # Курсор для активного поля
            if is_active:
                current_time = pygame.time.get_ticks()
                if (current_time // 500) % 2:  # Мигает каждые 500мс
                    cursor_x = text_rect.right + 2
                    cursor_y = text_rect.centery
                    pygame.draw.line(self.screen, self.text_color, 
                                   (cursor_x, cursor_y - 8), (cursor_x, cursor_y + 8), 2)
        
        # Кнопки
        button_texts = {
            'save': '💾 СОХРАНИТЬ',
            'reset': '🔄 СБРОС',
            'cancel': '❌ ОТМЕНА'
        }
        
        for button_id, button_rect in self.buttons.items():
            is_hover = self.button_hover[button_id]
            button_color = self.button_hover_color if is_hover else self.button_color
            
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=6)
            pygame.draw.rect(self.screen, self.border_color, button_rect, 2, border_radius=6)
            
            button_text = self.text_font.render(button_texts[button_id], True, self.text_color)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)
        
        # Сообщения об ошибках и успехе
        if self.error_message:
            error_text = self.small_font.render(self.error_message, True, self.error_color)
            self.screen.blit(error_text, (self.x + 20, self.y + 420))
        elif self.success_message:
            success_text = self.small_font.render(self.success_message, True, self.success_color)
            self.screen.blit(success_text, (self.x + 20, self.y + 420))
        
        # Подсказки
        hint_text = self.small_font.render("TAB - переключение полей | ENTER - сохранить | ESC - отмена", True, (150, 150, 150))
        self.screen.blit(hint_text, (self.x + 20, self.y + 450))
        
        pygame.display.flip()

def show_bot_config_window(screen, bot_config: BotConfig, on_config_changed: Callable = None) -> Optional[dict]:
    """Показывает окно настройки бота и возвращает конфигурацию"""
    window = BotConfigWindow(screen, bot_config, on_config_changed)
    return window.run()
