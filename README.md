# 🤖 Telegram AI Bot: GigaChat + YandexGPT

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue)](https://telegram.org/)
[![GigaChat](https://img.shields.io/badge/GigaChat-API-green)](https://developers.sber.ru/)
[![YandexGPT](https://img.shields.io/badge/YandexGPT-API-red)](https://cloud.yandex.ru/)

**Многофункциональный Telegram-бот с поддержкой двух AI-провайдеров: GigaChat (Сбербанк) и YandexGPT (Яндекс)**

---

## 📋 Содержание

- [О проекте](#-о-проекте)
- [Возможности](#-возможности)
- [Быстрый старт](#-быстрый-старт)
- [Установка](#-установка)
- [Настройка](#-настройка)
- [Использование](#-использование)
- [Тестирование](#-тестирование)
- [API Клиентов](#-api-клиентов)
- [Структура проекта](#-структура-проекта)
- [Получение ключей](#-получение-ключей)
- [Troubleshooting](#-troubleshooting)
- [Лицензия](#-лицензия)

---

## 🎯 О проекте

Этот Telegram-бот предоставляет удобный интерфейс для работы с двумя популярными российскими AI-моделями:
- **GigaChat** от Сбербанка - передовая языковая модель
- **YandexGPT** от Яндекса - мощная модель для генерации текста

Бот поддерживает переключение между провайдерами, хранение истории диалогов и множество полезных команд.

---

## ✨ Возможности

### 🔹 Основные функции
- ✅ **Два AI-провайдера**: GigaChat и YandexGPT
- ✅ **Переключение на лету**: Выбор провайдера через inline-кнопки
- ✅ **История диалога**: Сохранение контекста беседы (до 20 сообщений)
- ✅ **Поддержка команд**: Полный набор команд для управления
- ✅ **Форматирование**: MarkdownV2 для красивых ответов

### 🔹 Доступные команды
| Команда | Описание |
|---------|----------|
| `/start` | Начать работу с ботом |
| `/help` | Справка по командам |
| `/clear` | Очистить историю диалога |
| `/provider` | Выбрать AI-провайдера |
| `/models` | Показать доступные модели |
| `/balance` | Проверить баланс токенов (GigaChat) |

### 🔹 Поддерживаемые модели
**GigaChat:**
- `GigaChat` - базовая модель
- `GigaChat-Pro` - продвинутая модель
- `GigaChat-2` - вторая версия
- `Embeddings` - векторные представления
- `EmbeddingsGigaR` - продвинутые эмбеддинги

**YandexGPT:**
- `yandexgpt-lite` - лёгкая версия
- `yandexgpt-pro` - профессиональная
- `yandexgpt` - полная версия
- `gpt-35-turbo` - альтернативная модель

---

## 🚀 Быстрый старт

```bash
# Клонирование репозитория
git clone https://github.com/mirash21/telegram-ai-bot-gigachat-yandex.git
cd telegram-ai-bot-gigachat-yandex

# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
.\venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env и добавьте ваши API ключи

# Запуск бота
python bot.py
```

---

## 📦 Установка

### Требования
- Python 3.9 или выше
- Токен Telegram бота
- Учётная запись GigaChat (обязательно)
- Учётная запись Yandex Cloud (опционально)

### Шаг 1: Клонирование
```bash
git clone https://github.com/mirash21/telegram-ai-bot-gigachat-yandex.git
cd telegram-ai-bot-gigachat-yandex
```

### Шаг 2: Виртуальное окружение
```bash
# Создание
python -m venv venv

# Активация Windows
.\venv\Scripts\activate

# Активация macOS/Linux
source venv/bin/activate
```

### Шаг 3: Установка зависимостей
```bash
pip install -r requirements.txt
```

---

## ⚙️ Настройка

### Файл .env

Скопируйте файл с примером конфигурации:
```bash
cp .env.example .env
```

Отредактируйте `.env` и добавьте ваши ключи:

```env
# === GigaChat API (Обязательно) ===
# Вариант 1: Готовый ключ авторизации из личного кабинета
GIGACHAT_CREDENTIALS=MDE5YjZmNTkt...your_key_here

# Вариант 2: Client ID и Client Secret (будут сконвертированы)
# GIGACHAT_CLIENT_ID=your_client_id
# GIGACHAT_CLIENT_SECRET=your_client_secret

# Область доступа: GIGACHAT_API_PERS (физ.лица), GIGACHAT_API_B2B, GIGACHAT_API_CORP
GIGACHAT_SCOPE=GIGACHAT_API_PERS

# === Yandex Cloud API (Опционально) ===
YANDEX_FOLDER_ID=b1g...your_folder_id
YANDEX_API_KEY=AQVN...your_api_key
# Или OAuth токен:
# YANDEX_OAUTH_TOKEN=t1...your_oauth_token

# === Telegram Bot ===
TELEGRAM_BOT_TOKEN=1234567890:AABBccDDeeFFggHHiiJJkkLLmmNNooP
```

### Получение токенов

#### Telegram Bot Token
1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

#### GigaChat Credentials
1. Перейдите на [developers.sber.ru](https://developers.sber.ru/)
2. Авторизуйтесь через Сбербанк ID
3. Создайте проект в разделе GigaChat API
4. Получите Client ID и Client Secret или готовый ключ

#### Yandex Cloud API Key
1. Войдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
2. Создайте сервисный аккаунт с ролью `ai.languageModels.user`
3. Создайте API ключ
4. Узнайте Folder ID вашего каталога

---

## 📖 Использование

### Запуск бота
```bash
# Активация виртуального окружения
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Запуск
python bot.py
```

### Основные команды

**Начало работы:**
```
/start - Приветствие и информация о боте
/help - Справка по всем командам
```

**Управление:**
```
/clear - Очистка истории диалога
/provider - Выбор AI-провайдера (кнопки)
```

**Информация:**
```
/models - Список доступных моделей
/balance - Баланс токенов (только GigaChat)
```

### Переключение провайдеров

Используйте команду `/provider` или inline-кнопки для переключения между:
- **GigaChat** (Сбербанк)
- **YandexGPT** (Яндекс)

⚠️ **Важно:** При смене провайдера история диалога очищается!

---

## 🧪 Тестирование

### Тестирование GigaChat
```bash
python test_gigachat.py
```

**Что проверяется:**
- ✅ Получение списка моделей
- ✅ Простой чат
- ✅ Чат с историей
- ✅ Подсчёт токенов
- ✅ Создание эмбеддингов
- ✅ Проверка баланса

### Тестирование YandexGPT
```bash
python test_yandex.py
```

**Что проверяется:**
- ✅ Создание клиента
- ✅ Генерация ответов

---

## 🔧 API Клиентов

### GigaChat Client

```python
from gigachat_client import GigaChatClient

# Инициализация
client = GigaChatClient(
    credentials="your_credentials",
    scope="GIGACHAT_API_PERS"
)

# Простой запрос
response = client.chat_simple("Привет!")
print(response)

# Диалог с историей
messages = [
    {"role": "user", "content": "Какая столица России?"},
    {"role": "assistant", "content": "Москва"},
    {"role": "user", "content": "Население?"}
]
response = client.chat(messages=messages)

# Эмбеддинги
embeddings = client.embeddings(["Привет мир"])

# Подсчёт токенов
tokens = client.tokens_count(["Текст для подсчёта"])

# Баланс
balance = client.get_balance()
```

### YandexGPT Client

```python
from yandex_client import YandexGPTClient

# Инициализация
client = YandexGPTClient(
    folder_id="b1g...",
    api_key="AQVN..."
)

# Запрос
response = client.chat(
    messages=[{"role": "user", "content": "Привет!"}],
    model="yandexgpt-lite"
)
print(response["choices"][0]["message"]["content"])
```

---

## 📁 Структура проекта

```
telegram-ai-bot-gigachat-yandex/
├── .env.example              # Пример конфигурации
├── .gitignore               # Git ignore файл
├── bot.py                   # Основной файл бота
├── gigachat_client.py       # Клиент GigaChat API
├── yandex_client.py         # Клиент YandexGPT API
├── test_gigachat.py         # Тесты GigaChat
├── test_yandex.py           # Тесты YandexGPT
├── requirements.txt         # Зависимости Python
├── README.md               # Документация
└── LICENSE                 # Лицензия
```

---

## 🔑 Получение ключей

### GigaChat для физических лиц

1. Перейдите на [developers.sber.ru](https://developers.sber.ru/)
2. Авторизуйтесь через Сбербанк ID
3. Создайте новый проект в разделе GigaChat API
4. Получите Client ID и Client Secret
5. Сконвертируйте в Base64: `echo -n "client_id:client_secret" | base64`

### GigaChat для ИП и юридических лиц

1. Подключите платный пакет (B2B или CORP)
2. Получите ключи в личном кабинете
3. Используйте готовый ключ авторизации

### Yandex Cloud

1. Войдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
2. Создайте сервисный аккаунт
3. Назначьте роль `ai.languageModels.user`
4. Создайте API ключ
5. Получите Folder ID каталога

---

## ⚠️ Troubleshooting

### Ошибка подключения к Telegram API

**Симптомы:** `telegram.error.TimedOut`

**Решения:**
1. Проверьте соединение с интернетом
2. Попробуйте использовать VPN
3. Измените DNS на Google DNS (8.8.8.8, 8.8.4.4)
4. Увеличьте таймауты в коде (уже установлено 60 сек)

### Ошибка аутентификации GigaChat

**Симптомы:** `401 Unauthorized`

**Решения:**
1. Проверьте правильность credentials
2. Убедитесь, что срок действия токена не истёк (30 минут)
3. Проверьте scope доступа

### Модели возвращают None

**Симптомы:** В списке моделей все значения `None`

**Решения:**
1. Обновите библиотеку: `pip install --upgrade gigachat`
2. Проверьте версию API в документации

---

## 📄 Лицензия

Этот проект распространяется под лицензией **MIT License**.

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🔗 Полезные ссылки

- [Документация GigaChat API](https://developers.sber.ru/docs/files/openapi/gigachat/api.yml)
- [Документация YandexGPT](https://cloud.yandex.ru/docs/yandexgpt/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Python-telegram-bot документация](https://docs.python-telegram-bot.org/)

---

## 💡 Примеры использования

### Пример 1: Простой вопрос
```
Вы: Какая столица Франции?
Бот: Столица Франции — Париж. Это один из самых посещаемых городов мира...
```

### Пример 2: Диалог с контекстом
```
Вы: Расскажи о Пушкине
Бот: Александр Сергеевич Пушкин — великий русский поэт...

Вы: Когда он родился?
Бот: Александр Сергеевич Пушкин родился 6 июня (26 мая по старому стилю) 1799 года...
```

### Пример 3: Переключение провайдера
```
Вы: /provider
[Нажимаете кнопку YandexGPT]
Бот: ✅ Выбран провайдер: YandexGPT (Яндекс)
```

---

## 🤝 Вклад в проект

Приветствуются pull request'ы и issues! Не стесняйтесь сообщать об ошибках или предлагать улучшения.

---

## 📞 Контакты

Если у вас возникли вопросы или предложения:
- Создайте [Issue](https://github.com/mirash21/telegram-ai-bot-gigachat-yandex/issues)
- Напишите в Telegram (если доступно)

---

**Made with ❤️ using GigaChat and YandexGPT**
