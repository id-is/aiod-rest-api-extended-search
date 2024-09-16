from database.model.dataset.dataset import Dataset
from routers.search_router import SearchRouter


class SearchRouterDatasets(SearchRouter[Dataset]):
    @property
    def es_index(self) -> str:
        return "dataset"

    @property
    def resource_name_plural(self) -> str:
        return "datasets"

    @property
    def resource_class(self):
        return Dataset

    @property
    def indexed_fields(self):
        #return {"name", "description_plain", "description_html", "issn"}
        #return {"version", "name", "platform", "description_plain", "description_html", "date_published", "issn", "platform_resource_identifier", "same_as", "is_accessible_for_free", "measurement_technique", "temporal_coverage", "size_identifier", "spatial_coverage_identifier", "ai_asset_id", "license_identifier", "ai_resource_id", "date_deleted", "aiod_entry_identifier"}
        return {"name","version", "platform", "description_plain", "description_html", "date_published", "issn", "same_as", "is_accessible_for_free", "measurement_technique", "temporal_coverage", "size_identifier", "license_identifier"}

    # @indexed_fields.setter
    # def add_indexed_fields(self, new_fields: str):
    #     """Setter method to set indexed_fields"""
    #     self._indexed_fields.add(new_fields)
