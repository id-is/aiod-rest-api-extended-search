from database.model.educational_resource.educational_resource import EducationalResource
from routers.search_router import SearchRouter


class SearchRouterEducationalResources(SearchRouter[EducationalResource]):
    @property
    def es_index(self) -> str:
        return "educational_resource"

    @property
    def resource_name_plural(self) -> str:
        return "educational_resources"

    @property
    def resource_class(self):
        return EducationalResource

    @property
    def indexed_fields(self):
        return {"platform", "description_plain", "description_html", "date_published", "same_as", "content_identifier"}

    # @indexed_fields.setter
    # def add_indexed_fields(self, new_fields: str):
    #     """Setter method to set indexed_fields"""
    #     self._indexed_fields.add(new_fields)
