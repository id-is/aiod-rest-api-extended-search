from database.model.knowledge_asset.publication import Publication
from routers.search_router import SearchRouter


class SearchRouterPublications(SearchRouter[Publication]):
    @property
    def es_index(self) -> str:
        return "publication"

    @property
    def resource_name_plural(self) -> str:
        return "publications"

    @property
    def resource_class(self):
        return Publication

    @property
    def indexed_fields(self):
        return {"description_plain", "description_html", "issn", "isbn"}
        #return {"name", "platform", "alternative_name", "date_published", "editor-creator", "application_area", "content", "description_plain", "description_html", "distribution", "documents", "industrial_sector", "keyword", "research_area", "scientific_domain", "type"}

    # @indexed_fields.setter
    # def add_indexed_fields(self, new_fields: str):
    #     """Setter method to set indexed_fields"""
    #     self._indexed_fields.add(new_fields)
