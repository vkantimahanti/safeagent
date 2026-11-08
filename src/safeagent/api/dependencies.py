import os
from pathlib import Path

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


def get_service() -> PersistentUtilityService:
    db_path = Path(
        os.environ.get(
            "SAFEAGENT_DB_PATH",
            "data/safeagent.db",
        )
    )

    return PersistentUtilityService(db_path)