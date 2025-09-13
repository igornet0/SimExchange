# SimExchange - Модульный Симулятор Биржевого Стакана

## 🚀 Новая Модульная Архитектура v0.2.0

SimExchange теперь использует современную модульную архитектуру с четким разделением ответственности, что делает код более читаемым, тестируемым и масштабируемым.

## 📁 Структура Проекта

```
simexchange/
├── core/                    # Основная бизнес-логика
│   ├── models/              # Модели данных
│   │   ├── order.py         # Ордера и типы ордеров
│   │   ├── trade.py         # Сделки
│   │   ├── agent.py         # Торговые агенты
│   │   ├── market_data.py   # Рыночные данные
│   │   └── simulation_config.py  # Конфигурация симуляции
│   ├── services/            # Бизнес-сервисы
│   │   ├── simulation_service.py    # Управление симуляцией
│   │   ├── order_book_service.py    # Работа со стаканом заявок
│   │   ├── agent_service.py         # Управление агентами
│   │   └── trading_simulator.py     # Основной координатор
│   └── strategies/          # Торговые стратегии (будущее)
├── ui/                      # Пользовательский интерфейс
│   ├── components/          # UI компоненты (будущее)
│   ├── windows/             # Окна приложения (будущее)
│   └── dialogs/             # Диалоговые окна (будущее)
├── config/                  # Конфигурация
│   ├── settings.py          # Менеджер конфигурации
│   └── default_config.yaml  # Конфигурация по умолчанию
├── utils/                   # Утилиты
│   └── performance.py       # Тестирование производительности
├── tests/                   # Тесты
│   ├── unit/                # Unit тесты
│   └── integration/         # Интеграционные тесты
├── main.py                  # Главный файл
└── __main__.py              # Точка входа пакета
```

## 🏗️ Архитектурные Принципы

### 1. **Разделение Ответственности (SRP)**
- Каждый класс имеет одну четко определенную ответственность
- Модели содержат только данные и базовую логику
- Сервисы содержат бизнес-логику
- UI компоненты отвечают только за отображение

### 2. **Инверсия Зависимостей (DIP)**
- Высокоуровневые модули не зависят от низкоуровневых
- Зависимости инжектируются через конструкторы
- Легко заменять реализации для тестирования

### 3. **Открытость/Закрытость (OCP)**
- Код открыт для расширения, закрыт для модификации
- Новые стратегии торговли можно добавлять без изменения существующего кода
- Новые UI компоненты легко интегрируются

### 4. **Единый Интерфейс (ISP)**
- Интерфейсы разделены по функциональности
- Клиенты не зависят от неиспользуемых методов

## 🚀 Быстрый Старт

### Установка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd SimExchange

# Установите зависимости
pip install -r requirements.txt
```

### Запуск

```bash
# Запуск с настройками по умолчанию
python -m simexchange

# Запуск с параметрами
python -m simexchange -a 50 -p 200 -b 15000

# Запуск с пользовательской конфигурацией
python -m simexchange --config my_config.yaml

# Тест производительности
python -m simexchange --performance-test

# Консольный режим
python -m simexchange --no-ui
```

## 📊 Основные Компоненты

### Модели Данных

#### Order (Ордер)
```python
from simexchange.core.models import Order, OrderType

# Создание ордера на покупку
order = Order.create_buy_order(1, 100.0, 10, agent_id=0)

# Создание ордера на продажу
order = Order.create_sell_order(2, 101.0, 5, agent_id=1)
```

#### Trade (Сделка)
```python
from simexchange.core.models import Trade

# Создание сделки из двух ордеров
trade = Trade.create_from_orders(1, buy_order, sell_order, quantity=5)
```

#### Agent (Агент)
```python
from simexchange.core.models import Agent

# Создание агента
agent = Agent(id=0, balance=10000.0, position=0)

# Проверка возможности торговли
if agent.can_buy(100.0, 10):
    # Агент может купить 10 акций по 100
    pass
```

### Сервисы

#### TradingSimulator (Основной Симулятор)
```python
from simexchange.core.services import TradingSimulator
from simexchange.core.models import SimulationConfig

# Создание конфигурации
config = SimulationConfig(
    initial_price=100.0,
    num_agents=20,
    initial_balance=10000.0
)

# Создание симулятора
simulator = TradingSimulator(config)

# Выполнение цикла
trades = simulator.run_cycle()

# Получение данных
data = simulator.get_simulation_data()
```

## ⚙️ Конфигурация

### YAML Конфигурация

```yaml
# config/my_config.yaml
simulation:
  initial_price: 150.0
  num_agents: 50
  initial_balance: 20000.0

performance:
  performance_mode: true
  max_history_size: 2000

agents:
  risk_tolerance_range: [0.2, 0.9]
  trading_frequency_range: [0.05, 0.6]
```

### Программная Конфигурация

```python
from simexchange.config.settings import ConfigManager

# Загрузка конфигурации
config_manager = ConfigManager("my_config.yaml")
config = config_manager.get_simulation_config()

# Обновление конфигурации
config_manager.update_simulation_config(
    initial_price=200.0,
    num_agents=100
)
```

## 🧪 Тестирование

### Запуск Тестов

```bash
# Все тесты
python -m pytest simexchange/tests/

# Конкретный тест
python -m pytest simexchange/tests/test_basic_functionality.py

# С подробным выводом
python -m pytest simexchange/tests/ -v
```

### Тест Производительности

```python
from simexchange.utils.performance import PerformanceTester
from simexchange.core.models import SimulationConfig

config = SimulationConfig(num_agents=100)
tester = PerformanceTester(config)
tester.run_test()
```

## 📈 Производительность

### Режимы Производительности

```python
# Включение режима высокой производительности
simulator.set_performance_mode(True, skip_volatility=True)

# Настройка ограничений истории
config.max_history_size = 500
config.max_trades_history = 1000
```

### Бенчмарки

- **100 агентов, 1000 циклов**: ~50 циклов/сек
- **500 агентов, 1000 циклов**: ~20 циклов/сек
- **1000 агентов, 1000 циклов**: ~10 циклов/сек

## 🔧 Расширение

### Добавление Новых Моделей

```python
# simexchange/core/models/new_model.py
from dataclasses import dataclass

@dataclass
class NewModel:
    field1: str
    field2: int
    
    def __post_init__(self):
        # Валидация
        if self.field2 < 0:
            raise ValueError("field2 must be positive")
```

### Добавление Новых Сервисов

```python
# simexchange/core/services/new_service.py
class NewService:
    def __init__(self, dependency):
        self.dependency = dependency
    
    def do_something(self):
        # Бизнес-логика
        pass
```

## 🐛 Отладка

### Логирование

```python
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# В коде
logger.debug(f"Processing cycle {cycle}")
logger.info(f"Generated {len(trades)} trades")
```

### Профилирование

```python
import cProfile

# Профилирование симуляции
profiler = cProfile.Profile()
profiler.enable()

# Выполнение симуляции
for _ in range(1000):
    simulator.run_cycle()

profiler.disable()
profiler.dump_stats('simulation_profile.prof')
```

## 📚 API Документация

### Основные Классы

- `TradingSimulator`: Главный класс симулятора
- `SimulationConfig`: Конфигурация симуляции
- `Order`: Ордер на покупку/продажу
- `Trade`: Сделка между агентами
- `Agent`: Торговый агент
- `MarketData`: Рыночные данные

### Основные Методы

- `simulator.run_cycle()`: Выполнить один цикл симуляции
- `simulator.get_simulation_data()`: Получить данные для отображения
- `simulator.reset()`: Сбросить симуляцию
- `agent.can_buy(price, quantity)`: Проверить возможность покупки
- `order.can_match_with(other_order)`: Проверить совместимость ордеров

## 🤝 Вклад в Проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

## 🆘 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте документацию
2. Запустите тесты
3. Создайте Issue в GitHub
4. Обратитесь к команде разработки

---

**SimExchange v0.2.0** - Модульная архитектура для симуляции торговли
