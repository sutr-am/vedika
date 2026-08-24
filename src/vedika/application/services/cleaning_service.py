# src/vedika/application/services/cleaning_service.py
from loguru import logger

from vedika.application.preprocessing.cleaning.factory import CleaningHandlerFactory
from vedika.domain.cleaned import BaseCleanedDomain
from vedika.domain.raw import BaseRawDomain


class CleaningService:
    """
    Abstract base class for all cleaning services:

    - clean(): transforms the raw document to cleaned document
    """

    def __init__(self):
        self._factory = CleaningHandlerFactory()

    def clean(self, data: BaseRawDomain) -> BaseCleanedDomain:
        handler = self._factory.create_handler(category=data.category)
        try:
            cleaned_data = handler.clean(data=data)
            return cleaned_data
        except Exception as e:
            logger.exception(f"Failed to clean document: {data.id=}: {e}")
            raise


# class CleaningDispatcher:
#     _factory = CleaningHandlerFactory()
#
#     @classmethod
#     def dispatch(cls, data: BaseRawDomain):
#         """Routes the raw data to the correct cleaning-handler and return sthe cleaned document"""
#         handler = cls._factory.create_handler(category=data.category)
#         try:
#             cleaned_data = handler.clean(data=data)
#             return cleaned_data
#         except Exception as e:
#             logger.exception(f"Failed to clean document: {data.id=}: {e}")
#             raise
