# monitoring/exporters/elasticsearch.py

from elasticsearch import Elasticsearch, helpers
import logging
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElasticsearchExporter:
    """
    Handles the exportation of structured logs to an Elasticsearch cluster.
    This class provides methods for bulk-inserting logs and managing index
    templates, which are crucial for efficient log storage and searchability.
    """

    def __init__(self, hosts: List[str], index_prefix: str = "quantum-logs"):
        """
        Initializes the Elasticsearch exporter.
        Args:
            hosts (List[str]): A list of Elasticsearch node URLs to connect to.
            index_prefix (str): The prefix for the log indices. Indices will be
                                created daily with the format: <prefix>-YYYY.MM.DD.
        """
        try:
            self.es = Elasticsearch(hosts)
            if not self.es.ping():
                raise ConnectionError("Could not connect to Elasticsearch.")
        except Exception as e:
            logger.error(f"Elasticsearch connection failed: {e}")
            raise

        self.index_prefix = index_prefix

    def export_logs(self, logs: List[Dict[str, Any]]):
        """
        Exports a batch of structured log records to Elasticsearch using the
        efficient bulk helper.
        Args:
            logs (List[Dict[str, Any]]): A list of log records, where each log
                                         is a dictionary.
        """
        if not logs:
            return

        index_name = f"{self.index_prefix}-{datetime.utcnow().strftime('%Y.%m.%d')}"
        actions = [
            {
                "_index": index_name,
                "_source": log,
            }
            for log in logs
        ]

        try:
            success, failed = helpers.bulk(self.es, actions, stats_only=True)
            logger.info(f"Exported {success} logs to Elasticsearch. Failed: {failed}.")
            if failed > 0:
                logger.warning(f"{failed} logs failed to be indexed.")
        except Exception as e:
            logger.error(f"Failed to export logs to Elasticsearch: {e}")

    def manage_index_template(self, template_name: str, template_body: Dict[str, Any]):
        """
        Creates or updates an index template in Elasticsearch. Index templates
        are used to define settings and mappings for new indices as they are
        created, ensuring consistency.
        Args:
            template_name (str): The name of the index template.
            template_body (Dict[str, Any]): The body of the template, including
                                            index patterns, settings, and mappings.
        """
        try:
            self.es.indices.put_template(name=template_name, body=template_body)
            logger.info(f"Index template '{template_name}' was created or updated successfully.")
        except Exception as e:
            logger.error(f"Failed to manage index template '{template_name}': {e}")
            raise

    @staticmethod
    def get_default_template_body(index_prefix: str) -> Dict[str, Any]:
        """
        Provides a default index template with optimized mappings for logging.
        """
        return {
            "index_patterns": [f"{index_prefix}-*"],
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
                "index.codec": "best_compression"
            },
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "message": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}},
                    "trace_id": {"type": "keyword"},
                    "span_id": {"type": "keyword"},
                    "quantum_context.system_id": {"type": "keyword"},
                    "quantum_context.energy": {"type": "float"},
                }
            }
        }
