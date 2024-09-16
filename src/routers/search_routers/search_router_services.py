from database.model.service.service import Service
from routers.search_router import SearchRouter


class SearchRouterServices(SearchRouter[Service]):
    @property
    def es_index(self) -> str:
        return "service"

    @property
    def resource_name_plural(self) -> str:
        return "services"

    @property
    def resource_class(self):
        return Service

    @property
    def indexed_fields(self):
        return {"description_plain", "description_html", "slogan"}
        #return {"name", "platform", "alternative_name", "slogan", "application_area", "description_plain", "description_html", "industrial_sector", "keyword", "research_area", "scientific_domain"}

    # @indexed_fields.setter
    # def add_indexed_fields(self, new_fields: str):
    #     """Setter method to set indexed_fields"""
    #     self._indexed_fields.add(new_fields)
