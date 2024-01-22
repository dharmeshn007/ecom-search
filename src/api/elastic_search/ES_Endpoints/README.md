# ES-Endpoint-Factory

A generic Elasticsearch endpoints factory to create, cache and maintain any number of connections simultaniously.

## Usage

Create a config object:

```python
from .config import Config

config = Config.from_dict(
        {
            "user": "elastic_user",
            "password": "elastic_password",
            "host": "elastic_host",
            "port": 9200,
            "timeout": 60,
            "use_ssl": True,
            "es_cert_path": "path/to/certificate.cer",
        }
    )
```

Initialize the type of endpoints the factory should use (ESEndpoint is the default):

```python
from .es_endpoints_factory import ESEndpointsFactory

ESEndpointsFactory.init_endpoint_type()
```

or

```python
from es_endpoints_factory.es_endpoint import ESEndpoint
from es_endpoints_factory.es_endpoints_factory import ESEndpointsFactory


class MyCustomEndpoint(ESEndpoint):
    pass


ESEndpointsFactory.init_endpoint_type(MyCustomEndpoint)
```

Create a connection from the config:

```python
es_client = ESEndpointsFactory.get_endpoint(config)
```

Now you can use the es_client as you would with a regular instance of `Elasticsearch`:

```python
es_client.indices.create(index="my-new-index")
```

### The factory caches existing connections

```python
from es_endpoints_factory.config import Config
from es_endpoints_factory.es_endpoints_factory import ESEndpointsFactory


config = Config.from_env()

ESEndpointsFactory.init_endpoint_type()

es_client1 = ESEndpointsFactory.get_endpoint(config)
es_client2 = ESEndpointsFactory.get_endpoint(config)

print(es_client1 is es_client2)  # >>> True
```

### The Config object

There are several ways to create the config file:

```python
from es_endpoints_factory.config import Config

config = Config.from_dict(
        {
            "user": "elastic_user",
            "password": "elastic_password",
            "host": "elastic_host",
            "port": 9200,
            "timeout": 60,
            "use_ssl": True,
            "es_cert_path": "path/to/certificate.cer",
        }
    )

config = Config.from_args(
            user="elastic_user",
            password="elastic_password",
            host="elastic_host",
            port=9200,
            timeout=60,
            use_ssl=True,
            es_cert_path="path/to/certificate.cer",
    )
    
config = Config.from_json("path/to/config_file.json")

config = Config.from_env()
```

