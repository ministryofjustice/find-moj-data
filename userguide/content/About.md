# About

[Find MoJ data](https://find-moj-data.service.justice.gov.uk/) is a searchable catalogue service to help users find and understand data, supporting the [Ministry of Justice's 2025 data strategy](https://www.gov.uk/government/publications/ministry-of-justice-digital-strategy-2025).

The aim is to increase the value of MoJ data by making it easy to find and understand. The catalogue contains **metadata** - data which describes the data assets - not the data itself.

The service is now in public beta with a limited number of datasets catalogued, currently limited to models from the [Create a Derived Table (CaDeT)](https://github.com/moj-analytical-services/create-a-derived-table) service and charts from [Justice Data](https://data.justice.gov.uk/).

### Getting started

All MoJ users can sign in to [Find MoJ data](https://find-moj-data.service.justice.gov.uk/) with their @justice.gov.uk Microsoft account.

Data modelling and engineering (DMET) curate analysis-ready clones of external databases using Create a Derived Table including:

- Book A Secure Move
- Caseman
- Delius
- Nomis
- Oasys
- Sirius
- Xhibit

In addition Create a Derived Table processes some prison apps data and tables uploaded from the data uploader.

Create a Derived Table also contains derived tables that clean, join and transform the curated data listed above, using dimensional modelling, implementing tests and documentation to ensure that the output is reliable and understandable.

Derived data is trusted and consistent across use cases, meaning we get the same answers to the same questions no matter where we ask them and should be used over the curated source data where possible.

Find MoJ Data unites many different MoJ sources in one place, describing datasets with metadata but without including actual data. This is because data owners are responsible for controlling access to potentially sensitive data.

You can use Find MoJ Data to:

* discover datasets from [MoJ data sources](#moj-data-sources)
* evaluate datasets for relevance without needing access to the data they contain
* locate data owners, so you can request access or report a problem

### Using Find MoJ Data

Anyone with an @justice.gov.uk (Microsoft) account can sign in to Find MoJ Data and start using it. Use the service’s search bar to discover datasets through keywords, or select a category to see all datasets in one area. You can filter results to focus on relevant datasets.

Each entry lists metadata to describe the data asset, so you can understand its scope and the type of information it contains. For example, Find MoJ Data can show you database descriptions for versions of NOMIS (`nomis_dbt` or `nomis_sensitive`).

You can see other information about a data asset, including:

* table descriptions
* field descriptions
* database descriptions
* table schemas
* security classification
* how regularly the data owner intends to update the data

<img src="/static/assets/images/guide/example-table-entity.jpg" alt="A screenshot illustrating a data asset example showcasing format type, table descriptions, field descriptions, database descriptions, table schemas, security classification, and how regularly the data owner intends to update the data" width="600" height="600">

### How it works

<img src="/static/assets/images/guide/fmd-process-schematic.svg" alt="A flowchart illustrating the steps in the Find MoJ Data process, starting with data owners providing datasets and ending with Find MoJ Data users accessing the information" width="700" height="300">

* Data owners store and maintain their datasets on the Analytical Platform (AP) and other sources.
* Find MoJ Data ingests the metadata of datasets from the AP and other sources every day.
* Find MoJ Data adds the ingested metadata to DataHub so it can be accessed from the DataHub API.
* Information about ingested datasets is displayed in Find MoJ Data’s user interface.
* Users can find and evaluate dataset entries on Find MoJ Data.
* Users can contact data owners to request access or report a problem.

### Data sources

The MoJ owns a large number of data sources which are stored and maintained differently, making the data landscape complex and difficult to join up. While we continue to grow and improve the catalogue, be aware that not every database or dataset we own is catalogued.

Find MoJ Data includes information about the following:

* statistical publications from GOV.UK
* charts from [Justice Data](https://data.justice.gov.uk/)
* digital prisons reporting (DPR) data from the [Create a Derived Table (CaDeT) service](https://github.com/moj-analytical-services/create-a-derived-table)
* electronic monitoring (EM) data from the [Create a Derived Table (CaDeT) service](https://github.com/moj-analytical-services/create-a-derived-table)
* models from the [Create a Derived Table (CaDeT) service](https://github.com/moj-analytical-services/create-a-derived-table)
* AWS Glue databases, including from legacy pipelines

### Adding datasets

You can add an entry about your data to Find MoJ Data's catalogue yourself if it's derived using the Analytical Platform's Create a Derived Table (CaDeT) service. Follow guidance on [Adding metadata from Create a Derived Table to Find MoJ Data](/userguide/create-a-derived-table).
