from sqlmodel import SQLModel, Field


class ComputationalResourceHasShareLink(SQLModel, table=True):  # type: ignore [call-arg]
    __tablename__ = "computational_resource_has_share_link"
    computational_resource_identifier: int = Field(
        foreign_key="computational_resource.identifier", primary_key=True
    )
    agent_identifier: int = Field(
        foreign_key="computational_resource_uri.identifier", primary_key=True
    )
