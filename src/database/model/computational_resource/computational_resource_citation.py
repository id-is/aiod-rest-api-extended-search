from typing import TYPE_CHECKING, List

from sqlmodel import SQLModel, Field, Relationship

from database.model.named_relation import NamedRelation

if TYPE_CHECKING:  # avoid circular imports; only import while type checking
    from database.model.computational_resource.computational_resource import ComputationalResource


class ComputationalResourceCitationLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "computational_resource_citation_link"
    citation_identifier: int = Field(foreign_key="citation.identifier", primary_key=True)
    citation_enum_identifier: int = Field(
        foreign_key="computational_resource_citation.identifier", primary_key=True
    )


class ComputationalResourceCitation(NamedRelation, table=True):  # type: ignore [call-arg]
    __tablename__ = "computational_resource_citation"
    computational_resources: List["ComputationalResource"] = Relationship(
        back_populates="citation", link_model=ComputationalResourceCitationLink
    )
