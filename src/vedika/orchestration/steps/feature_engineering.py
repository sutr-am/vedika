from typing import Annotated

from zenml import step

from vedika.application.preprocessing.cleaning.dispatcher import CleaningDispatcher
from vedika.domain.cleaned import BaseCleanedDomain
from vedika.domain.raw import BaseContentDomain
from vedika.infrastructure.db.factory import get_cleaned_repository


@step
def clean_documents(
    raw_documents: list[BaseContentDomain],
) -> Annotated[list[BaseCleanedDomain], "cleaned_documents"]:
    """ZenML step: Takes raw documents, cleans those and persists in the corresponding DBs"""
    cleaned_documents = []

    if not raw_documents:
        return []

    for raw_doc in raw_documents:
        cleaned_repo = get_cleaned_repository(category=raw_doc.category)
        # # Now this check is moved to the retrieve.py step which fetches only unprocessed raw docs
        # if cleaned_repo.exists_by_id(document_id=raw_doc.id):
        #     cached_doc = cleaned_repo.get_by_id(document_id=raw_doc.id)
        #     cleaned_documents.append(cached_doc)
        #     logger.info(f"{raw_doc.id=} cleaned version already exists. Skipping...")
        #     continue

        # Handoff to application layer
        try:
            cleaned_doc = CleaningDispatcher.dispatch(data=raw_doc)
            cleaned_repo.save(document=cleaned_doc)
            cleaned_documents.append(cleaned_doc)
        except Exception as e:
            raise e
    return cleaned_documents
