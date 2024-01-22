"""Defines Config which is an object that represents a config for elasticsearch connection"""

import json
from os import getenv
from typing import Any, Dict, NoReturn, Optional, Union, cast


class _ConfigKeys:
    USER = "user"
    PASSWORD = "password"
    HOST = "host"
    PORT = "port"
    TIMEOUT = "timeout"
    USE_SSL = "use_ssl"
    ES_CERT_PATH = "es_cert_path"


_Config = Dict[str, Union[str, int, bool]]


# TODO: Migrate to this when updating to a python version that fully supports TypedDict
# from typing_extensions import TypedDict
# class _Config(TypedDict):
#     user: str
#     password: str
#     host: str
#     port: int
#     timeout: int
#     use_ssl: bool
#     es_cert_path: str


class Config:
    """An object that represents a config for elasticsearch connection"""

    _timeout_default: int = 60
    _use_ssl_default: bool = False
    _es_cert_path_default: str = ""

    _es_user_env_key = "ES_USER"
    _es_password_env_key = "ES_PASSWORD"
    _es_host_env_key = "ES_HOST"
    _es_port_env_key = "ES_PORT"
    _es_timeout_env_key = "ES_TIMEOUT"
    _es_use_ssl_env_key = "ES_USE_SSL"
    _es_cert_path_env_key = "ES_CERT_PATH"

    def __init__(self, config: _Config):
        if not Config.__is_config(config):
            raise ValueError("Invalid config")

        self._user = config[_ConfigKeys.USER]
        self._password = config[_ConfigKeys.PASSWORD]
        self._host = config[_ConfigKeys.HOST]
        self._port = config[_ConfigKeys.PORT]
        self._timeout = config.get(_ConfigKeys.TIMEOUT, Config._timeout_default)
        self._use_ssl = config.get(_ConfigKeys.USE_SSL, Config._use_ssl_default)
        self._es_cert_path = config.get(_ConfigKeys.ES_CERT_PATH, Config._es_cert_path_default)

    @classmethod
    def from_json(cls, json_path: str) -> "Config":
        """
        Tries to create a config object from json file.\n
        Fails if the content of the json is not according to rules verified in `Config.__is_config`
        """
        content = cast(dict, json.load(json_path))
        return Config.from_dict(content)

    @classmethod
    def from_args(
            cls,
            *,
            user: str,
            password: str,
            host: str,
            port: int,
            timeout: Optional[int] = None,
            use_ssl: Optional[bool] = None,
            es_cert_path: Optional[str] = None,
    ) -> "Config":
        """
        Creates config from arguments.
        """
        timeout = timeout or cls._timeout_default
        use_ssl = use_ssl or cls._use_ssl_default
        es_cert_path = es_cert_path or cls._es_cert_path_default

        config = Config.__create_config_dict(
            user=user,
            password=password,
            host=host,
            port=port,
            timeout=timeout,
            use_ssl=use_ssl,
            es_cert_path=es_cert_path,
        )

        return cls(config)

    @classmethod
    def from_dict(cls, config: dict) -> "Config":
        """
        Tries to create a config object from specified dict.\n
        Fails if the config dict is not according to rules verified in `Config.__is_config`
        """
        return cls(config)

    @classmethod
    def from_env(
            cls,
            *,
            es_user_key: str = None,
            es_password_key: str = None,
            es_host_key: str = None,
            es_port_key: str = None,
            es_timeout_key: str = None,
            es_use_ssl_key: str = None,
            es_cert_path_key: str = None,
    ) -> "Config":
        """
        Creates config from environment variables.\n
        All the following Environment Variables must be set for this to work:
            - ES_USER
            - ES_PASSWORD
            - ES_HOST
            - ES_PORT
            - ES_TIMEOUT
            - ES_USE_SSL
            - ES_CERT_PATH
        """
        config = Config.__create_config_dict(
            user=cls.__get_env_var(es_user_key or cls._es_user_env_key),
            password=cls.__get_env_var(es_password_key or cls._es_password_env_key),
            host=cls.__get_env_var(es_host_key or cls._es_host_env_key),
            port=cls.__get_env_var(es_port_key or cls._es_port_env_key),
            timeout=cls.__get_env_var(es_timeout_key or cls._es_timeout_env_key),
            use_ssl=cls.__get_env_var(es_use_ssl_key or cls._es_use_ssl_env_key),
            es_cert_path=cls.__get_env_var(es_cert_path_key or cls._es_cert_path_env_key),
        )

        return cls(config)

    @staticmethod
    def __get_env_var(key: str) -> Union[str, NoReturn]:
        value = getenv(key, None)

        if value is None:
            raise KeyError("No such environment variable", key)

        return value

    # TODO: Change to TypeGuard when updating to Python_ver >= 3.10
    @staticmethod
    def __is_config(config: Any) -> bool:
        return (
                isinstance(config, dict)
                and isinstance(config.get(_ConfigKeys.USER), str)
                and isinstance(config.get(_ConfigKeys.PASSWORD), str)
                and isinstance(config.get(_ConfigKeys.HOST), str)
                and isinstance(config.get(_ConfigKeys.PORT), int)
        )

    @staticmethod
    def __create_config_dict(*, user, password, host, port, timeout, use_ssl, es_cert_path) -> _Config:
        """Creates config dict from args"""
        return {
            _ConfigKeys.USER: user,
            _ConfigKeys.PASSWORD: password,
            _ConfigKeys.HOST: host,
            _ConfigKeys.PORT: port,
            _ConfigKeys.TIMEOUT: timeout,
            _ConfigKeys.USE_SSL: use_ssl,
            _ConfigKeys.ES_CERT_PATH: es_cert_path,
        }

    @property
    def user(self) -> str:
        """Getter for configs' user"""
        return self._user

    @property
    def password(self) -> str:
        """Getter for configs' password"""
        return self._password

    @property
    def host(self) -> str:
        """Getter for configs' host"""
        return self._host

    @property
    def port(self) -> int:
        """Getter for configs' port"""
        return self._port

    @property
    def timeout(self) -> int:
        """Getter for configs' timeout"""
        return self._timeout

    @property
    def use_ssl(self) -> bool:
        """Getter for configs' use_ssl"""
        return self._use_ssl

    @property
    def verify_certs(self) -> bool:
        """Getter for configs' verify_certs"""
        return bool(self._es_cert_path)

    @property
    def es_cert_path(self) -> str:
        """Getter for configs' es_cert_path"""
        return self._es_cert_path
