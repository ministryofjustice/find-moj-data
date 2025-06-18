# Other Sources

### Airflow
AP Users using Airflow for data workloads will generally register outputs with the AWS Glue catalog, so that they are accessible for analysis via AWS Athena. Find MoJ Data can easily ingest from AWS Glue, [please follow our instructions to do so.](/userguide/adding-metadata-from-the-aws-glue-catalog/)

To define Airflow metadata in code, so that it is not just stored in the Glue catalogue, use [`awswrangler.s3.store_parquet_metadata`](https://aws-sdk-pandas.readthedocs.io/en/stable/stubs/awswrangler.s3.store_parquet_metadata.html) to attach metadata to the parquet file created from your Airflow job. [Here's an example of this being done.](https://github.com/moj-analytical-services/data_linking/blob/473e015227112a39bb71a786fa7ba9ec6550fe4c/06_products/internal/journey/mh-cx/job.py)


### AWS Glue Catalogue
Data stored in AWS Glue which is not processed via Create A Derived Table but needs to be added to the catalog requires the Find MoJ Data team to be contacted.

Please [raise an issue on GitHub](https://github.com/ministryofjustice/data-catalogue/issues) and supply the team with some information to add the database. Select "New issue" then "Add Glue database to the data catalogue".
