import re

from loguru import logger

from vedika.application.preprocessing.cleaning.base import BaseCleaningHandler
from vedika.domain.cleaned import CleanedCodebaseDomain
from vedika.domain.raw import CodebaseDomain


class CodebaseCleaningHandler(BaseCleaningHandler[CodebaseDomain, CleanedCodebaseDomain]):
    def clean(self, data: CodebaseDomain) -> CleanedCodebaseDomain:
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

        return CleanedCodebaseDomain(
            id=data.id,
            content=cleaned_text,
            platform=data.platform,
            author_id=data.author_id,
            author_full_name=data.author_full_name,
        )
