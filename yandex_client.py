"""
Клиент для работы с YandexGPT API через Yandex Cloud SDK
Документация: https://cloud.yandex.ru/docs/yandexgpt/
"""
import os
import json
import logging
import sys
from typing import Optional, List, Dict, Any

try:
    # Пробуем использовать yandexcloud SDK
    from yandex.cloud import sdk
    from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Функция для очистки заголовков от не-ASCII символов
def _sanitize_headers(headers: dict) -> dict:
    """Очищает заголовки от не-ASCII символов для совместимости с HTTP"""
    safe_headers = {}
    for key, value in headers.items():
        # Ключи заголовков должны быть ASCII
        if isinstance(key, str):
            try:
                key.encode('ascii')
            except UnicodeEncodeError:
                logger.warning(f"Заголовок с не-ASCII ключом: {key}")
                key = key.encode('ascii', 'ignore').decode('ascii')
        # Значения заголовков тоже должны быть ASCII
        if isinstance(value, str):
            try:
                value.encode('ascii')
            except UnicodeEncodeError:
                logger.warning(f"Заголовок '{key}' содержит не-ASCII символы, очищаем")
                # Для Authorization заголовка не очищаем, так как это может сломать токен
                if key.lower() == "authorization":
                    # Пробуем найти проблемные символы и заменить их
                    # Но обычно в Authorization не должно быть не-ASCII
                    logger.error(f"В заголовке Authorization обнаружены не-ASCII символы!")
                    value = value.encode('ascii', 'ignore').decode('ascii')
                else:
                    value = value.encode('ascii', 'ignore').decode('ascii')
        safe_headers[key] = value
    return safe_headers

# Исправляем проблему с кодировкой заголовков в urllib3 на Windows
# Патчим метод putheader для правильной работы с UTF-8
if sys.platform == 'win32':
    try:
        import urllib3.connection
        _original_putheader = urllib3.connection.HTTPConnection.putheader
        
        def _putheader_utf8(self, header, *values):
            """Переопределённый метод putheader с поддержкой UTF-8"""
            # Убеждаемся, что все значения заголовков содержат только ASCII символы
            safe_values = []
            for value in values:
                if isinstance(value, str):
                    try:
                        # Пробуем закодировать в ASCII
                        value.encode('ascii')
                        safe_values.append(value)
                    except UnicodeEncodeError:
                        # Если содержит не-ASCII, кодируем в UTF-8 и используем RFC 2047 encoding
                        import email.header
                        encoded_value = email.header.Header(value, 'utf-8').encode()
                        safe_values.append(encoded_value)
                else:
                    safe_values.append(value)
            return _original_putheader(self, header, *safe_values)
        
        urllib3.connection.HTTPConnection.putheader = _putheader_utf8
        logger.debug("Патч для urllib3.putheader применён")
    except Exception as e:
        logger.warning(f"Не удалось применить патч для urllib3: {e}")


class YandexGPTClient:
    """Клиент для работы с YandexGPT API через Yandex Cloud SDK"""

    def __init__(
        self,
        folder_id: Optional[str] = None,
        api_key: Optional[str] = None,
        oauth_token: Optional[str] = None
    ):
        """
        Инициализация клиента YandexGPT

        Args:
            folder_id: ID папки в Yandex Cloud
            api_key: API ключ сервисного аккаунта
            oauth_token: OAuth токен (вместо api_key)
        """
        folder_id = folder_id or os.getenv("YANDEX_FOLDER_ID")
        api_key = api_key or os.getenv("YANDEX_API_KEY")
        oauth_token = oauth_token or os.getenv("YANDEX_OAUTH_TOKEN")

        if not folder_id:
            raise ValueError("Не задан YANDEX_FOLDER_ID")
        if not api_key and not oauth_token:
            raise ValueError("Не задан YANDEX_API_KEY или YANDEX_OAUTH_TOKEN")

        self.folder_id = folder_id
        self.api_key = api_key
        self.oauth_token = oauth_token
        
        # Создаём сессию requests с правильной настройкой
        self.session = requests.Session()
        # Настраиваем retry стратегию
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_iam_token(self) -> str:
        """Получает IAM токен из OAuth токена через Yandex Cloud API"""
        if not self.oauth_token:
            return None
            
        url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        payload = {"yandexPassportOauthToken": self.oauth_token}
        
        # Убеждаемся, что заголовки содержат только ASCII символы
        headers = {"Content-Type": "application/json"}
        headers = _sanitize_headers(headers)
        
        # Используем json параметр, который автоматически правильно обрабатывает UTF-8
        response = self.session.post(
            url,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()["iamToken"]

    def _get_auth_header(self) -> str:
        """Получает заголовок авторизации"""
        if self.api_key:
            # Убеждаемся, что API ключ содержит только ASCII символы
            auth_value = f"Api-Key {self.api_key}"
            try:
                auth_value.encode('ascii')
                return auth_value
            except UnicodeEncodeError:
                # Если содержит не-ASCII, заменяем на безопасный вариант
                safe_key = self.api_key.encode('ascii', 'ignore').decode('ascii')
                return f"Api-Key {safe_key}"
        else:
            iam_token = self._get_iam_token()
            # Убеждаемся, что IAM токен содержит только ASCII символы
            auth_value = f"Bearer {iam_token}"
            try:
                auth_value.encode('ascii')
                return auth_value
            except UnicodeEncodeError:
                # Если содержит не-ASCII, заменяем на безопасный вариант
                safe_token = iam_token.encode('ascii', 'ignore').decode('ascii')
                return f"Bearer {safe_token}"

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Конвертирует сообщения в формат YandexGPT"""
        converted = []
        for msg in messages:
            role_map = {
                "system": "system",
                "user": "user",
                "assistant": "assistant"
            }
            converted.append({
                "role": role_map.get(msg.get("role", "user"), "user"),
                "text": msg.get("content", "")
            })
        return converted

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.6,
        max_tokens: Optional[int] = 2000,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Сгенерировать ответ модели

        Args:
            messages: Массив сообщений (role, content)
            model: Название модели (yandexgpt-lite, yandexgpt-pro, yandexgpt, gpt-35-turbo)
            temperature: Температура выборки (0-1)
            max_tokens: Максимальное количество токенов
            stream: Потоковый режим

        Returns:
            Ответ модели
        """
        model_name = model or "yandexgpt-lite"
        model_uri = f"gpt://{self.folder_id}/{model_name}"

        # Формируем completionOptions
        completion_options = {
            "stream": stream,
            "temperature": temperature
        }
        # Добавляем maxTokens только если он указан
        if max_tokens is not None:
            completion_options["maxTokens"] = max_tokens
        
        payload = {
            "modelUri": model_uri,
            "completionOptions": completion_options,
            "messages": self._convert_messages(messages)
        }

        # Формируем заголовки
        auth_header = self._get_auth_header()
        # Проверяем, что заголовок авторизации содержит только ASCII
        try:
            auth_header.encode('ascii')
        except UnicodeEncodeError:
            logger.error("Заголовок Authorization содержит не-ASCII символы! Это может быть проблемой.")
            # Не очищаем Authorization, так как это может сломать токен
            # Вместо этого логируем предупреждение
        
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        # Очищаем заголовки, но с осторожностью для Authorization
        headers = _sanitize_headers(headers)
        
        base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1"

        try:
            if stream:
                # Потоковый режим
                # Используем json параметр для автоматической обработки UTF-8
                response = self.session.post(
                    f"{base_url}/completion",
                    headers=headers,
                    json=payload,
                    stream=True
                )
                response.raise_for_status()

                full_text = ""
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data_str = line_text[6:]
                            try:
                                data = json.loads(data_str)
                                if 'result' in data and 'alternatives' in data['result']:
                                    for alt in data['result']['alternatives']:
                                        if 'message' in alt and 'text' in alt['message']:
                                            full_text += alt['message']['text']
                            except json.JSONDecodeError:
                                pass
                return {
                    "choices": [{
                        "message": {"content": full_text, "role": "assistant"}
                    }]
                }
            else:
                # Обычный режим
                # Логируем запрос для отладки
                logger.debug(f"Отправка запроса к YandexGPT: model={model_name}, messages={len(messages)}")
                logger.debug(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
                
                # Используем json параметр для автоматической обработки UTF-8
                response = self.session.post(
                    f"{base_url}/completion",
                    headers=headers,
                    json=payload
                )
                
                if not response.ok:
                    print(f"=== ОШИБКА YANDEXGPT ===")
                    print(f"Статус: {response.status_code}")
                    print(f"Ответ сервера: {response.text}")
                    print(f"Заголовки запроса: {headers}")
                    print(f"Тело запроса: {json.dumps(payload, ensure_ascii=False, indent=2)}")
                    try:
                        error_data = response.json()
                        print(f"Детали ошибки: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
                    except:
                        pass
                    print("========================")
                    logger.error(f"Ошибка запроса YandexGPT:")
                    logger.error(f"  Статус: {response.status_code}")
                    logger.error(f"  Ответ сервера: {response.text}")
                    logger.error(f"  Заголовки запроса: {headers}")
                    logger.error(f"  Тело запроса: {json.dumps(payload, ensure_ascii=False, indent=2)}")
                    # Пробуем получить детальную информацию об ошибке
                    try:
                        error_data = response.json()
                        logger.error(f"  Детали ошибки: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
                    except:
                        pass
                
                response.raise_for_status()

                data = response.json()

                # Преобразуем ответ в формат совместимый с GigaChat
                if 'result' in data and 'alternatives' in data['result']:
                    alt = data['result']['alternatives'][0]
                    text = alt.get('message', {}).get('text', '')
                    return {
                        "choices": [{
                            "message": {"content": text, "role": "assistant"}
                        }]
                    }
                else:
                    return {
                        "choices": [{
                            "message": {"content": "Ошибка получения ответа", "role": "assistant"}
                        }]
                    }

        except requests.RequestException as e:
            import traceback
            logger.error(f"Ошибка запроса YandexGPT: {e}")
            logger.error(f"Трассировка ошибки:\n{traceback.format_exc()}")
            raise
        except UnicodeEncodeError as e:
            import traceback
            logger.error(f"Ошибка кодировки в YandexGPT: {e}")
            logger.error(f"Трассировка ошибки:\n{traceback.format_exc()}")
            raise
        except Exception as e:
            import traceback
            logger.error(f"Неожиданная ошибка в YandexGPT: {e}")
            logger.error(f"Трассировка ошибки:\n{traceback.format_exc()}")
            raise

    def chat_simple(self, user_message: str, model: Optional[str] = None) -> str:
        """
        Упрощённый метод для отправки одного сообщения

        Args:
            user_message: Текст сообщения пользователя
            model: Название модели

        Returns:
            Текст ответа модели
        """
        messages = [{"role": "user", "content": user_message}]
        response = self.chat(messages=messages, model=model)
        return response["choices"][0]["message"]["content"]

    def get_available_models(self) -> List[str]:
        """
        Получить список доступных моделей

        Returns:
            Список названий моделей
        """
        return [
            "yandexgpt-lite",
            "yandexgpt-pro",
            "yandexgpt",
            "gpt-35-turbo"
        ]
