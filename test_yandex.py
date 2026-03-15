"""Тестовый скрипт для проверки работы с YandexGPT API"""
import os
from dotenv import load_dotenv
from yandex_client import YandexGPTClient

load_dotenv()


def test_yandex():
    """Тест основных функций YandexGPT"""
    
    # Инициализация клиента
    print("🔧 Инициализация клиента YandexGPT...")

    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("YANDEX_API_KEY")
    oauth_token = os.getenv("YANDEX_OAUTH_TOKEN")

    if not folder_id:
        print("❌ YANDEX_FOLDER_ID не задан. Пропускаем тесты YandexGPT.")
        return

    try:
        client = YandexGPTClient(
            folder_id=folder_id,
            api_key=api_key,
            oauth_token=oauth_token
        )
        print("✅ Клиент YandexGPT успешно инициализирован")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return
    
    # Тест 1: Получение списка моделей
    print("\n📋 Тест 1: Доступные модели...")
    try:
        models = client.get_available_models()
        print(f"✅ Доступно {len(models)} моделей:")
        for model in models:
            print(f"   • {model}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: Простой чат
    print("\n💬 Тест 2: Отправка сообщения...")
    try:
        response = client.chat_simple("Привет! Расскажи о себе в двух словах.", model="yandexgpt-lite")
        print(f"✅ Ответ модели: {response}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 3: Чат с историей
    print("\n📝 Тест 3: Диалог с историей...")
    try:
        messages = [
            {"role": "system", "content": "Ты — полезный ассистент."},
            {"role": "user", "content": "Какая столица России?"},
            {"role": "assistant", "content": "Столица России — Москва."},
            {"role": "user", "content": "А какое население?"}
        ]
        response = client.chat(messages=messages, model="yandexgpt-lite")
        print(f"✅ Ответ: {response['choices'][0]['message']['content']}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n✨ Все тесты завершены!")


if __name__ == "__main__":
    test_yandex()
