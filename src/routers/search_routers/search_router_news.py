from database.model.news.news import News
from routers.search_router import SearchRouter


class SearchRouterNews(SearchRouter[News]):
    @property
    def es_index(self) -> str:
        return "news"

    @property
    def resource_name_plural(self) -> str:
        return "news"

    @property
    def resource_class(self):
        return News

    @property
    def indexed_fields(self):
        return {"description_plain", "description_html", "headline", "alternative_headline"}
        #return {"name", "platform", "alternative_name", "date_published", "headline", "alternative_headline", "application_area", "category", "content", "description_plain", "description_html", "industrial_sector", "keyword", "research_area", "scientific_domain"}

    # @indexed_fields.setter
    # def add_indexed_fields(self, new_fields: str):
    #     """Setter method to set indexed_fields"""
    #     self._indexed_fields.add(new_fields)
