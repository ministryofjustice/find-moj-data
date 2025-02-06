# Adding metadata from Create a Derived Table to Find MoJ data

Find MoJ data uses the [Create a Derived Table](https://github.com/moj-analytical-services/create-a-derived-table) service (CaDeT) as a source of metadata about the Analytical Platform. CaDeT uses a python package called [dbt](https://www.getdbt.com/product/what-is-dbt).

By default, all models and sources will be ingested into the Datahub catalogue, but they will not be shown in the Find MoJ data service.

## Make a model visible

To make a model visible in Find MoJ data, add the `dc_display_in_catalogue` tag to that model. [Config of CaDeT models is described in their documentation here.](https://user-guidance.analytical-platform.service.justice.gov.uk/tools/create-a-derived-table/models/#where-can-i-define-configs)

For example, in `dbt_project.yml` you can include

```yaml
models:
  courts:
    some_subdirectory:
      common_platform_derived:
        +tags:
          - dc_display_in_catalogue
```

This tag should be used for tables that users are expected to work with directly. Don't add it to intermediate/staging tables.

### Generated models

Some models are generated from a template. If you intend to include these generated models
in the catalogue, set `tags` to `$TAGS_WITH_DISPLAY_IN_CATALOGUE$` in the YAML template. This makes sure that the `dc_display_in_catalogue` tag is set in the resulting file.

For example, `/model_templates/oasys/templates/models/risk/oasys/oasys__{table_name}.yml` contains the following model definition:

```yaml
- name: $MODEL_NAME$
  config:
    tags: $TAGS_WITH_DISPLAY_IN_CATALOGUE$
```

### Set required metadata

When adding new entities to the catalgoue, we require that you specify some additional metadata in DBT. For example:

```yaml
models:
  courts:
    +meta:
      dc_slack_channel_name: "#ask-data-engineering"
      dc_slack_channel_url: https://moj.enterprise.slack.com/archives/C8X3PP1TN
      dc_data_custodian: Joe.Bloggs
```

This metadata can be set at domain level, so for all tables in that domain, or individually on a per-table level.

The required fields are as follows:

| field name            | description                                                                                                                                                                                                                                                                             | example                                               |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| dc_slack_channel_name | The name of a slack channel to be used as a contact point for users of the catalogue service, including the leading '#'. Note: this is not the same as the owner channel for notifications.                                                                                             | `#data-engineering`                                   |
| dc_slack_channel_url  | The URL to the slack channel                                                                                                                                                                                                                                                            | `https://moj.enterprise.slack.com/archives/C8X3PP1TN` |
| dc_data_custodian     | The Datahub user ID for the [data custodian](/data/glossary/#glossary:~:text=Data%20governance-,Data%20custodian,-%3A%20Responsible%20for%20the), usually in the form FirstName.LastName. This is a technical contact, _not_ a data owner, information asset owner (IAO), or DBT owner. | `Joe.Bloggs`                                          |

### Additional metadata

| field name                 | description                                                                                                                                                              | example            |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------ |
| dc_where_to_access_dataset | An enum representing how the data can be accessed by end users, eg a choice of ["AnalyticalPlatform", "CourtsAPI"]. For DBT, this always defaults to AnalyticalPlatform. | AnalyticalPlatform |

### Ensure the data custodian has an account in Datahub

The user's Datahub account must exist before you set the `dc_data_custodian`. This will happen automatically the first time they log into Datahub.

The user ID is visible in the URL of a user page in Datahub, e.g.

`https://datahub-catalogue-dev.apps.live.cloud-platform.service.justice.gov.uk/user/**urn:li:corpuser:Joe.Bloggs**/owner%20of`

[Speak to Find MoJ data team](/index.html#contact-us) if you would like us to manually add a set of users without them logging in.

### Full example `dbt_project.yml` file

```yaml
models:
  mojap_derived_tables:
    +materialized: table
    +group: default
    +meta:
      # Metadata to send Find MoJ data. Can be overriden
      # per domain/model/source
      dc_slack_channel_name: "#ask-data-modelling"
      dc_slack_channel_url: https://moj.enterprise.slack.com/archives/C03J21VFHQ9
      dc_where_to_access_dataset: AnalyticalPlatform
    bold:
      +meta:
        dc_data_custodian: jane.doe
      +group: bold
      bold_rr_pnc_ids:
      +tags:
        - bold_daily
        - dc_display_in_catalogue
```

## Make a source visible

In CaDeT, dbt sources are not ingested. To ingest a source, [contact the team](/index.html#contact-us) and request that the source is ingested from glue.

## Make a seed visible

All dbt seeds are ingested into the catalogue and shown by default.

## Make a database visible

If your model has been tagged with `dc_display_in_catalogue` then by default it will have its parent database created in Find MoJ data, see guidance for [registering a model/table](../../ingestion/cadet-registration/)

However, this database will have no associated metadata available to make it more useful to someone browsing Find MoJ data. But don't worry you can create this metadata and this section will explain how.

### Creating a metadata file for your CaDeT database

Create a branch off of latest main in the [CaDeT github repoistory](https://github.com/moj-analytical-services/create-a-derived-table).

Add a new yaml file with filename as the name of your database in the folder [`mojap_derived_tables/database_metadata`](https://github.com/moj-analytical-services/create-a-derived-table/tree/main/mojap_derived_tables/database_metadata)

Add your metadata to the file. The content of that file should be like the example below but with metadata relating to your specific database:

```yaml
database_metadata:
  # The name of the database as it appears in prod
  name: example_derived
  # A description of the database that will aid people to understand what
  # it contains and whether it might be of use
  description: This is just an example, serves no other purpose
  # The data custodian (technical contact)
  # This should be the name as it appears before the @justice.gov.uk
  # If a functional mailbox or team email it can be given as full email
  # address
  dc_data_custodian: some.body12
  # Slack channel name for where people should direct any questions they
  # have about the data
  dc_slack_channel_name: "#ask-channel-example"
  # The url for the named channel above
  dc_slack_channel_url: "https://moj.enterprise.slack.com/archives/12"
  # A readable user friendly name for the database that can be used to
  # display in find-moj-data
  dc_readable_name: Example derived
  # A link to where a user of find-moj-data can find information on how to
  # access the data
  dc_access_requirements: "https://example-data-access.gov.uk"
```

Raise a pull request, when your file is complete, to have your metadata reviewed and merged to main.

When merged to main your new database metadata will be available in Find MoJ data the following day.
