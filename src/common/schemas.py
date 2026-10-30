import math
from typing import Self

from pydantic import BaseModel


class PaginationParams(BaseModel):
  page: int = 1
  page_size: int = 10
  paginate: bool = True

  @property
  def skip(self) -> int | None:
    if not self.paginate:
      return None
    return (self.page - 1) * self.page_size

  @property
  def limit(self) -> int | None:
    if not self.paginate:
      return None
    return self.page_size


class PaginationMeta(BaseModel):
  page: int
  page_size: int
  total_count: int
  total_pages: int
  has_next_page: bool
  has_prev_page: bool


class PaginatedResponse[T](BaseModel):
  items: list[T]
  meta: PaginationMeta

  @classmethod
  def create(
    cls,
    items: list[T],
    page: int,
    page_size: int,
    total_count: int,
    paginate: bool = True,
  ) -> Self:
    if not paginate:
      page = 1
      page_size = len(items)
      total_pages = 1
    else:
      total_pages = math.ceil(total_count / page_size)

    return cls(
      items=items,
      meta=PaginationMeta(
        page=page,
        page_size=page_size,
        total_count=total_count,
        total_pages=total_pages,
        has_next_page=page < total_pages,
        has_prev_page=page > 1,
      ),
    )
