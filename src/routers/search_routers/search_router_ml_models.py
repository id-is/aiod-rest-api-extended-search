from database.model.models_and_experiments.ml_model import MLModel
from routers.search_router import SearchRouter


class SearchRouterMLModels(SearchRouter[MLModel]):
    @property
    def es_index(self) -> str:
        return "ml_model"

    @property
    def resource_name_plural(self) -> str:
        return "ml_models"

    @property
    def resource_class(self):
        return MLModel

    @property
    def indexed_fields(self):
        return {"name", "description_plain", "description_html", "platform", "version","date_published", "same_as", "is_accessible_for_free","pid", "license_identifier"}


    # @indexed_fields.setter
    # def add_indexed_fields(self, new_fields: str):
    #     """Setter method to set indexed_fields"""
    #     self._indexed_fields.add(new_fields)
