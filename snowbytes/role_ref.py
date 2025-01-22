from typing import TYPE_CHECKING, Union

from .var import VarString

if TYPE_CHECKING:
    from snowbytes.resources.role import DatabaseRole, Role

RoleRef = Union["Role", "DatabaseRole", VarString, str]
