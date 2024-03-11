from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.core import list_parameters, get_db

PageDepends = Annotated[dict, Depends(list_parameters)]
DBDepends = Annotated[AsyncSession, Depends(get_db)]
