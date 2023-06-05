from typing import List
from typing import TYPE_CHECKING

from sqlmodel import Relationship


from database.model.educational_resource.keyword_link import EducationalResourceKeywordLink


if TYPE_CHECKING:  # avoid circular imports; only import while type checking
    from database.model.news.news import News
    from database.model.dataset.dataset import Dataset
    from database.model.educational_resource.educational_resource import EducationalResource
from database.model.dataset.keyword import DatasetKeywordLink
from database.model.news.keyword_link import NewsKeywordLink
from database.model.named_relation import NamedRelation


class Keyword(NamedRelation, table=True):  # type: ignore [call-arg]
    """
    Keywords or tags used to describe some item
    """

    __tablename__ = "keyword"

    datasets: List["Dataset"] = Relationship(
        back_populates="keywords", link_model=DatasetKeywordLink
    )
    news: List["News"] = Relationship(back_populates="keywords", link_model=NewsKeywordLink)
    educational_resources: List["EducationalResource"] = Relationship(
        back_populates="keywords", link_model=EducationalResourceKeywordLink
    )
