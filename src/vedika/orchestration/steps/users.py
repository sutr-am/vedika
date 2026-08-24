# src/vedika/orchestration/steps/users.py
from typing import Annotated

from zenml import get_step_context, step

from vedika.application.interfaces.repositories import BaseUserRepository
from vedika.domain.users import UserDomain
from vedika.infrastructure.db.factory import get_user_repository
from vedika.orchestration.utils.trackers import UserMetadataTracker


@step
def get_or_create_user(user_full_name: str) -> Annotated[UserDomain, "users"]:
    tracker = UserMetadataTracker()
    first_name, last_name = user_full_name.split(" ", 1)

    # 1. Dynamically load the repository via the factory
    repository: BaseUserRepository = get_user_repository()
    user = repository.get_or_create_user(first_name=first_name, last_name=last_name)

    tracker.record(user)
    step_context = get_step_context()
    step_context.add_output_metadata(output_name="users", metadata=tracker.full_metadata)

    return user
