import pytest

from snowbytes.blueprint import Blueprint
from snowbytes.resources import (
    ComputePool,
    Database,
    ImageRepository,
    Role,
    Schema,
    SnowflakePartnerOAuthSecurityIntegration,
    Warehouse,
)


def test_container_service():
    "Test a container service in Snowbytes end-to-end"

    bp = Blueprint()

    db = Database(name="container_test_db")
    sch = Schema(name="container_test_schema")
    db.add(sch)

    admin_role = Role(name="container_test_admin_role")
    wh = Warehouse(name="container_test_wh", auto_suspend=60, auto_resume=True)

    compute_pool = ComputePool(
        name="snowbytes_app_compute_pool_test", min_nodes=1, max_nodes=1, instance_family="CPU_X64_XS"
    )

    image_repository = ImageRepository(name="container_test_image_repo")

    bp.add(compute_pool, image_repository)

    # # Grant permissions
    # bp.grant_all_on_database("snowbytes_db_test", "container_test_admin_role")
    # bp.grant_all_on_schema("snowbytes_db_test.snowbytes_app_test", "container_test_admin_role")
    # bp.grant_select_on_all_tables("snowbytes_db_test.snowbytes_app_test", "container_test_admin_role")
    # bp.grant_select_on_future_tables("snowbytes_db_test.snowbytes_app_test", "container_test_admin_role")

    # bp.grant_all_on_warehouse("container_test_wh", "container_test_admin_role")

    # bp.grant_usage_on_compute_pool("snowbytes_app_compute_pool_test", "container_test_admin_role")
    # bp.grant_monitor_on_compute_pool("snowbytes_app_compute_pool_test", "container_test_admin_role")

    # bp.grant_ownership_on_integration("Application Authentication Test", "container_test_admin_role")

    # bp.grant_bind_service_endpoint_on_account("container_test_admin_role")

    bp.add(db, admin_role, wh)
