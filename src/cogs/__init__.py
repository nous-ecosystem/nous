from typing import List

# Import your category packages
from . import owner
from . import admin
from . import general


def get_all_cogs() -> List[str]:
    return [
        # Owner cogs
        "src.cogs.owner.permissions",
        "src.cogs.owner.system",
        # Admin cogs
        "src.cogs.admin.settings",
        # General cogs
        "src.cogs.general.info",
        "src.cogs.general.utility",
    ]
