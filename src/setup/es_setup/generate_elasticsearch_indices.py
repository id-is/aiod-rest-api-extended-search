#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generates the elasticsearch indices

Launched by the es_logstash_setup container in the docker-compose file.
"""

import copy
import logging
import sys
from definitions import BASE_MAPPING
from routers.search_routers import router_list
from routers.search_routers.elasticsearch import ElasticsearchSingleton
from setup.logstash_setup.generate_logstash_config_files import GLOBAL_FIELDS
from setup_logger import setup_logger


def generate_mapping(fields):
    mapping = copy.deepcopy(BASE_MAPPING)
    #fields.append('combined')

    mapping["mappings"]["properties"]['combined'] = {
            "type": "text",
            "fields": {"keyword": {"type": "keyword"}},
        }
    for field_name in fields:
        print(field_name, file = sys.stderr)
        #if field_name != "name"  and field_name!= "description_plain" and field_name!= "identifier":
        if field_name == "date_published"  or field_name == "issn" or field_name == "size_identifier" or field_name == "license_identifier" or field_name == "is_accessible_for_free" or field_name == "content_identifier" or field_name == "type_identifier":
            mapping["mappings"]["properties"][field_name] = {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
                #"copy_to": "combined"
            }
        elif field_name != "name" and field_name != "description_plain" and field_name != "description_html" and field_name != "combined":
            mapping["mappings"]["properties"][field_name] = {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
                "copy_to": "combined"
            }
    mapping["mappings"]["properties"]["name"] = {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
                "copy_to": "combined"
            }
    mapping["mappings"]["properties"]["description_plain"] = {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
                "copy_to": "combined"
             }
    mapping["mappings"]["properties"]["description_html"] = {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
                "copy_to": "combined"
             }

    
    return mapping


def main():
    setup_logger()
    es_client = ElasticsearchSingleton().client
    entities = {
        router.es_index: list(router.indexed_fields ^ GLOBAL_FIELDS) for router in router_list
    }
    logging.info("Generating indices...")
    for es_index, fields in entities.items():
        mapping = generate_mapping(fields)
        if es_client.indices.exists(index=es_index):
            es_client.indices.delete(index=es_index, ignore=[400, 404])
        # ignore 400 cause by IndexAlreadyExistsException when creating an index
        es_client.indices.create(index=es_index, body=mapping, ignore=400)
    logging.info("Generating indices completed.")


if __name__ == "__main__":
    main()
