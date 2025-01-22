# Blueprint

The Blueprint class validates and deploys a set of resources as a group. It provides a structured way to manage your Snowflake resources through two methods: `plan` and `apply`.

Blueprint provides options to customize how resources are deployed to Snowflake, including `run_mode`, `allowlist`, and `dry_run`.

In Python, you utilize the `Blueprint` class to create and manage blueprints. When using the CLI or GitHub Action with YAML configurations, a Blueprint is created automatically.

## Example

```Python
from snowbytes.blueprint import Blueprint
from snowbytes.resources import Database, Schema

bp = Blueprint(
    run_mode='create-or-update',
    resources=[
        Database('my_database'),
        Schema('my_schema', database='my_database'),
    ],
    allowlist=["database", "schema"],
    dry_run=False,
)
plan = bp.plan(session)
bp.apply(session, plan)
```

## Blueprint parameters
**run_mode** `str`
- Defines how the blueprint interacts with the Snowflake account
  - **create-or-update** (*default*): Resources are either created or updated, no resources are destroyed
  - **sync**:
    - `⚠️ WARNING` Sync mode will drop resources.
    - Snowbytes will update Snowflake to match the blueprint exactly. Must be used with `allowlist`.

**resources** `list[Resource]`
- List of resources initialized in the blueprint.

**allowlist** `list[str]`
- Specifies the allowed resource types in the blueprint.

**dry_run** `bool`
- `apply()` will return a list of SQL commands that would be executed without applying them.

**vars** `dict`
- A key-value dictionary that specifies the names and values of vars.

**vars_spec** `list[dict]`
- A list of dictionaries defining the `name`, `type` and `default` (optional) of all expected vars.

**scope** `str`
- Limit Snowbytes's scope to a single database or schema. Must be one of "DATABASE" or "SCHEMA". If not specified, Snowbytes will manage any resource.

**database** `str`
- The name of a database to limit Snowbytes's scope to. Must be used with `scope`.

**schema** `str`
- The name of a schema to limit Snowbytes's scope to. Must be used with `scope` and `database`.

## Methods

### `plan(session)`

The plan method analyzes your Snowflake account to determine how it is different from your configuration. It identifies what resources need to be added, changed, or removed to achieve the desired state.

#### Parameters:
- **session** (`SnowflakeConnection`): The session object used to connect to Snowflake

#### Returns:

- `list[ResourceChange]`: The list of changes that need to be made to the Snowflake account


### `apply(session, [plan])`

The apply method executes the SQL commands required to update your Snowflake account according to the plan generated. Apply returns a list of SQL commands that were executed.

#### Parameters:
- **session** (`SnowflakeConnection`): The session object used to connect to Snowflake
- **plan** (`list[ResourceChange]`, *optional*): The list of changes to apply. If not provided, the plan is generated automatically.

#### Returns:

- `list[str]`: A list of SQL commands that were executed.


### `add(resource: Resource)`

Alternate uses:
- `add(resource_1, resource_2, ...)`
- `add([resource_1, resource_2, ...])`

The add method allows you to add a resource to the blueprint.

## Using vars

### Vars in YAML
In YAML, vars are specified with double curly braces.
```YAML
-- snowbytes.yml
databases:
  - name: "db_{{ var.fruit }}"
```

In the CLI, use the `--vars` flag to pass values to Snowbytes
```sh
# Specify values as a key-value JSON string
snowbytes plan --config snowbytes.yml \
  --vars '{"fruit": "banana"}'
```

Alternatively, use environment variables to pass values to Snowbytes. Vars environment variables must start with `SNOWBYTES_VAR_` and must be in uppercase.

```sh
export SNOWBYTES_VAR_FRUIT="peach"
snowbytes plan --config snowbytes.yml
```

### Vars defaults in YAML

Use the top-level `vars:` key to define a list of expected vars. You must specify a `type`, you can optionally specify a `default`.

```YAML
vars:
  - name: color
    type: string

  - name: fruit
    type: string
    default: apple

databases:
  - name: "db_{{ var.color }}_{{ var.fruit }}"
```


### Vars in Python

```Python
from snowbytes.blueprint import Blueprint
from snowbytes.resources import Database

# In Python, a var can be specifed using Snowbytes's var module
from snowbytes import var
db1 = Database(name=var.db1_name)

# Alternatively, a var can be specified inside a string with double curly braces. This is Jinja-style template syntax, not an f-string.
db2 = Database(name="db_{{ var.db2_name }}")

# Use the vars parameter to pass values to Snowbytes
Blueprint(
  resources=[db1, db2],
  vars={
    "db1_name": "pineapple",
    "db2_name": "durian",
  },
)
```

### Vars defaults in Python

```Python
from snowbytes.blueprint import Blueprint
from snowbytes.resources import Database

# Use the vars_spec parameter to define a list of expected vars. You must specify a `type`, you can optionally specify a `default`.
Blueprint(
  resources=[Database(name="db_{{ var.color }}_{{ var.fruit }}")],
  vars={"color": "blue"},
  vars_spec=[
    {
      "name": "color",
      "type": "string",
    },
    {
      "name": "fruit",
      "type": "string",
      "default": "apple",
    }

  ]
)
```

## Using scope

`🔬 EXPERIMENTAL`

When the `scope` parameter is used, Snowbytes will limit which resources are allowed and limit where those resources are located within Snowflake.

### Using database scope

```YAML
-- raw.yml
scope: DATABASE
database: RAW

schemas:
  - name: FINANCE
  - name: LEGAL
  - name: MARKETING

tables:
  - name: products
    schema: FINANCE
    columns:
      - name: product
        data_type: string
```


### Using schema scope
```YAML
-- salesforce.yml
scope: SCHEMA
database: DEV
schema: SALESFORCE

tables:
  - name: products
    columns:
      - name: product
        data_type: string

tags:
  - name: cost_center
    allowed_values: ["finance", "engineering"]
```

### Scope example: re-use the same schema setup for multiple engineers

```YAML
-- dev_schema.yml
scope: SCHEMA
database: DEV

tables: ...
views: ...
procedures: ...
```

```sh
snowbytes apply --config dev_schema.yml --schema=SCH_TEEJ
snowbytes apply --config dev_schema.yml --schema=SCH_ALLY
snowbytes apply --config dev_schema.yml --schema=SCH_DAVE
```

### Scope example: combine scope with vars

```YAML
-- finance.yml
scope: SCHEMA
database: "ANALYTICS_{{ vars.env }}"
schema: FINANCE

tables: ...
views: ...
procedures: ...
```

```sh
snowbytes apply --config finance.yml --vars='{"env": "stage"}'
snowbytes apply --config finance.yml --vars='{"env": "prod"}'
```