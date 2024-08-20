from src.application.services.send_metrics_service import SendMetricsService
from src.adapter.datadog_adapter import DataDogAPIAdapter


class SendMetricsUseCase:
    def __init__(self, metric_name: str, tags: list, value: int):
        self.metrics_repository = DataDogAPIAdapter(metric_name, tags, value)

    def send(self):
        SendMetricsService(MetricsRepository=self.metrics_repository).send()
