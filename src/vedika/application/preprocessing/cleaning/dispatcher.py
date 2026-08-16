from loguru import logger

from vedika.application.preprocessing.cleaning.factory import CleaningHandlerFactory
from vedika.domain.raw import BaseContentDomain


class CleaningDispatcher:
    _factory = CleaningHandlerFactory()

    @classmethod
    def dispatch(cls, data: BaseContentDomain):
        """Routes the raw data to the correct cleaning-handler and return sthe cleaned document"""
        handler = cls._factory.create_handler(category=data.category)
        try:
            cleaned_data = handler.clean(data=data)
            return cleaned_data
        except Exception as e:
            logger.exception(f"Failed to clean document: {data.id=}: {e}")
            raise
