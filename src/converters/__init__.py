from typing import Type  # noqa:F401

from schemas import (
    AIoDDataset,
    AIoDEvent,
    AIoDNews,
    AIoDOrganisation,
    AIoDPublication,
    AIoDEducationalResource,
)
from .abstract_converter import ResourceConverter  # noqa:F401
from .dataset_converter import DatasetConverter
from .news_converter import NewsConverter
from .publication_converter import PublicationConverter
from .educational_resource_converter import EducationalResourceConverter
from .event_converter import EventResourceConverter
from .organisation_converter import OrganisationResourceConverter

dataset_converter_instance = DatasetConverter()
news_converter_instance = NewsConverter()
publication_converter_instance = PublicationConverter()
educational_resource_converter_instance = EducationalResourceConverter()
event_converter_instance = EventResourceConverter()
organisation_converter_instance = OrganisationResourceConverter()

converters = {
    AIoDDataset: dataset_converter_instance,
    AIoDEducationalResource: educational_resource_converter_instance,
    AIoDNews: news_converter_instance,
    AIoDPublication: publication_converter_instance,
    AIoDEvent: event_converter_instance,
    AIoDOrganisation: organisation_converter_instance,
}  # type: dict[Type, ResourceConverter]
