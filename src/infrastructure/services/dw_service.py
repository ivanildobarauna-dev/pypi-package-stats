import os
from typing import Optional, Tuple
from google.cloud import bigquery
from pandas.core.frame import DataFrame
from src.infrastructure.utils.logger_module import logger, log_extra_info, LogStatus
from src.infrastructure import tracing_service


class BigQuery:
    """
    A class used to represent a BigQueryAdapter
    """
    def __init__(self):
        self.bigquery_conn = bigquery.Client()
        self.tracing_service = tracing_service
        self.tracer = self.tracing_service.get_tracer()

    def query_execute(self, query: str) -> Tuple[bigquery.QueryJob, Optional[str]]:
        with self.tracer.start_as_current_span("bigquery-query_execute") as span:
            span.set_attribute("bigquery.query", query)
            """
            Get data from BigQuery
            """
            # Perform a query.
            _query = query
            query_job = self.bigquery_conn.query(_query)
            result = query_job.result()

            span.set_attribute("bigquery.job.total_rows", result.total_rows)
            span.set_attribute("bigquery.job.affected_rows", result.num_dml_affected_rows)


            if query_job.errors:
                span.set_attribute("bigquery.job.error", str(query_job.error_result))
                span.set_status(self.tracing_service.span_status.ERROR)
                logger.error(
                    f"Error executing query: {str(query_job.error_result)}",
                    extra=log_extra_info(status=LogStatus.ERROR),
                )
                return query_job, str(query_job.error_result)

            return query_job, None

    def query_to_dataframe(self, query: str) -> Tuple[DataFrame, Optional[str]]:
        with self.tracer.start_as_current_span("bigquery-query_to_dataframe") as span:
            span.set_attribute("bigquery.query", query)
            _query = query

            df = DataFrame()

            try:
                query_job = self.bigquery_conn.query(_query)
                if query_job.errors:
                    span.set_status(self.tracing_service.span_status.ERROR)
                    logger.error(
                        f"Error executing query {str(query_job.error_result)}",
                        extra=log_extra_info(status=LogStatus.ERROR),
                    )
                    return df, str(query_job.error_result)

                df = query_job.to_dataframe()
                span.set_attribute("bigquery.job.total_rows", df.shape[0])
            except Exception as e:
                span.set_status(self.tracing_service.span_status.ERROR)
                span.set_attribute("bigquery.job.error", str(e))
                logger.error(
                    f"Error executing query: {str(e)}",
                    extra=log_extra_info(status=LogStatus.ERROR),
                )
                return df, str(e)

            return df, None



class DWService:
    def __init__(self):
        self.datawarehouse = BigQuery()
        self.tracing_service = tracing_service
        self.tracer = self.tracing_service.get_tracer()

    def query_to_dataframe(self, query: str):
        with self.tracer.start_as_current_span("services-dw-query_to_dataframe") as span:
            result = self.datawarehouse.query_to_dataframe(query)
        return result

    def update_downloads(self, downloads_list: list, project_name: str):
        with self.tracer.start_as_current_span("services-dw-update_downloads") as span:
            span.set_attribute("sended_rows", len(downloads_list))
            downloads_list_str = ",".join(map(str, downloads_list))

            query = f"""
                UPDATE {os.getenv('PROJECT_ID')}.STG.PYPI_PROJ_DOWNLOADS
                SET PUSHED = true
                WHERE DOWNLOAD_ID in ({downloads_list_str})
                and PROJECT = '{project_name}'
                AND NOT PUSHED
                """
            result =  self.datawarehouse.query_execute(query)
            return result

