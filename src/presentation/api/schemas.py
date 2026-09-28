from datetime import datetime

from pydantic import BaseModel, Field

from src.application.ports.usecases import AdView
from src.domain.entities import Ad, AdStatus


class CreateAdRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    price: int = Field(ge=0)
    category: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)


class UpdateAdRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    price: int | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    city: str | None = Field(default=None, min_length=1, max_length=100)


class AdResponse(BaseModel):
    id: int
    user_id: int
    user_name: str | None = None
    title: str
    description: str
    price: int
    category: str
    city: str
    status: AdStatus
    views: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, ad: Ad, user_name: str | None = None) -> "AdResponse":
        return cls(
            id=ad.id,
            user_id=ad.user_id,
            user_name=user_name,
            title=ad.title,
            description=ad.description,
            price=ad.price,
            category=ad.category,
            city=ad.city,
            status=ad.status,
            views=ad.views,
            created_at=ad.created_at,
            updated_at=ad.updated_at,
        )

    @classmethod
    def from_view(cls, view: AdView) -> "AdResponse":
        return cls.from_entity(view.ad, view.user_name)


class AdListResponse(BaseModel):
    items: list[AdResponse]
    total: int
    limit: int
    offset: int


class MyAdsResponse(BaseModel):
    items: list[AdResponse]
    total: int
