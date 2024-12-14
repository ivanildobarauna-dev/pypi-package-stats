from typing import Optional, Tuple
from google.cloud import bigquery
from pandas.core.frame import DataFrame
from src.infrastructure.utils.logger_module import logger, log_extra_info, LogStatus


class BigQuery:
    """
    A class used to represent a BigQueryAdapter
    """
    def __init__(self):
        self.bigquery_conn = bigquery.Client()


    def query_execute(self, query: str) -> Tuple[bigquery.QueryJob, Optional[str]]:
        """
        Get data from BigQuery
        """
        # Perform a query.
        _query = query
        query_job = self.bigquery_conn.query(_query)

        if query_job.errors:
            logger.error(
                f"Error executing query: {str(query_job.error_result)}",
                extra=log_extra_info(status=LogStatus.ERROR),
            )
            return query_job, str(query_job.error_result)

        return query_job, None

    def query_to_dataframe(self, query: str) -> Tuple[DataFrame, Optional[str]]:
        _query = query

        df = DataFrame()

        try:
            query_job = self.bigquery_conn.query(_query)
            if query_job.errors:
                logger.error(
                    f"Error executing query {str(query_job.error_result)}",
                    extra=log_extra_info(status=LogStatus.ERROR),
                )
                return df, str(query_job.error_result)

            df = query_job.to_dataframe()
        except Exception as e:
            logger.error(
                f"Error executing query: {str(e)}",
                extra=log_extra_info(status=LogStatus.ERROR),
            )
            return df, str(e)

        return df, None



class DWService:
    def __init__(self):
        self.datawarehouse = BigQuery()

    def query_execute(self, query: str):
        return self.datawarehouse.query_execute(query)

    def query_to_dataframe(self, query: str):
        return self.datawarehouse.query_to_dataframe(query)
