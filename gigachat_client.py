"""
Обёртка над официальной библиотекой GigaChat
Документация: https://github.com/ai-foundation/gigachat
"""
import logging
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from typing import Optional, List, Dict, Any, Union

logger = logging.getLogger(__name__)


class GigaChatClient:
    """Клиент для работы с GigaChat API через официальную библиотеку"""

    def __init__(
        self,
        credentials: str,
        scope: str = "GIGACHAT_API_PERS",
        base_url: Optional[str] = None,
        verify_ssl_certs: bool = False,
        model: str = "GigaChat"
    ):
        """
        Инициализация клиента GigaChat

        Args:
            credentials: Ключ авторизации (Base64 от Client ID:Secret или готовый ключ из ЛК)
            scope: Область доступа (GIGACHAT_API_PERS, GIGACHAT_API_B2B, GIGACHAT_API_CORP)
            base_url: Базовый URL API (опционально)
            verify_ssl_certs: Проверять SSL сертификаты (по умолчанию False для GigaChat)
            model: Модель по умолчанию
        """
        self.default_model = model
        self._client = GigaChat(
            credentials=credentials,
            scope=scope,
            base_url=base_url,
            verify_ssl_certs=verify_ssl_certs
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        repetition_penalty: Optional[float] = None,
        function_call: Optional[Union[str, Dict[str, str]]] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        attachments: Optional[List[str]] = None,
        update_interval: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Сгенерировать ответ модели

        Args:
            messages: Массив сообщений (role, content)
            model: Название модели (GigaChat, GigaChat-Pro, GigaChat-2 и т.д.)
            temperature: Температура выборки (креативность ответа)
            top_p: Nucleus sampling параметр
            max_tokens: Максимальное количество токенов в ответе
            stream: Потоковый режим
            repetition_penalty: Штраф за повторения
            function_call: Режим вызова функций (auto, none, или {"name": "func_name"})
            functions: Массив описаний пользовательских функций
            attachments: Массив идентификаторов файлов
            update_interval: Интервал для потокового режима

        Returns:
            Ответ модели
        """
        # Преобразуем сообщения в формат библиотеки
        giga_messages = [
            Messages(
                role=MessagesRole(msg["role"]),
                content=msg["content"]
            )
            for msg in messages
        ]

        payload = Chat(
            messages=giga_messages,
            model=model or self.default_model,
            stream=stream
        )

        # Добавляем опциональные параметры
        if temperature is not None:
            payload.temperature = temperature
        if top_p is not None:
            payload.top_p = top_p
        if max_tokens is not None:
            payload.max_tokens = max_tokens
        if repetition_penalty is not None:
            payload.repetition_penalty = repetition_penalty
        if function_call is not None:
            payload.function_call = function_call
        if functions is not None:
            payload.functions = functions
        if attachments is not None:
            payload.attachments = attachments
        if update_interval is not None:
            payload.update_interval = update_interval

        # Отправляем запрос
        try:
            response = self._client.chat(payload)
        except UnicodeEncodeError as e:
            import traceback
            logger.error(f"Ошибка кодировки в GigaChat: {e}")
            logger.error(f"Трассировка ошибки:\n{traceback.format_exc()}")
            raise
        except Exception as e:
            import traceback
            logger.error(f"Ошибка запроса GigaChat: {e}")
            logger.error(f"Трассировка ошибки:\n{traceback.format_exc()}")
            raise

        # Преобразуем ответ в dict для совместимости
        if hasattr(response, "model_dump"):
            return response.model_dump(mode="json")
        elif hasattr(response, "dict"):
            return response.dict()
        return response.__dict__

    def chat_simple(self, user_message: str, model: Optional[str] = None) -> str:
        """
        Упрощённый метод для отправки одного сообщения

        Args:
            user_message: Текст сообщения пользователя
            model: Название модели

        Returns:
            Текст ответа модели
        """
        response = self._client.chat(user_message, model=model or self.default_model)
        if hasattr(response, "choices") and response.choices:
            return response.choices[0].message.content
        return str(response)

    def get_models(self) -> List[Dict[str, Any]]:
        """
        Получить список доступных моделей

        Returns:
            Список моделей с их описанием
        """
        models = self._client.get_models()
        if hasattr(models, "model_dump"):
            return models.model_dump(mode="json")
        elif hasattr(models, "dict"):
            return models.dict()
        return models.__dict__

    def embeddings(
        self,
        input_text: Union[str, List[str]],
        model: str = "Embeddings"
    ) -> Dict[str, Any]:
        """
        Создать эмбеддинг для текста

        Args:
            input_text: Строка или массив строк
            model: Модель для эмбеддингов (Embeddings или EmbeddingsGigaR)

        Returns:
            Векторное представление текста
        """
        embeddings = self._client.embeddings(input_text, model=model)
        if hasattr(embeddings, "model_dump"):
            return embeddings.model_dump(mode="json")
        elif hasattr(embeddings, "dict"):
            return embeddings.dict()
        return embeddings.__dict__

    def tokens_count(self, texts: List[str], model: str = "GigaChat") -> List[Dict[str, int]]:
        """
        Подсчитать количество токенов в текстах

        Args:
            texts: Массив строк для подсчёта
            model: Название модели

        Returns:
            Массив с информацией о токенах для каждой строки
        """
        counts = self._client.tokens_count(texts, model=model)
        if hasattr(counts[0], "model_dump"):
            return [item.model_dump(mode="json") for item in counts]
        elif hasattr(counts[0], "dict"):
            return [item.dict() for item in counts]
        return [item.__dict__ for item in counts]

    def get_balance(self) -> Dict[str, Any]:
        """
        Получить остаток токенов (только при покупке пакетов токенов)

        Returns:
            Информация о балансе
        """
        balance = self._client.get_balance()
        if hasattr(balance, "model_dump"):
            return balance.model_dump(mode="json")
        elif hasattr(balance, "dict"):
            return balance.dict()
        return balance.__dict__

    def upload_file(self, file_path: str, purpose: str = "general") -> Dict[str, Any]:
        """
        Загрузить файл в хранилище

        Args:
            file_path: Путь к файлу
            purpose: Назначение файла (general)

        Returns:
            Информация о загруженном файле
        """
        with open(file_path, "rb") as f:
            file_info = self._client.upload_file(f, purpose=purpose)
            if hasattr(file_info, "model_dump"):
                return file_info.model_dump(mode="json")
            elif hasattr(file_info, "dict"):
                return file_info.dict()
            return file_info.__dict__

    def get_files(self) -> List[Dict[str, Any]]:
        """Получить список всех файлов"""
        files = self._client.get_files()
        if hasattr(files, "model_dump"):
            return files.model_dump(mode="json")
        elif hasattr(files, "dict"):
            return files.dict()
        return files.__dict__

    def get_file(self, file_id: str) -> Dict[str, Any]:
        """Получить информацию о файле по ID"""
        file_info = self._client.get_file(file_id)
        if hasattr(file_info, "model_dump"):
            return file_info.model_dump(mode="json")
        elif hasattr(file_info, "dict"):
            return file_info.dict()
        return file_info.__dict__

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Удалить файл по ID"""
        result = self._client.delete_file(file_id)
        if hasattr(result, "model_dump"):
            return result.model_dump(mode="json")
        elif hasattr(result, "dict"):
            return result.dict()
        return result.__dict__

    def validate_function(self, function: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидировать описание пользовательской функции

        Args:
            function: Описание функции в формате JSON

        Returns:
            Результат валидации
        """
        result = self._client.validate_function(function)
        if hasattr(result, "model_dump"):
            return result.model_dump(mode="json")
        elif hasattr(result, "dict"):
            return result.dict()
        return result.__dict__

    # Свойство для доступа к нативному клиенту, если нужно напрямую
    @property
    def native_client(self) -> GigaChat:
        """Возвращает нативный клиент GigaChat для продвинутого использования"""
        return self._client
