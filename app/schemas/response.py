from typing import Generic, TypeVar
from pydantic import BaseModel

DataType = TypeVar("DataType", bound=BaseModel)
DocType = TypeVar("DocType", bound=BaseModel)


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses"""
    page: int
    limit: int
    totalPage: int
    totalDocs: int
    hasNext: bool
    hasPrev: bool


class PaginatedListContainer(BaseModel, Generic[DocType]):
    """Container for paginated list data"""
    docs: list[DocType]
    pagination: PaginationMeta


class StandardResponse(BaseModel, Generic[DataType]):
    """Standard API response envelope"""
    status: bool
    message: str
    data: DataType
