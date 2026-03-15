# 🤖 Telegram AI Bot: GigaChat + YandexGPT

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue)](https://telegram.org/)
[![GigaChat](https://img.shields.io/badge/GigaChat-API-green)](https://developers.sber.ru/)
[![YandexGPT](https://img.shields.io/badge/YandexGPT-API-red)](https://cloud.yandex.ru/)

**Многофункциональный Telegram-бот с поддержкой двух AI-провайдеров: GigaChat (Сбербанк) и YandexGPT (Яндекс)**

## ✨ Возможности

- 🔹 **Два AI-провайдера**: GigaChat и YandexGPT
- 🔹 **Переключение на лету**: Выбор провайдера через inline-кнопки
- 🔹 **История диалога**: Сохранение контекста (до 20 сообщений)
- 🔹 **Поддержка команд**: /start, /help, /clear, /provider, /models, /balance
- 🔹 **Форматирование**: MarkdownV2 для красивых ответов

## 🚀 Быстрый старт

```bash
git clone https://github.com/mirash21/telegram-ai-bot-gigachat-yandex.git
cd telegram-ai-bot-gigachat-yandex
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env
python bot.py
```

## 📖 Документация

Полная документация доступна в файле [README.md](README.md)

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

---

**Made with ❤️ using GigaChat and YandexGPT**
