from database.model.agent.organisation import Organisation
from routers.search_router import SearchRouter


class SearchRouterOrganisations(SearchRouter[Organisation]):
    @property
    def es_index(self) -> str:
        return "organisation"

    @property
    def resource_name_plural(self) -> str:
        return "organisations"

    @property
    def resource_class(self):
        return Organisation

    @property
    def indexed_fields(self):
        return {"legal_name", "description_plain", "description_html"}
        #return {"name", "platform", "legal_name", "alternative_name", "ai_relevance", "application_area", "description_plain", "description_html", "industrial_factor", "research_area", "scientific_domain", "type"}

    # @indexed_fields.setter
    # def add_indexed_fields(self, new_fields: str):
    #     """Setter method to set indexed_fields"""
    #     self._indexed_fields.add(new_fields)