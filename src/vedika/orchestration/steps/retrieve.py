# src/vedika/orchestration/steps/retrieve.py
from typing import Annotated

from loguru import logger
from zenml import step

from vedika.domain.raw import BaseRawDomain
from vedika.domain.types import DataCategory
from vedika.infrastructure.db.factory import get_cleaned_repository, get_raw_repository


@step
def fetch_unprocessed_documents(
    category: DataCategory,
) -> Annotated[list[BaseRawDomain], "unprocessed_raw_documents"]:
    raw_repo = get_raw_repository(category=category)
    cleaned_repo = get_cleaned_repository(category=category)

    all_raw_docs = raw_repo.get_all()
    unprocessed_docs = []
    for doc in all_raw_docs:
        if not cleaned_repo.exists_by_id(document_id=doc.id):
            unprocessed_docs.append(doc)
    logger.info(
        f"Retrieved {len(unprocessed_docs)=} of {category=} out of {len(all_raw_docs)=} documents"
    )
    return unprocessed_docs
