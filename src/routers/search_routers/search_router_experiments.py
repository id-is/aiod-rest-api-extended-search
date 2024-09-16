from database.model.models_and_experiments.experiment import Experiment
from routers.search_router import SearchRouter


class SearchRouterExperiments(SearchRouter[Experiment]):
    @property
    def es_index(self) -> str:
        return "experiment"

    @property
    def resource_name_plural(self) -> str:
        return "experiments"

    @property
    def resource_class(self):
        return Experiment

    @property
    def indexed_fields(self):
        return {"description_plain", "description_html"}
        #return {"name", "platform", "alternative_name", "application_area", "description_plain", "description_html", "industrial_sector", "keyword", "scientific_domain", "research_area"}

    # @indexed_fields.setter
    # def add_indexed_fields(self, new_fields: str):
    #     """Setter method to set indexed_fields"""
    #     self._indexed_fields.add(new_fields)
