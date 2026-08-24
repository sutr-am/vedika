# src/vedika/orchestration/pipelines/feature_engineering.py
from zenml import pipeline

from vedika.domain.types import DataCategory
from vedika.orchestration.steps.feature_engineering import clean_documents
from vedika.orchestration.steps.retrieve import fetch_unprocessed_documents


@pipeline(name="vedika_feature_engineering")
def feature_engineering_pipeline(category: DataCategory):
    # Delta Retrieval
    raw_docs = fetch_unprocessed_documents(category=category)

    # Cleaning phase
    cleaned_docs = clean_documents(raw_documents=raw_docs)

    # return cleaned_docs
