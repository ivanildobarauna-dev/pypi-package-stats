from dotenv import load_dotenv
from src.infrastructure.services.tracing_service import TracingService

load_dotenv()

tracing_service = TracingService()
