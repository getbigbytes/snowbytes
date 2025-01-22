import logging
from typing import Optional

import snowflake.connector.errors
from inflection import pluralize

from snowbytes.client import UNSUPPORTED_FEATURE
from snowbytes.data_provider import fetch_resource, list_resource
from snowbytes.enums import ResourceType
from snowbytes.identifiers import URN, resource_label_for_type
from snowbytes.operations.connector import connect
from snowbytes.resources.grant import grant_yaml

logger = logging.getLogger("snowbytes")


def export_resources(
    session=None, include: Optional[list[ResourceType]] = None, exclude: Optional[list[ResourceType]] = None
) -> dict[str, list]:
    if session is None:
        session = connect()
    config = {}
    for resource_type in ResourceType:
        if include and resource_type not in include:
            continue
        if exclude and resource_type in exclude:
            continue
        try:
            config.update(export_resource(session, resource_type))
        # No list method for resource
        except AttributeError:
            logger.warning(f"Skipping {resource_type} because it has no list method")
            continue
        # Resource not supported
        except snowflake.connector.errors.ProgrammingError as err:
            if err.errno == UNSUPPORTED_FEATURE:
                logger.warning(f"Skipping {resource_type} because it is not supported")
                continue
            else:
                raise
    return config


def export_resource(session, resource_type: ResourceType) -> dict[str, list]:
    resource_label = resource_label_for_type(resource_type)
    resource_names = list_resource(session, resource_label)
    if len(resource_names) == 0:
        return {}
    resources = []
    for fqn in resource_names:
        urn = URN(resource_type, fqn, account_locator="")
        try:
            resource = fetch_resource(session, urn)
        except Exception as e:
            logger.warning(f"Failed to fetch resource {urn}: {e}")
            # continue
            raise e
        if resource is None:
            logger.warning(f"Found resource {urn} in metadata but failed to fetch")
            continue
        try:
            resources.append(_format_resource_config(urn, resource, resource_type))
        except Exception as e:
            logger.warning(f"Failed to format resource {urn}: {e}")
            continue
    return {pluralize(resource_label): resources}


def _format_resource_config(urn: URN, resource: dict, resource_type: ResourceType) -> dict:
    if resource_type == ResourceType.GRANT:
        return grant_yaml(resource)
    # Sort dict based on key name
    resource = {k: resource[k] for k in sorted(resource)}
    # Put name field at the top of the dict
    first_fields = {}
    if "name" in resource:
        first_fields = {"name": resource.pop("name")}

    if resource_type == ResourceType.SCHEMA:
        first_fields["database"] = str(urn.database().fqn)

    return {**first_fields, **resource}
