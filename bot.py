"""
Telegram Bot с интеграцией GigaChat и YandexGPT API
"""
import os
import sys
import base64
import logging
from dotenv import load_dotenv

# Устанавливаем UTF-8
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from gigachat_client import GigaChatClient
from yandex_client import YandexGPTClient

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


# Доступные провайдеры
PROVIDERS = {
    "gigachat": "GigaChat (Сбербанк)",
    "yandex": "YandexGPT (Яндекс)"
}


def _get_gigachat_credentials() -> str:
    """Получает credentials для GigaChat из переменных окружения"""
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    if credentials:
        return credentials

    client_id = os.getenv("GIGACHAT_CLIENT_ID")
    client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
    if client_id and client_secret:
        return base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    return None


class MultiProviderBot:
    """Telegram Bot с поддержкой нескольких AI-провайдеров"""

    @staticmethod
    def _format_message(text: str) -> str:
        """Форматирует ответ для Telegram (MarkdownV2)"""
        # Экранируем спецсимволы для MarkdownV2
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        text = ''.join(f'\\{c}' if c in escape_chars else c for c in text)

        # Восстанавливаем базовое форматирование (если есть в тексте)
        # Эти замены нужно делать аккуратно
        text = text.replace('\\*\\*', '**')  # Жирный
        text = text.replace('\\*', '*')  # Курсив

        return text

    def __init__(self):
        # Инициализация клиентов
        self.giga_client = None
        self.yandex_client = None

        # GigaChat
        giga_credentials = _get_gigachat_credentials()
        if giga_credentials:
            try:
                self.giga_client = GigaChatClient(
                    credentials=giga_credentials,
                    scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
                )
                logger.info("GigaChat клиент инициализирован")
            except Exception as e:
                logger.warning(f"Не удалось инициализировать GigaChat: {e}")

        # YandexGPT
        yandex_folder = os.getenv("YANDEX_FOLDER_ID")
        if yandex_folder and (os.getenv("YANDEX_API_KEY") or os.getenv("YANDEX_OAUTH_TOKEN")):
            try:
                self.yandex_client = YandexGPTClient(
                    folder_id=yandex_folder,
                    api_key=os.getenv("YANDEX_API_KEY"),
                    oauth_token=os.getenv("YANDEX_OAUTH_TOKEN")
                )
                logger.info("YandexGPT клиент инициализирован")
            except Exception as e:
                logger.warning(f"Не удалось инициализировать YandexGPT: {e}")

        if not self.giga_client and not self.yandex_client:
            raise ValueError(
                "Не настроен ни один AI-провайдер! "
                "Добавьте GIGACHAT_CREDENTIALS или YANDEX_FOLDER_ID + YANDEX_API_KEY"
            )

        # Хранилище: {user_id: {"provider": str, "model": str, "history": [messages]}}
        self.user_data: dict = {}

    def _get_user_provider(self, user_id: int) -> str:
        """Получает текущего провайдера пользователя"""
        if user_id not in self.user_data:
            # По умолчанию используем первый доступный
            self.user_data[user_id] = {
                "provider": "gigachat" if self.giga_client else "yandex",
                "model": "yandexgpt-lite",
                "history": []
            }
        return self.user_data[user_id]["provider"]

    def _get_user_model(self, user_id: int) -> str:
        """Получает текущую модель пользователя"""
        if user_id not in self.user_data:
            self._get_user_provider(user_id)  # Создаёт запись
        return self.user_data[user_id].get("model", "yandexgpt-lite")

    def _set_user_provider(self, user_id: int, provider: str):
        """Устанавливает провайдера для пользователя"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {"provider": provider, "model": "yandexgpt-lite", "history": []}
        else:
            self.user_data[user_id]["provider"] = provider
            if provider == "yandex":
                self.user_data[user_id]["model"] = self.user_data[user_id].get("model", "yandexgpt-lite")

    def _get_client(self, provider: str):
        """Возвращает клиент по имени провайдера"""
        if provider == "gigachat":
            return self.giga_client
        elif provider == "yandex":
            return self.yandex_client
        raise ValueError(f"Неизвестный провайдер: {provider}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user = update.effective_user

        # Проверяем доступные провайдеры
        available_providers = []
        if self.giga_client:
            available_providers.append("gigachat")
        if self.yandex_client:
            available_providers.append("yandex")

        # Устанавливаем провайдер по умолчанию
        default_provider = available_providers[0] if available_providers else None
        if default_provider:
            self._set_user_provider(user.id, default_provider)

        keyboard = self._provider_keyboard(user.id)
        await update.message.reply_html(
            f"Привет, {user.mention_html()}!\n\n"
            f"Текущий провайдер: {PROVIDERS.get(self._get_user_provider(user.id), 'Не выбран')}\n"
            "Напишите сообщение, и я отвечу.\n\n"
            "<b>Команды:</b>\n"
            "/start - Начать работу\n"
            "/help - Справка\n"
            "/clear - Очистить историю\n"
            "/provider - Выбрать AI-провайдера\n"
            "/models - Доступные модели\n"
            "/balance - Проверить баланс",
            reply_markup=keyboard
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        user_id = update.effective_user.id
        current_provider = self._get_user_provider(user_id)

        help_text = (
            f"<b>Справка по боту:</b>\n\n"
            f"Текущий провайдер: {PROVIDERS.get(current_provider, 'Не выбран')}\n\n"
            "Отправьте любое сообщение для диалога с AI.\n\n"
            "<b>Команды:</b>\n"
            "/start - Приветствие\n"
            "/help - Эта справка\n"
            "/clear - Очистить историю\n"
            "/provider - Выбрать AI-провайдера\n"
            "/models - Список моделей\n"
            "/balance - Проверить баланс"
        )
        await update.message.reply_html(help_text)

    def _provider_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        """Создаёт клавиатуру выбора провайдера"""
        buttons = []
        if self.giga_client:
            is_active = self._get_user_provider(user_id) == "gigachat"
            icon = "✅" if is_active else "⚪"
            buttons.append([
                InlineKeyboardButton(f"{icon} GigaChat", callback_data="provider_gigachat")
            ])
        if self.yandex_client:
            is_active = self._get_user_provider(user_id) == "yandex"
            icon = "✅" if is_active else "⚪"
            buttons.append([
                InlineKeyboardButton(f"{icon} YandexGPT", callback_data="provider_yandex")
            ])
        return InlineKeyboardMarkup(buttons)

    async def show_provider_select(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает меню выбора провайдера"""
        user_id = update.effective_user.id
        keyboard = self._provider_keyboard(user_id)
        await update.message.reply_text(
            "Выберите AI-провайдера:",
            reply_markup=keyboard
        )

    async def provider_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора провайдера через inline-кнопки"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        data = query.data

        if data.startswith("provider_"):
            provider = data.split("_")[1]
            self._set_user_provider(user_id, provider)

            # Обновляем историю (очищаем при смене провайдера)
            self.user_data[user_id]["history"] = []
            if provider == "yandex":
                self.user_data[user_id]["model"] = "yandexgpt-lite"

            keyboard = self._provider_keyboard(user_id)
            provider_name = PROVIDERS.get(provider, provider)

            try:
                await query.edit_message_text(
                    f"✅ Выбран провайдер: {provider_name}",
                    reply_markup=keyboard
                )
            except Exception:
                pass

    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Очистить историю диалога"""
        user_id = update.effective_user.id
        if user_id in self.user_data:
            self.user_data[user_id]["history"] = []
        await update.message.reply_text("История диалога очищена.")

    async def show_models(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список доступных моделей"""
        user_id = update.effective_user.id
        provider = self._get_user_provider(user_id)
        client = self._get_client(provider)

        if not client:
            await update.message.reply_text("Провайдер не настроен")
            return

        try:
            if provider == "gigachat":
                models = client.get_models()
                text = "<b>Модели GigaChat:</b>\n\n"
                for model in models.get("data", []):
                    model_id = model.get("id", "Unknown")
                    model_type = model.get("type", "Unknown")
                    text += f"• {model_id} ({model_type})\n"
            else:  # yandex
                models = client.get_available_models()
                text = "<b>Модели YandexGPT:</b>\n\n"
                for model in models:
                    text += f"• {model}\n"

            await update.message.reply_html(text)
        except Exception as e:
            logger.error(f"Ошибка получения моделей: {e}")
            await update.message.reply_text("Ошибка при получении списка моделей.")

    async def show_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать баланс токенов"""
        user_id = update.effective_user.id
        provider = self._get_user_provider(user_id)
        client = self._get_client(provider)

        if not client:
            await update.message.reply_text("Провайдер не настроен")
            return

        if provider == "gigachat":
            try:
                balance = client.get_balance()
                text = "<b>Баланс GigaChat:</b>\n\n"
                for item in balance.get("balance", []):
                    model_name = item.get("usage", "Unknown")
                    tokens = item.get("value", 0)
                    text += f"{model_name}: {tokens} токенов\n"
                await update.message.reply_html(text)
            except Exception as e:
                logger.error(f"Ошибка получения баланса: {e}")
                await update.message.reply_text("Не удалось получить баланс.")
        else:
            await update.message.reply_text("Баланс недоступен для YandexGPT (оплачивается по тарифам).")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        user_message = update.message.text

        if not user_message:
            return

        await update.message.chat.send_action("typing")

        try:
            # Получаем или создаём данные пользователя
            if user_id not in self.user_data:
                self.user_data[user_id] = {
                    "provider": "gigachat" if self.giga_client else "yandex",
                    "model": "yandexgpt-lite",
                    "history": []
                }

            # Добавляем сообщение в историю
            self.user_data[user_id]["history"].append({
                "role": "user",
                "content": user_message
            })

            # Ограничиваем историю
            history = self.user_data[user_id]["history"][-20:]

            # Получаем текущего провайдера и клиент
            provider = self._get_user_provider(user_id)
            client = self._get_client(provider)

            if not client:
                await update.message.reply_text("AI-провайдер не настроен. Используйте /provider")
                return

            # Отправляем запрос
            if provider == "yandex":
                model_name = self._get_user_model(user_id)
                response = client.chat(messages=history, model=model_name)
            else:
                response = client.chat(messages=history)
            assistant_message = response["choices"][0]["message"]["content"]

            # Добавляем ответ в историю
            self.user_data[user_id]["history"].append({
                "role": "assistant",
                "content": assistant_message
            })

            # Форматируем и отправляем
            formatted_message = self._format_message(assistant_message)
            keyboard = self._provider_keyboard(user_id)
            await update.message.reply_text(
                formatted_message,
                parse_mode='MarkdownV2',
                reply_markup=keyboard
            )

        except Exception as e:
            import traceback
            logger.error(f"Ошибка обработки сообщения: {e}")
            logger.error(f"Трассировка ошибки:\n{traceback.format_exc()}")
            await update.message.reply_text(
                "Произошла ошибка при обработке запроса. Попробуйте позже."
            )

    def run(self):
        """Запуск бота"""
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")

        # Строим application с увеличенными таймаутами
        application = Application.builder()
        application = application.token(bot_token)
        
        # Увеличиваем таймауты для стабильности
        application = application.read_timeout(60).connect_timeout(60).write_timeout(60)
        
        application = application.build()

        # Обработчики команд
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("clear", self.clear_history))
        application.add_handler(CommandHandler("provider", self.show_provider_select))
        application.add_handler(CommandHandler("models", self.show_models))
        application.add_handler(CommandHandler("balance", self.show_balance))

        # Обработчик inline-кнопок
        application.add_handler(CallbackQueryHandler(self.provider_callback, pattern="^provider_"))

        # Обработчик текстовых сообщений
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        logger.info("Бот запущен...")
        application.run_polling()


def main():
    """Точка входа"""
    bot = None
    try:
        bot = MultiProviderBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise
    finally:
        if bot:
            logger.info("Завершение работы...")


if __name__ == "__main__":
    main()
