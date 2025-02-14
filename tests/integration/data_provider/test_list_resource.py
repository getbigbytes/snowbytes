import os

import pytest
import snowflake.connector.errors
from inflection import pluralize

from tests.helpers import get_json_fixtures
from snowbytes import data_provider
from snowbytes import resources as res
from snowbytes.client import UNSUPPORTED_FEATURE, reset_cache
from snowbytes.identifiers import resource_label_for_type
from snowbytes.resources import Resource
from snowbytes.scope import DatabaseScope, SchemaScope

pytestmark = pytest.mark.requires_snowflake

TEST_ROLE = os.environ.get("TEST_SNOWFLAKE_ROLE")
TEST_USER = os.environ.get("TEST_SNOWFLAKE_USER")

JSON_FIXTURES = list(get_json_fixtures())


@pytest.fixture(
    params=JSON_FIXTURES,
    ids=[resource_cls.__name__ for resource_cls, _ in JSON_FIXTURES],
    scope="function",
)
def resource(request, suffix):
    resource_cls, data = request.param
    if "name" in data and resource_cls not in (res.AccountParameter, res.ScannerPackage):
        data["name"] += f"_{suffix}_list_resources"
    if "login_name" in data:
        data["login_name"] += f"_{suffix}_list_resources"
    resource = resource_cls(**data)

    yield resource


def create(cursor, resource: Resource):
    session_ctx = data_provider.fetch_session(cursor.connection)
    account_edition = session_ctx["account_edition"]
    sql = resource.create_sql(account_edition=account_edition, if_not_exists=True)
    try:
        cursor.execute(sql)
    except Exception as err:
        raise Exception(f"Error creating resource: \nQuery: {err.query}\nMsg: {err.msg}") from err
    return resource


@pytest.fixture(scope="session")
def list_resources_database(cursor, suffix, marked_for_cleanup):
    db = res.Database(name=f"list_resources_test_database_{suffix}")
    cursor.execute(db.create_sql(if_not_exists=True))
    marked_for_cleanup.append(db)
    yield db


def test_list_resource(cursor, list_resources_database, resource, marked_for_cleanup):

    data_provider.fetch_session.cache_clear()
    reset_cache()
    session_ctx = data_provider.fetch_session(cursor.connection)

    if session_ctx["account_edition"] not in resource.edition:
        pytest.skip(
            f"Skipping {resource.__class__.__name__}, not supported by account edition {session_ctx['account_edition']}"
        )

    if not hasattr(data_provider, f"list_{pluralize(resource_label_for_type(resource.resource_type))}"):
        pytest.skip(f"{resource.resource_type} is not supported")

    if resource.__class__ == res.ScannerPackage:
        pytest.skip("Flaky test, skipping for now")
    if isinstance(resource.scope, DatabaseScope):
        list_resources_database.add(resource)
    elif isinstance(resource.scope, SchemaScope):
        list_resources_database.public_schema.add(resource)

    try:
        create(cursor, resource)
        marked_for_cleanup.append(resource)
    except snowflake.connector.errors.ProgrammingError as err:
        if err.errno == UNSUPPORTED_FEATURE:
            pytest.skip(f"{resource.resource_type} is not supported")
        else:
            raise

    list_resources = data_provider.list_resource(cursor, resource_label_for_type(resource.resource_type))
    assert len(list_resources) > 0
    assert resource.fqn in list_resources


# @pytest.mark.enterprise
# def test_list_tag_references(cursor):
#     data_provider.fetch_session.cache_clear()
#     reset_cache()
#     tag_references = data_provider.list_tag_references(cursor)
#     assert len(tag_references) > 0
