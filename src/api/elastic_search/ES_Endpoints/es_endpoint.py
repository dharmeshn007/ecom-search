from elasticsearch import Elasticsearch

from .config import Config


class ESEndpoint(Elasticsearch):
    def __init__(self, config: Config):
        super().__init__(
            hosts=[
                {
                    "host": config.host,
                    "port": config.port,
                    # "http_auth": (config.user, config.password),
                    # "ca_certs": config.es_cert_path,
                    # "use_ssl": config.use_ssl,
                    # "verify_certs": config.verify_certs,
                    # "ssl_show_warns": True,
                    "timeout": config.timeout,
                }
            ]
        )

        self.config = config
