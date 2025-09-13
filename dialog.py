import pygame
import sys
from typing import Optional

class InputDialog:
    """Диалоговое окно для ввода текста"""
    
    def __init__(self, screen, title: str, prompt: str, default_value: str = ""):
        self.screen = screen
        self.title = title
        self.prompt = prompt
        self.input_text = default_value
        self.result = None
        self.running = True
        
        # Размеры окна
        self.width = 400
        self.height = 200
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        # Шрифты
        self.title_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)
        self.input_font = pygame.font.Font(None, 28)
        
        # Цвета
        self.bg_color = (50, 50, 50)
        self.border_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.input_bg_color = (30, 30, 30)
        self.input_border_color = (150, 150, 150)
        self.button_color = (70, 130, 180)
        self.button_hover_color = (100, 150, 200)
        
        # Прямоугольники
        self.dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.input_rect = pygame.Rect(self.x + 20, self.y + 80, self.width - 40, 40)
        self.ok_button_rect = pygame.Rect(self.x + 50, self.y + 140, 100, 40)
        self.cancel_button_rect = pygame.Rect(self.x + 250, self.y + 140, 100, 40)
        
        # Состояние
        self.input_active = True
        self.ok_hover = False
        self.cancel_hover = False
        
    def run(self) -> Optional[str]:
        """Запускает диалог и возвращает введенный текст или None"""
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.result = self.input_text
                        self.running = False
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        if self.input_active:
                            self.input_text = self.input_text[:-1]
                    elif event.unicode.isprintable():
                        if self.input_active and len(self.input_text) < 10:
                            self.input_text += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка мыши
                        mouse_pos = event.pos
                        if self.ok_button_rect.collidepoint(mouse_pos):
                            self.result = self.input_text
                            self.running = False
                        elif self.cancel_button_rect.collidepoint(mouse_pos):
                            self.running = False
                            return None
                        elif self.input_rect.collidepoint(mouse_pos):
                            self.input_active = True
                        else:
                            self.input_active = False
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos
                    self.ok_hover = self.ok_button_rect.collidepoint(mouse_pos)
                    self.cancel_hover = self.cancel_button_rect.collidepoint(mouse_pos)
            
            self.draw()
            clock.tick(60)
        
        return self.result
    
    def draw(self):
        """Отрисовывает диалоговое окно"""
        # Полупрозрачный фон
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Окно диалога
        pygame.draw.rect(self.screen, self.bg_color, self.dialog_rect)
        pygame.draw.rect(self.screen, self.border_color, self.dialog_rect, 2)
        
        # Заголовок
        title_surface = self.title_font.render(self.title, True, self.text_color)
        title_rect = title_surface.get_rect(center=(self.x + self.width // 2, self.y + 30))
        self.screen.blit(title_surface, title_rect)
        
        # Подсказка
        prompt_surface = self.text_font.render(self.prompt, True, self.text_color)
        prompt_rect = prompt_surface.get_rect(center=(self.x + self.width // 2, self.y + 60))
        self.screen.blit(prompt_surface, prompt_rect)
        
        # Поле ввода
        input_color = self.input_border_color if self.input_active else self.input_bg_color
        pygame.draw.rect(self.screen, self.input_bg_color, self.input_rect)
        pygame.draw.rect(self.screen, input_color, self.input_rect, 2)
        
        # Текст в поле ввода
        input_surface = self.input_font.render(self.input_text, True, self.text_color)
        input_text_rect = input_surface.get_rect(center=self.input_rect.center)
        self.screen.blit(input_surface, input_text_rect)
        
        # Курсор (мигающий)
        if self.input_active:
            current_time = pygame.time.get_ticks()
            if (current_time // 500) % 2:  # Мигает каждые 500мс
                cursor_x = input_text_rect.right + 2
                cursor_y = input_text_rect.centery
                pygame.draw.line(self.screen, self.text_color, 
                               (cursor_x, cursor_y - 10), (cursor_x, cursor_y + 10), 2)
        
        # Кнопка OK
        ok_color = self.button_hover_color if self.ok_hover else self.button_color
        pygame.draw.rect(self.screen, ok_color, self.ok_button_rect)
        pygame.draw.rect(self.screen, self.border_color, self.ok_button_rect, 2)
        ok_text = self.text_font.render("OK", True, self.text_color)
        ok_text_rect = ok_text.get_rect(center=self.ok_button_rect.center)
        self.screen.blit(ok_text, ok_text_rect)
        
        # Кнопка Cancel
        cancel_color = self.button_hover_color if self.cancel_hover else self.button_color
        pygame.draw.rect(self.screen, cancel_color, self.cancel_button_rect)
        pygame.draw.rect(self.screen, self.border_color, self.cancel_button_rect, 2)
        cancel_text = self.text_font.render("Cancel", True, self.text_color)
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_button_rect.center)
        self.screen.blit(cancel_text, cancel_text_rect)
        
        pygame.display.flip()

def show_input_dialog(screen, title: str, prompt: str, default_value: str = "") -> Optional[str]:
    """Показывает диалог ввода и возвращает введенный текст"""
    dialog = InputDialog(screen, title, prompt, default_value)
    return dialog.run()

