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


def get_products_index_mapping(dim: int = DEFAULT_VECTOR_DIM) -> Dict[str, Any]:
    return {
        "settings": TECHNICAL_ANALYSIS_SETTINGS,
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "technical_analyzer",
                    "fields": {"raw": {"type": "keyword"}},
                },
                "slug": {"type": "keyword"},
                "description": {"type": "text", "analyzer": "technical_analyzer"},
                "model_number": {
                    "type": "keyword",
                    "fields": {"text": {"type": "text", "analyzer": "technical_analyzer"}},
                },
                "sku": {"type": "keyword"},
                "brand": {"type": "keyword"},
                "category": {"type": "keyword"},
                "subcategory": {"type": "keyword"},
                "price": {"type": "float"},
                "currency": {"type": "keyword"},
                "is_component": {"type": "boolean"},
                "specs": {"type": "object", "dynamic": True},
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
    "components": get_components_index_mapping,
    "reviews": get_reviews_index_mapping,
    "documents": get_documents_index_mapping,
}
