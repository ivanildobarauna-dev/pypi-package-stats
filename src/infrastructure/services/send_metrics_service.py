import os
from typing import Tuple, Optional
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_series import MetricSeries
from src.infrastructure.utils.logger_module import logger, log_extra_info, LogStatus
from src.infrastructure.utils.logger_module import logger, log_extra_info, LogStatus


class Datadog:
    def __init__(self):
        self._metric_name = "pypi"
        self.configuration = Configuration()
        self.configuration.api_key["apiKeyAuth"] = os.getenv("DATADOG_API_KEY")
        self.configuration.host = os.getenv("DATADOG_HOST")
        self.configuration.debug = False
        self.configuration.enable_retry = True
        self.configuration.max_retries = 3

    def increment(self, tags: list, value: int, timestamp) -> Tuple[str, Optional[str]]:
        body = MetricPayload(
            series=[
                MetricSeries(
                    metric=self._metric_name,
                    type=MetricIntakeType.COUNT,
                    points=[
                        MetricPoint(
                            # """ Add historical timestamp here """
                            timestamp=int(timestamp),
                            # """ *********************** """
                            value=value,
                        ),
                    ],
                    tags=tags,
                ),
            ],
        )

        try:
            with ApiClient(self.configuration) as api_client:
                api_instance = MetricsApi(api_client)
                response = api_instance.submit_metrics(body=body)
        except Exception as e:
            logger.error(
                f"API Client error sending metrics to DataDog: {str(e)}",
                extra=log_extra_info(status=LogStatus.ERROR),
            )
            return "", str(e)

        if response.to_dict()["errors"]:
            logger.error(
                f"Response error sending metrics to DataDog: {str(e)}",
                extra=log_extra_info(status=LogStatus.ERROR),
            )

            return "", response.to_str()

        logger.info(
            "Metrics sent to DataDog: {response.to_str()}",
            extra=log_extra_info(status=LogStatus.OK),
        )
        return response.to_str(), None


class SendMetricsService:
    def __init__(self):
        self.metrics_repository = Datadog()

    def send(
        self,
        tags: list,
        value: int,
        timestamp: float,
    ) -> Tuple[str, Optional[str]]:
        return self.metrics_repository.increment(
            tags=tags, value=value, timestamp=timestamp
        )
