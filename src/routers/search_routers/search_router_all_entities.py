#from database.model.dataset.dataset import Dataset
#from database.model.concept.concept import AIoDConcept
from database.model.ai_asset.ai_asset import AIAsset
#from typing import Type
from routers.search_router import SearchRouter


class AllEntitySearchRouter(SearchRouter[AIAsset]):
    """
    A router that searches across all entities in the platform.
    """

    @property
    def es_index(self) -> str:
        """Search across all indices by using a wildcard."""
        return "*"

    @property
    def indexed_fields(self) -> set[str]:
        """Fields to be searched across all entities."""
        return {"name","version", "platform", "description_plain", "description_html", "date_published", "issn", "same_as", "is_accessible_for_free", "measurement_technique", "temporal_coverage", "size_identifier", "license_identifier","type","pid"}

    @property
    def resource_name_plural(self) -> str:
        """A generic name for all resources."""
        return "all_entities"

    @property
    def resource_class(self):
        """Resource class to be used for this router."""
        return AIAsset

