import abc
from typing import TypeVar, Generic, Any, Type, Literal, Annotated, TypeAlias

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pydantic.generics import GenericModel
from sqlmodel import SQLModel, select, Field
from starlette import status
from database.model.dataset.dataset import Dataset

from database.model.concept.aiod_entry import AIoDEntryRead
from database.model.concept.concept import AIoDConcept
from database.model.platform.platform import Platform
from database.model.resource_read_and_create import resource_read
from database.session import DbSession
from error_handling import as_http_exception
from .search_routers.elasticsearch import ElasticsearchSingleton
import sys


from database.model.dataset.dataset import Dataset
from database.model.ai_asset.ai_asset import AIAsset
from database.model.models_and_experiments.ml_model import MLModel

CLASS_MAPPING = {
    'dataset': Dataset,
    'ml_model': MLModel
}

SORT = {"identifier": "asc"}
LIMIT_MAX = 1000

RESOURCE = TypeVar("RESOURCE", bound=AIoDConcept)
RESOURCE_READ = TypeVar("RESOURCE_READ", bound=BaseModel)


class SearchResult(BaseModel):
    total_hits: int = Field(description="The total number of results.")
    resources: list = Field(description="The resources matching the search query.")
    limit: int = Field(description="The maximum number of returned results, as specified in the input.")
    offset: int = Field(description="The offset, as specified in the input.")
   
class SearchRouter(Generic[RESOURCE], abc.ABC):
    """
    Providing search functionality in ElasticSearch
    """

    @property
    @abc.abstractmethod
    def es_index(self) -> str:
        """The name of the elasticsearch index"""

    @property
    @abc.abstractmethod
    def resource_name_plural(self) -> str:
        """The name of the resource (plural)"""

    @property
    def key_translations(self) -> dict[str, str]:
        """If an attribute is called differently in elasticsearch than in our
        metadata model, you can define a translation dictionary here. The key
        should be the name in elasticsearch, the value the name in our data
        model."""
        return {}

    @property
    @abc.abstractmethod
    def resource_class(self) -> RESOURCE:
        """The resource class"""

    @property
    @abc.abstractmethod
    def indexed_fields(self) -> set[str]:
        """The set of indexed fields"""
    
    # @indexed_fields.setter
    # def add_indexed_fields(self, new_fields: str):
    #     """Setter method to set indexed_fields"""
    #     self._indexed_fields.add(new_fields)


    def create(self, url_prefix: str) -> APIRouter:
        #self.add_indexed_fields("combined")
        router = APIRouter()
        #print(self.indexed_fields, file = sys.stderr)
        # read_class = resource_read(self.resource_class)  # type: ignore resource_read(Dataset)
        indexed_fields: TypeAlias = Literal[tuple(self.indexed_fields)]  # type: ignore

        @router.get(
            f"{url_prefix}/search/{self.resource_name_plural}/v1",
            tags=["search"],
            description=f"""Search for {self.resource_name_plural}.""",
            # response_model=SearchResult[read_class],  # This gives errors, so not used.
        )
        def search(
            search_query: Annotated[
                str,
                Query(
                    description="The text to find. It is used in an ElasticSearch match query.",
                    examples=["Name of the resource"],
                ),
            ],
            search_fields: Annotated[
                list[indexed_fields] | None,
                Query(
                    description="Search in these fields. If empty, the query will be matched "
                    "against all fields. Do not use the '--' option in Swagger, it is a Swagger "
                    "artifact.",
                ),
            ] = None,
            combined_field: Annotated[
                list[Literal["combined"]] | None,
                Query(
                    description="Search in all fields",
                ),
            ] = None,
            platforms: Annotated[
                list[str] | None,
                Query(
                    description="Search for resources of these platforms. If empty, results from "
                    "all platforms will be returned.",
                    examples=["huggingface", "openml"],
                ),
            ] = None,
            limit: Annotated[int, Query(ge=1, le=LIMIT_MAX)] = 10,
            offset: Annotated[int, Query(ge=0)] = 0,
        ):
            try:
                with DbSession() as session:
                    query = select(Platform)
                    database_platforms = session.scalars(query).all()
                    platform_names = {p.name for p in database_platforms}
            except Exception as e:
                raise as_http_exception(e)

            if platforms and not set(platforms).issubset(platform_names):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"The available platforms are: {platform_names}",
                )
            fields = search_fields if search_fields else self.indexed_fields
            query_matches = [{"match": {f: search_query}} for f in fields]
            query = {"bool": {"should": query_matches, "minimum_should_match": 1}}
            if platforms:
                platform_matches = [{"match": {"platform": p}} for p in platforms]
                query["bool"]["must"] = {
                    "bool": {"should": platform_matches, "minimum_should_match": 1}
                }

            result = ElasticsearchSingleton().client.search(
                index=self.es_index, query=query, from_=offset, size=limit, sort=SORT
            )
            total_hits = result["hits"]["total"]["value"]
           
            resources: list[Type[read_class]] = [  # type: ignore
                self._cast_resource(resource_read(CLASS_MAPPING[hit['_index']]), hit["_source"])
                for hit in result["hits"]["hits"]
            ]

            return SearchResult(  # type: ignore
                total_hits=total_hits,
                resources=resources,
                limit=limit,
                offset=offset,
            )
        return router


    def _cast_resource(
        self, read_class: Type[SQLModel], resource_dict: dict[str, Any]
    ) -> Type[RESOURCE]:
        kwargs = {
            self.key_translations.get(key, key): val
            for key, val in resource_dict.items()
        }

        resource = read_class(**kwargs)
        resource.aiod_entry = AIoDEntryRead(
            date_modified=resource_dict["date_modified"], status=None
        )

        resource.description = {
            "plain": resource_dict["description_plain"],
            "html": resource_dict["description_html"],
        }

        resource.type = resource_dict["type"]

        
        return resource
