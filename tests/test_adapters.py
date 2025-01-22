import pytest

from snowbytes.adapters import permifrost
from snowbytes.enums import ResourceType
from snowbytes.privs import DatabasePriv, WarehousePriv
from snowbytes.resources import Grant, RoleGrant
from snowbytes.resources.resource import ResourcePointer


@pytest.mark.skip("skipping due to pending deprecation")
@pytest.mark.requires_snowflake
def test_permifrost(cursor):
    resources = permifrost.read_permifrost_config(cursor.connection, "tests/fixtures/adapters/permifrost.yml")
    assert ResourcePointer(name="loading", resource_type=ResourceType.WAREHOUSE) in resources
    assert Grant(priv=WarehousePriv.OPERATE, on_warehouse="loading", to="accountadmin") in resources
    assert RoleGrant(role="engineer", to_role="sysadmin") in resources
    assert ResourcePointer(name="raw", resource_type=ResourceType.DATABASE) in resources
    assert Grant(priv=DatabasePriv.USAGE, on_database="raw", to="sysadmin") in resources
    assert ResourcePointer(name="raw", resource_type=ResourceType.DATABASE) in resources
    assert RoleGrant(role="sysadmin", to_user="eburke") in resources
    assert RoleGrant(role="eburke", to_user="eburke") in resources
