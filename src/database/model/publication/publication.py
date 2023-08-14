from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, Relationship

from database.model.ai_asset import AIAsset
from database.model.general.resource_type import ResourceType
from database.model.relationships import ResourceRelationshipList, ResourceRelationshipSingle
from serialization import (
    AttributeSerializer,
    FindByNameDeserializer,
)


class PublicationBase(AIAsset):
    # Required fields
    title: str = Field(max_length=250, schema_extra={"example": "A publication"})

    # Recommended fields
    doi: str | None = Field(max_length=150, schema_extra={"example": "0000000/000000000000"})
    creators: str | None = Field(max_length=450, schema_extra={"example": "John Doe"})
    access_right: str | None = Field(max_length=150, schema_extra={"example": "open access"})
    date_created: datetime | None = Field(
        default=None, schema_extra={"example": "2022-01-01T15:15:00.000Z"}
    )
    date_published: datetime | None = Field(
        default=None, schema_extra={"example": "2023-01-01T15:15:00.000Z"}
    )
    url: str | None = Field(
        max_length=250, schema_extra={"example": "https://www.example.com/publication/example"}
    )


class PublicationOld(PublicationBase, table=True):  # type: ignore [call-arg]
    __tablename__ = "publication_old"

    identifier: int = Field(primary_key=True, foreign_key="ai_asset.identifier")

    # license_identifier: int | None = Field(foreign_key="license_old.identifier")
    # license: Optional[LicenseOld] = Relationship(back_populates="publications")

    # datasets: List["DatasetOld"] = Relationship(
    #     back_populates="citations", link_model=DatasetPublicationLink
    # )
    resource_type_identifier: int | None = Field(foreign_key="resource_type.identifier")
    resource_type: Optional[ResourceType] = Relationship(back_populates="publications")

    class RelationshipConfig:
        datasets: List[int] = ResourceRelationshipList(
            serializer=AttributeSerializer("identifier"), example=[1]
        )
        # license: Optional[str] = ResourceRelationshipSingle(
        #     identifier_name="license_identifier",
        #     serializer=AttributeSerializer("name"),
        #     deserializer=FindByNameDeserializer(LicenseOld),
        #     example="https://creativecommons.org/share-your-work/public-domain/cc0/",
        # )
        resource_type: Optional[str] = ResourceRelationshipSingle(
            identifier_name="resource_type_identifier",
            serializer=AttributeSerializer("name"),
            deserializer=FindByNameDeserializer(ResourceType),
            example="journal article",
        )
