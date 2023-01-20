# stdlib
from typing import Any
from typing import Dict
from typing import List
from typing import Type

# third party
from nacl.signing import SigningKey

# relative
from ...common.uid import UID
from ...io.route import Route
from .api import APIRegistry
from .api import SyftAPI


class SyftClientCache:
    __credentials_store__: Dict = {}
    __cache_key_format__ = "{username}-{password}"

    def _get_key(self, username: str, password: str) -> int:
        key = self.__cache_key_format__.format(username=username, password=password)
        return hash(key)

    def add_user(self, username: str, password: str, verify_key: str):
        hash_key = self._get_key(username, password)
        self.__credentials_store__[hash_key] = verify_key

    def get_user_key(self, username: str, password: str):
        hash_key = self._get_key(username, password)
        return self.__credentials_store__.get(hash_key, None)


class SyftClient:
    credentials: SigningKey
    id: UID
    routes: List[Type[Route]]

    def __init__(
        self, node_uid: str, signing_key: str, routes: List[Type[Route]]
    ) -> None:
        self.id = UID.from_string(node_uid)
        self.credentials = SigningKey(bytes.fromhex(signing_key))
        self.routes = routes
        self._api = None

    @property
    def api(self) -> SyftAPI:
        if self._api is not None:
            return self._api
        _api = self.routes[0].connection._get_api()  # type: ignore
        APIRegistry.set_api_for(node_uid=self.id, api=_api)
        self._api = _api
        return _api

    @property
    def icon(self) -> str:
        return "🏰"

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SyftClient):
            return False

        if self.id != other.id:
            return False

        return True
