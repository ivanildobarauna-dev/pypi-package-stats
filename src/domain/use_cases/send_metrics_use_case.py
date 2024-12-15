import os
from pandas.core.frame import DataFrame
from dotenv import load_dotenv
from tqdm import tqdm
from src.infrastructure.services.dw_service import DWService
from src.infrastructure.services.send_metrics_service import SendMetricsService
from src.infrastructure.utils.logger_module import logger, log_extra_info, LogStatus
from src.infrastructure import tracing_service

load_dotenv()


class SendPypiStatsUseCase:
    def __init__(self):
        self.dw_service = DWService()
        self.send_stats_service = SendMetricsService()
        self.tracing_service = tracing_service
        self.tracer = self.tracing_service.get_tracer()

    def get_stats(self):
        with self.tracer.start_as_current_span("use_cases-get_stats") as span:
            query = f"""
                SELECT
                DOWNLOAD_ID,
                CAST(UNIX_SECONDS(timestamp(TIMESTAMP_ADD(DTTM, INTERVAL 3 HOUR))) AS INT64) DTTM,
                COUNTRY_CODE,
                PROJECT,
                PACKAGE_VERSION,
                INSTALLER_NAME,
                PYTHON_VERSION
                FROM {os.getenv('PROJECT_ID')}.STG.PYPI_PROJ_DOWNLOADS
                WHERE DTTM >= DATETIME_SUB(CURRENT_DATETIME, INTERVAL 120 DAY)
                AND TRUE QUALIFY (ROW_NUMBER() OVER(PARTITION BY DTTM, COUNTRY_CODE, PROJECT, PACKAGE_VERSION, INSTALLER_NAME, PYTHON_VERSION ORDER BY DTTM ASC)) = 1
                AND NOT PUSHED
                limit 10
                """
            df = self.dw_service.query_to_dataframe(query=query)
            return df

    def send_stats(self, df: DataFrame):
        if len(df) == 0:
            return

        with self.tracer.start_as_current_span("use_cases.send_stats") as span:

            downloads_list = []

            for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing data"):
                tags = [
                    f"country_code:{row['COUNTRY_CODE']}",
                    f"project:{row['PROJECT']}",
                    f"package_version:{row['PACKAGE_VERSION']}",
                    f"installer_name:{row['INSTALLER_NAME']}",
                    f"python_version:{row['PYTHON_VERSION']}",
                ]

                result, err = self.send_stats_service.send(
                    tags=tags,
                    value=1,
                    timestamp=row["DTTM"],
                )

                if err:
                    span.set_status(self.tracing_service.span_status.ERROR)
                    span.set_attribute("error", str(err))
                    raise Exception(str(err))

                downloads_list.append(row["DOWNLOAD_ID"])

                if len(downloads_list) == 100:
                    result, err = self.dw_service.update_downloads(
                        downloads_list=downloads_list, project_name=row["PROJECT"]
                    )

                    if err:
                        span.set_status(self.tracing_service.span_status.ERROR)
                        span.set_attribute("error", str(err))
                        raise Exception(str(err))

                    downloads_list = []

            if len(downloads_list) > 0:
                result, err = self.dw_service.update_downloads(
                    downloads_list=downloads_list, project_name=row["PROJECT"]
                )

                if err:
                    span.set_status(self.tracing_service.span_status.ERROR)
                    span.set_attribute("error", str(err))
                    raise Exception(str(err))