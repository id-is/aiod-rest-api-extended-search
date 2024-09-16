from database.model.event.event import Event
from routers.search_router import SearchRouter


class SearchRouterEvents(SearchRouter[Event]):
    @property
    def es_index(self) -> str:
        return "event"

    @property
    def resource_name_plural(self) -> str:
        return "events"

    @property
    def resource_class(self):
        return Event

    @property
    def indexed_fields(self):
        return {"description_plain", "description_html"}
        #return {"name", "platform", "alternative_name", "application_area", "content", "description_plain", "description_html", "industrial_sector", "keyword", "location", "research_area", "scientific_domain", "mode", "start_date", "end_date"}

    # @indexed_fields.setter
    # def add_indexed_fields(self, new_fields: str):
    #     """Setter method to set indexed_fields"""
    #     self._indexed_fields.add(new_fields)
