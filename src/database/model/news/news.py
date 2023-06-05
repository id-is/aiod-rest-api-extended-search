from datetime import datetime
from typing import List
from sqlmodel import Field, Relationship
from database.model.general.news_category import NewsCategory
from database.model.news.news_category import NewsCategoryNewsLink
from database.model.relationships import ResourceRelationshipList
from database.model.resource import Resource
from serialization import (
    AttributeSerializer,
    FindByNameDeserializer,
)


class NewsBase(Resource):
    # Required fields
    title: str = Field(max_length=150, schema_extra={"example": "Example News"})
    date_modified: datetime | None = Field(
        default=None, schema_extra={"example": "2022-01-01T15:15:00.000Z"}
    )
    body: str = Field(max_length=2000, schema_extra={"example": "Example news body"})
    section: str = Field(max_length=500, schema_extra={"example": "Example news section"})
    headline: str = Field(max_length=500, schema_extra={"example": "Example news headline"})
    word_count: int = Field(schema_extra={"example": 100})
    # Recommended fields
    source: str | None = Field(
        max_length=500, default=None, schema_extra={"example": "https://news.source.example"}
    )
    alternative_headline: str | None = Field(
        max_length=500, default=None, schema_extra={"example": "Example news alternative headline"}
    )


class News(NewsBase, table=True):  # type: ignore [call-arg]
    __tablename__ = "news"
    identifier: int = Field(primary_key=True, foreign_key="ai_asset.identifier")
    news_categories: List[NewsCategory] = Relationship(
        back_populates="news", link_model=NewsCategoryNewsLink
    )

    class RelationshipConfig:
        news_categories: List[str] = ResourceRelationshipList(
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(NewsCategory),
            example=["news_category1", "news_category2"],
        )
