from threading import Lock
from typing import Callable, Dict, Type, TypeVar

from importlib_metadata import functools

from .config import Config
from .es_endpoint import ESEndpoint

T_ESEndpoint = TypeVar("T_ESEndpoint", bound=ESEndpoint)


class _EndpointTypeNotInitializedError(BaseException):
    pass


def _requires_endpoint_type_init(cls_meth: Callable) -> Callable:
    @functools.wraps(cls_meth)
    def _wrapper(cls: Type["ESEndpointsFactory"], *args, **kwargs):
        if not cls._is_initialized:
            raise _EndpointTypeNotInitializedError("Must initialize endpoint type")
        return cls_meth(cls, *args, **kwargs)

    return _wrapper


class ESEndpointsFactory:
    _is_initialized: bool = False
    _endpoint_cls: Type[T_ESEndpoint]

    _endpoints: Dict[str, T_ESEndpoint] = {}
    _endpoints_lock: Lock = Lock()

    @classmethod
    def init_endpoint_type(cls, endpoint_cls: Type[T_ESEndpoint] = ESEndpoint) -> None:
        if not issubclass(endpoint_cls, ESEndpoint):
            raise TypeError(f"Type {endpoint_cls.__name__} does not inherit {ESEndpoint.__name__}")

        cls._endpoint_cls = endpoint_cls
        cls._is_initialized = True

    @classmethod
    @_requires_endpoint_type_init
    def get_endpoint(cls, config: Config) -> T_ESEndpoint:
        endpoint_id = f'{config.host}:{config.port}'

        if endpoint_id not in cls._endpoints.keys():
            with cls._endpoints_lock:
                if endpoint_id not in cls._endpoints.keys():
                    cls._endpoints[endpoint_id] = cls._endpoint_cls(config)

        return cls._endpoints[endpoint_id]
