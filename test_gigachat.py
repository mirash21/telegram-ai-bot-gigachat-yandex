"""Тестовый скрипт для проверки работы с GigaChat API"""
import os
from dotenv import load_dotenv
from gigachat_client import GigaChatClient

load_dotenv()


def test_gigachat():
    """Тест основных функций GigaChat"""
    
    # Инициализация клиента
    print("🔧 Инициализация клиента GigaChat...")

    # Формируем credentials: можно передать Base64 от client_id:client_secret
    # Или готовый ключ авторизации из личного кабинета
    client_id = os.getenv("GIGACHAT_CLIENT_ID")
    client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
    credentials = os.getenv("GIGACHAT_CREDENTIALS")  # Готовый ключ из ЛК

    if credentials:
        # Используем готовый ключ авторизации
        client = GigaChatClient(
            credentials=credentials,
            scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
        )
    elif client_id and client_secret:
        # Формируем credentials из client_id и client_secret
        import base64
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        client = GigaChatClient(
            credentials=credentials,
            scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
        )
    else:
        raise ValueError("Не заданы GIGACHAT_CREDENTIALS или GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET")
    
    # Тест 1: Получение списка моделей
    print("\n📋 Тест 1: Получение списка моделей...")
    try:
        models = client.get_models()
        print(f"✅ Получено {len(models.get('data', []))} моделей:")
        for model in models.get("data", []):
            print(f"   • {model.get('id')} ({model.get('type')})")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: Простой чат
    print("\n💬 Тест 2: Отправка сообщения...")
    try:
        response = client.chat_simple("Привет! Расскажи о себе в двух словах.")
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
        response = client.chat(messages=messages)
        print(f"✅ Ответ: {response['choices'][0]['message']['content']}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 4: Подсчёт токенов
    print("\n🔢 Тест 4: Подсчёт токенов...")
    try:
        texts = ["Привет мир!", "Как дела?"]
        counts = client.tokens_count(texts=texts)
        print("✅ Результат подсчёта:")
        for item in counts:
            print(f"   • {item.get('characters')} символов = {item.get('tokens')} токенов")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 5: Эмбеддинги
    print("\n🧠 Тест 5: Создание эмбеддингов...")
    try:
        embeddings = client.embeddings(input_text=["Привет мир"])
        vector = embeddings["data"][0]["embedding"]
        print(f"✅ Размерность эмбеддинга: {len(vector)}")
        print(f"   Первые 5 значений: {vector[:5]}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 6: Баланс (если есть пакеты токенов)
    print("\n💰 Тест 6: Проверка баланса...")
    try:
        balance = client.get_balance()
        print("✅ Баланс:")
        for item in balance.get("balance", []):
            print(f"   • {item.get('usage')}: {item.get('value')} токенов")
    except Exception as e:
        print(f"ℹ️ Баланс недоступен (функция только для пакетов токенов): {e}")
    
    print("\n✨ Все тесты завершены!")


if __name__ == "__main__":
    test_gigachat()
