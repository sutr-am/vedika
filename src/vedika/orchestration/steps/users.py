# src/vedika/orchestration/steps/users.py
from typing import Annotated

from zenml import get_step_context, step

from vedika.application.bootstrap.container import ApplicationContainer
from vedika.application.interfaces.repositories import BaseUserRepository
from vedika.domain.users import UserDomain
from vedika.orchestration.utils.trackers import UserMetadataTracker
from vedika.settings import get_settings


@step
def ensure_user(first_name: str, last_name: str) -> Annotated[UserDomain | None, "users"]:
    # 1. Bootstrap the application
    settings = get_settings()
    container = ApplicationContainer(settings=settings)
    repository: BaseUserRepository = container.repository_provider.get_user_repository()
    user = repository.get_or_create_user(first_name=first_name, last_name=last_name)

    tracker = UserMetadataTracker()
    tracker.record(user)
    step_context = get_step_context()
    step_context.add_output_metadata(output_name="users", metadata=tracker.full_metadata)

    return user
