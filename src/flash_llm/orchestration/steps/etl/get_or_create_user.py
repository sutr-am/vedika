from loguru import logger
from src.domain.documents import UserDocument
from zenml import get_step_context, step


@step
def get_or_create_user(user_full_name: str):
    logger.info(f"Getting or Creating user: {user_full_name}")
    fname = ...
    lname = ...

    user = UserDocument.get_or_create(fname=fname, lname=lname)
    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="user",
        metadata=_get_metadata(user_full_name=user_full_name, user=user),
    )
    return user


def _get_metadata(user_full_name: str, user: UserDocument) -> dict:
    metadata = {
        "query": {"user_full_name": user_full_name},
        "retrieved": {
            "user_id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    }
    return metadata
