"""Implements Abstract Factory Pattern"""

from vedika.application.preprocessing.cleaning.base import BaseCleaningHandler
from vedika.application.preprocessing.cleaning.codebase import CodebaseCleaningHandler
from vedika.domain.types import DataCategory


class CleaningHandlerFactory:
    @staticmethod
    def create_handler(category: DataCategory) -> BaseCleaningHandler:
        if category == DataCategory.CODEBASES:
            return CodebaseCleaningHandler()
        else:
            raise ValueError(f"Unsupported data-category for cleaning: {category=}")
