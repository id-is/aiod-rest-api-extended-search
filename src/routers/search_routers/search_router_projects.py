from database.model.project.project import Project
from routers.search_router import SearchRouter


class SearchRouterProjects(SearchRouter[Project]):
    @property
    def es_index(self) -> str:
        return "project"

    @property
    def resource_name_plural(self) -> str:
        return "projects"

    @property
    def resource_class(self):
        return Project

    @property
    def indexed_fields(self):
        return {"description_plain", "description_html"}
        #return {"name", "platform", "alternative_name", "start_date", "end_date", "application_area", "description_plain", "description_html", "industrial_sector", "keyword", "research_area", "scientific_domain", "coordinator", "participant", "produced"}

    # @indexed_fields.setter
    # def add_indexed_fields(self, new_fields: str):
    #     """Setter method to set indexed_fields"""
    #     self._indexed_fields.add(new_fields)
