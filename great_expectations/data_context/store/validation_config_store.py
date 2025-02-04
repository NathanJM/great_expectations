from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from great_expectations.compatibility.typing_extensions import override
from great_expectations.core.data_context_key import DataContextKey, StringKey
from great_expectations.data_context.cloud_constants import GXCloudRESTResource
from great_expectations.data_context.store.store import Store
from great_expectations.data_context.types.resource_identifiers import (
    GXCloudIdentifier,
)

if TYPE_CHECKING:
    from great_expectations.core.validation_config import ValidationConfig


class ValidationConfigStore(Store):
    _key_class = StringKey

    def get_key(self, name: str, id: str | None = None) -> GXCloudIdentifier | StringKey:
        """Given a name and optional ID, build the correct key for use in the ValidationConfigStore."""  # noqa: E501
        if self.cloud_mode:
            return GXCloudIdentifier(
                resource_type=GXCloudRESTResource.VALIDATION_CONFIG,
                id=id,
                resource_name=name,
            )
        return StringKey(key=name)

    @override
    @staticmethod
    def gx_cloud_response_json_to_object_dict(response_json: dict) -> dict:
        response_data = response_json["data"]

        validation_data: dict
        if isinstance(response_data, list):
            if len(response_data) != 1:
                if len(response_data) == 0:
                    msg = f"Cannot parse empty data from GX Cloud payload: {response_json}"
                else:
                    msg = f"Cannot parse multiple items from GX Cloud payload: {response_json}"
                raise ValueError(msg)
            validation_data = response_data[0]
        else:
            validation_data = response_data

        id: str = validation_data["id"]
        validation_config_dict: dict = validation_data["attributes"]["validation_config"]
        validation_config_dict["id"] = id

        return validation_config_dict

    @override
    def serialize(self, value):
        if self.cloud_mode:
            data = value.dict()
            data["suite"] = data["suite"].to_json_dict()
            return data

        # In order to enable the custom json_encoders in ValidationConfig, we need to set `models_as_dict` off  # noqa: E501
        # Ref: https://docs.pydantic.dev/1.10/usage/exporting_models/#serialising-self-reference-or-other-models
        return value.json(models_as_dict=False, indent=2, sort_keys=True)

    @override
    def deserialize(self, value):
        from great_expectations.core.validation_config import ValidationConfig

        return ValidationConfig.parse_raw(value)

    @override
    def _add(self, key: DataContextKey, value: ValidationConfig, **kwargs):
        if not self.cloud_mode:
            # this logic should move to the store backend, but is implemented here for now
            value.id = str(uuid.uuid4())
        return super()._add(key=key, value=value, **kwargs)
