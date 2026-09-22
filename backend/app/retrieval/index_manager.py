"""OpenSearch Index Schemas, Analyzers, and Index Management for Product Advisor."""

from typing import Any, Dict

DEFAULT_VECTOR_DIM = 384

TECHNICAL_ANALYSIS_SETTINGS = {
    "index": {
        "knn": True,
        "knn.algo_param.ef_search": 100,
    },
    "analysis": {
        "analyzer": {
            "technical_analyzer": {
                "type": "custom",
                "tokenizer": "whitespace",
                "filter": [
                    "lowercase",
                    "word_delimiter_technical",
                ],
            }
        },
        "filter": {
            "word_delimiter_technical": {
                "type": "word_delimiter_graph",
                "generate_word_parts": True,
                "generate_number_parts": True,
                "catenate_words": True,
                "catenate_numbers": True,
                "catenate_all": True,
                "split_on_case_change": True,
                "preserve_original": True,
            }
        },
    },
}


DEFAULT_PRODUCT_INDEX = "products_v1"
DEFAULT_PRODUCT_ALIAS = "products_current"


def get_products_index_mapping(dim: int = DEFAULT_VECTOR_DIM) -> Dict[str, Any]:
    return {
        "settings": TECHNICAL_ANALYSIS_SETTINGS,
        "mappings": {
            "properties": {
                "product_id": {"type": "keyword"},
                "id": {"type": "keyword"},
                "brand": {
                    "type": "text",
                    "analyzer": "technical_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword"},
                        "raw": {"type": "keyword"},
                    },
                },
                "model": {
                    "type": "text",
                    "analyzer": "technical_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword"},
                        "raw": {"type": "keyword"},
                    },
                },
                "variant": {
                    "type": "text",
                    "analyzer": "technical_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword"},
                        "raw": {"type": "keyword"},
                    },
                },
                "title": {
                    "type": "text",
                    "analyzer": "technical_analyzer",
                    "fields": {"raw": {"type": "keyword"}},
                },
                "slug": {"type": "keyword"},
                "category": {"type": "keyword"},
                "subcategory": {"type": "keyword"},
                "description": {"type": "text", "analyzer": "technical_analyzer"},
                "search_text": {"type": "text", "analyzer": "technical_analyzer"},
                "specifications": {"type": "object", "dynamic": True},
                "specs": {"type": "object", "dynamic": True},
                "image_reference": {"type": "object", "dynamic": True},
                "source_metadata": {"type": "object", "dynamic": True},
                "model_number": {
                    "type": "keyword",
                    "fields": {"text": {"type": "text", "analyzer": "technical_analyzer"}},
                },
                "sku": {"type": "keyword"},
                "price": {"type": "float"},
                "currency": {"type": "keyword"},
                "is_component": {"type": "boolean"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": dim,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "nmslib",
                    },
                },
            }
        },
    }



def get_components_index_mapping(dim: int = DEFAULT_VECTOR_DIM) -> Dict[str, Any]:
    return {
        "settings": TECHNICAL_ANALYSIS_SETTINGS,
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "product_id": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "technical_analyzer",
                    "fields": {"keyword": {"type": "keyword"}},
                },
                "description": {"type": "text", "analyzer": "technical_analyzer"},
                "voltage_display": {"type": "text", "analyzer": "technical_analyzer"},
                "part_number": {
                    "type": "keyword",
                    "fields": {"text": {"type": "text", "analyzer": "technical_analyzer"}},
                },
                "component_type": {"type": "keyword"},
                "package_type": {"type": "keyword"},
                "mounting_type": {"type": "keyword"},
                "pin_count": {"type": "integer"},
                "lifecycle_status": {"type": "keyword"},
                "voltage_min": {"type": "float"},
                "voltage_max": {"type": "float"},
                "voltage_unit": {"type": "keyword"},
                "current_min": {"type": "float"},
                "current_max": {"type": "float"},
                "current_unit": {"type": "keyword"},
                "power": {"type": "float"},
                "power_unit": {"type": "keyword"},
                "tolerance": {"type": "keyword"},
                "interface": {
                    "type": "text",
                    "analyzer": "technical_analyzer",
                    "fields": {"keyword": {"type": "keyword"}},
                },
                "package": {"type": "keyword"},
                "frequency": {"type": "float"},
                "frequency_unit": {"type": "keyword"},
                "temperature_min": {"type": "float"},
                "temperature_max": {"type": "float"},
                "extra_specs": {"type": "object", "dynamic": True},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": dim,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "nmslib",
                    },
                },
            }
        },
    }


def get_reviews_index_mapping(dim: int = DEFAULT_VECTOR_DIM) -> Dict[str, Any]:
    return {
        "settings": TECHNICAL_ANALYSIS_SETTINGS,
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "product_id": {"type": "keyword"},
                "rating": {"type": "float"},
                "title": {"type": "text", "analyzer": "technical_analyzer"},
                "body": {"type": "text", "analyzer": "technical_analyzer"},
                "sentiment": {"type": "keyword"},
                "use_case": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}},
                },
                "is_verified_purchase": {"type": "boolean"},
                "fraud_score": {"type": "float"},
                "attributes_analyzed": {"type": "object", "dynamic": True},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": dim,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "nmslib",
                    },
                },
            }
        },
    }


def get_documents_index_mapping(dim: int = DEFAULT_VECTOR_DIM) -> Dict[str, Any]:
    return {
        "settings": TECHNICAL_ANALYSIS_SETTINGS,
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "product_id": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "technical_analyzer",
                    "fields": {"keyword": {"type": "keyword"}},
                },
                "doc_type": {"type": "keyword"},
                "storage_path": {"type": "keyword"},
                "extracted_text": {"type": "text", "analyzer": "technical_analyzer"},
                "metadata": {"type": "object", "dynamic": True},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": dim,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "nmslib",
                    },
                },
            }
        },
    }


INDEX_MAPPINGS = {
    "products": get_products_index_mapping,
    "products_v1": get_products_index_mapping,
    "components": get_components_index_mapping,
    "reviews": get_reviews_index_mapping,
    "documents": get_documents_index_mapping,
}


def create_versioned_product_index(
    client: Any, index_name: str, dim: int = DEFAULT_VECTOR_DIM
) -> bool:
    """Create a versioned product index if it does not already exist."""
    if client.indices.exists(index=index_name):
        return False
    body = get_products_index_mapping(dim=dim)
    client.indices.create(index=index_name, body=body)
    return True


def switch_alias(client: Any, alias_name: str, target_index: str) -> None:
    """Atomically switch alias_name to point to target_index, removing it from any prior indices."""
    actions = []
    # Find existing indices pointing to this alias
    if client.indices.exists_alias(name=alias_name):
        existing_indices = list(client.indices.get_alias(name=alias_name).keys())
        for idx in existing_indices:
            actions.append({"remove": {"index": idx, "alias": alias_name}})

    actions.append({"add": {"index": target_index, "alias": alias_name}})
    client.indices.update_aliases(body={"actions": actions})


def get_alias_indices(client: Any, alias_name: str) -> list:
    """Get list of concrete index names associated with alias."""
    if not client.indices.exists_alias(name=alias_name):
        return []
    return list(client.indices.get_alias(name=alias_name).keys())

