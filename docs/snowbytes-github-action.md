# `snowbytes` GitHub Action

## Using the GitHub action

To add the Snowbytes GitHub action to your repository, follow these steps:

### Create a Snowbytes workflow file

Create a file in the GitHub workflows directory of your repo (`.github/workflows/snowbytes.yml`)

```YAML
-- .github/workflows/snowbytes.yml
name: Deploy to Snowflake with Snowbytes
on:
  push:
    branches: [ main ]
    paths:
    - 'snowbytes/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to Snowflake
        uses: getbigbytes/snowbytes-action@main
        with:
          run-mode: 'create-or-update'
          resource-path: './snowbytes'
          allowlist: 'warehouse,role,grant'
          dry-run: 'false'
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
          SNOWFLAKE_ROLE: ${{ secrets.SNOWFLAKE_ROLE }}
          SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
```

### Configure your Snowflake connection

Go to your GitHub repository settings, navigate to `Secrets`. There, add a secret for `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, and whatever other connection settings you need.


### Create a `snowbytes` directory in your repository

Add YAML resource configs to the `snowbytes` directory.

```YAML
# snowbytes/warehouses.yml
warehouses:
  - name: reporting
    warehouse_size: XSMALL
    auto_suspend: 60
    auto_resume: true
```

```YAML
# snowbytes/rbac.yml

roles:
  - name: reporter
    comment: "Has permissions on the analytics database..."

grants:
  - to_role: reporter
    priv: usage
    on_warehouse: reporting
  - to_role: reporter
    priv: usage
    on_database: analytics

role_grants:
  - role: reporter
    roles:
      - SYSADMIN
```

### Commit and push your changes

When you push to `main` changes to files in the `snowbytes/` directory, the Github Action will deploy them to Snowflake.

## Configuration options

**run-mode** `string`

Defines how the blueprint interacts with the Snowflake account

- Default: `"create-or-update"`
- **create-or-update**
  - Resources are either created or updated, no resources are destroyed
- **sync**:
  - `⚠️ WARNING` Sync mode will drop resources.
  - Snowbytes will update Snowflake to match the blueprint exactly. Must be used with `allowlist`.

**resource-path** `string`

Defines the file or directory where Snowbytes will look for the resource configs

- Default: `"."`

**allowlist** `list[string] or "all"`

Defines which resource types are allowed 

 - Default: `"all"`

**dry_run** `bool`

**vars** `dict`

**vars_spec** `list[dict]`

**scope** `str`

**database** `str`

**schema** `str`

## Ignore files with `.snowbytesignore`

If you specify a directory as the `resource-path`, Snowbytes will recursively look for all files with a `.yaml` or `.yml` file extension. You can tell Snowbytes to exclude files or directories with a `.snowbytesignore` file. This file uses [gitignore syntax](https://git-scm.com/docs/gitignore).

### `.snowbytesignore` example

```
# .snowbytesignore

# Ignore dbt config
dbt_project.yml
```