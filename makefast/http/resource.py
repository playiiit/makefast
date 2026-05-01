from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type


class Resource(ABC):
    """
    Laravel-style API Resource for transforming a single model/dict into a
    consistent JSON-serializable structure.

    Usage:
        class UserResource(Resource):
            def to_dict(self) -> Dict[str, Any]:
                return {
                    "id":    self.data["id"],
                    "name":  self.data["name"],
                    "email": self.data["email"],
                }

        # In your route:
        user = await User.find(1)
        return UserResource(user).response()

    You can also attach extra meta data:
        return UserResource(user).with_meta({"token": jwt_token}).response()
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Args:
            data: A dict (e.g. a row returned from MySQLBase) or any mapping.
        """
        self.data = data
        self._meta: Dict[str, Any] = {}
        self._wrap: Optional[str] = "data"

    # ---------------------------------------------------------------
    # Override in subclasses
    # ---------------------------------------------------------------

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Transform the underlying data into a serializable dict.
        Access raw values via self.data["field"].
        """
        ...

    # ---------------------------------------------------------------
    # Fluent modifiers
    # ---------------------------------------------------------------

    def with_meta(self, meta: Dict[str, Any]) -> "Resource":
        """Attach additional top-level metadata to the response envelope."""
        self._meta.update(meta)
        return self

    def without_wrapping(self) -> "Resource":
        """Return the transformed dict directly, without a data key."""
        self._wrap = None
        return self

    def wrap(self, key: str) -> "Resource":
        """Use a custom wrapper key instead of 'data'."""
        self._wrap = key
        return self

    # ---------------------------------------------------------------
    # Serialisation helpers
    # ---------------------------------------------------------------

    def to_response_dict(self) -> Dict[str, Any]:
        """Return the full response envelope as a plain dict."""
        transformed = self.to_dict()

        if self._wrap:
            envelope: Dict[str, Any] = {self._wrap: transformed}
        else:
            envelope = transformed

        envelope.update(self._meta)
        return envelope

    def response(self) -> Dict[str, Any]:
        """
        Shorthand alias for to_response_dict().
        Designed to be returned directly from FastAPI route handlers.
        """
        return self.to_response_dict()

    # ---------------------------------------------------------------
    # Magic helpers
    # ---------------------------------------------------------------

    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access to the raw data: resource["field"]"""
        return self.data[key]

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def get(self, key: str, default: Any = None) -> Any:
        """Safely get a value from raw data with a default."""
        return self.data.get(key, default)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} data={self.data!r}>"


class ResourceCollection:
    """
    Laravel-style Resource Collection for transforming a list of models/dicts.

    Usage:
        class UserCollection(ResourceCollection):
            resource_class = UserResource

        users = await User.all()
        return UserCollection(users).response()

    Or use the inline factory (no subclassing needed):
        return ResourceCollection.of(UserResource, users).response()
    """

    resource_class: Optional[Type[Resource]] = None

    def __init__(self, collection: List[Dict[str, Any]]):
        self.collection = collection
        self._meta: Dict[str, Any] = {}
        self._wrap: Optional[str] = "data"

        if self.resource_class is None:
            raise TypeError(
                f"{self.__class__.__name__}.resource_class must be set to a Resource subclass, "
                "or use ResourceCollection.of(ResourceClass, data)."
            )

    # ---------------------------------------------------------------
    # Factory
    # ---------------------------------------------------------------

    @classmethod
    def of(
        cls,
        resource_class: Type[Resource],
        collection: List[Dict[str, Any]],
    ) -> "_InlineResourceCollection":
        """
        Inline factory – no need to subclass ResourceCollection.

            return ResourceCollection.of(UserResource, users).response()
        """
        return _InlineResourceCollection(resource_class, collection)

    # ---------------------------------------------------------------
    # Fluent modifiers
    # ---------------------------------------------------------------

    def with_meta(self, meta: Dict[str, Any]) -> "ResourceCollection":
        self._meta.update(meta)
        return self

    def without_wrapping(self) -> "ResourceCollection":
        self._wrap = None
        return self

    def wrap(self, key: str) -> "ResourceCollection":
        self._wrap = key
        return self

    # ---------------------------------------------------------------
    # Pagination helper
    # ---------------------------------------------------------------

    def with_pagination(self, pagination: Dict[str, Any]) -> "ResourceCollection":
        """
        Attach Laravel-style pagination metadata.

        Args:
            pagination: The dict returned by MySQLBase.paginate() or
                        QueryBuilder.paginate(), which already contains
                        keys: total, per_page, current_page, last_page, etc.
        """
        self._meta["pagination"] = {
            "total":        pagination.get("total"),
            "per_page":     pagination.get("per_page"),
            "current_page": pagination.get("current_page"),
            "last_page":    pagination.get("last_page"),
            "from":         pagination.get("from"),
            "to":           pagination.get("to"),
        }
        return self

    # ---------------------------------------------------------------
    # Serialisation
    # ---------------------------------------------------------------

    def _transform_collection(self) -> List[Dict[str, Any]]:
        return [
            self.resource_class(item).to_dict()  # type: ignore[misc]
            for item in self.collection
        ]

    def to_response_dict(self) -> Dict[str, Any]:
        items = self._transform_collection()

        if self._wrap:
            envelope: Dict[str, Any] = {self._wrap: items}
        else:
            envelope = {"data": items}

        envelope.update(self._meta)
        return envelope

    def response(self) -> Dict[str, Any]:
        """Return the full response envelope — return this directly from routes."""
        return self.to_response_dict()

    def __len__(self) -> int:
        return len(self.collection)

    def __iter__(self):
        return iter(self.collection)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} count={len(self.collection)}>"


class _InlineResourceCollection(ResourceCollection):
    """Internal helper created by ResourceCollection.of()."""

    def __init__(self, resource_class: Type[Resource], collection: List[Dict[str, Any]]):
        self._meta = {}
        self._wrap = "data"
        self.collection = collection
        self.resource_class = resource_class
