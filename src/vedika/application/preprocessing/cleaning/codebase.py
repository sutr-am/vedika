# src/vedika/application/preprocessing/cleaning/codebase.py
import re

from loguru import logger

from vedika.application.interfaces.cleaners import BaseCleaningHandler
from vedika.domain.cleaned import CodebaseCleanedDomain
from vedika.domain.raw import CodebaseRawDomain


class CodebaseCleaningHandler(BaseCleaningHandler[CodebaseRawDomain, CodebaseCleanedDomain]):
    def clean(self, data: CodebaseRawDomain) -> CodebaseCleanedDomain:
        raw_text = data.content

        # Data cleaning
        text = raw_text.replace("\r\n", "\n")  # Standardize line ending with Unix style
        text = re.sub(pattern=r"[ \t]+$", repl="", string=text, flags=re.MULTILINE)
        text = re.sub(pattern=r"\n{3,}", repl="\n\n", string=text)
        cleaned_text = text.strip()

        logger.info(
            f"Cleaned codebase '{data.id=}'."
            f"Length reduced from {len(raw_text)} -> {len(cleaned_text)} chars."
        )

        return CodebaseCleanedDomain(
            id=data.id,
            title=data.title,
            content=cleaned_text,
            platform=data.platform,
            source_url=data.source_url,
            user_id=data.user_id,
        )
