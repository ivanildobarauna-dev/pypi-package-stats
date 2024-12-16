from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
import time

# Configuração do TracerProvider
trace.set_tracer_provider(TracerProvider())

# Configuração do ConsoleSpanExporter
span_processor = SimpleSpanProcessor(ConsoleSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Obter um Tracer
tracer = trace.get_tracer(__name__)

# Método auxiliar 1
def metodo_a():
    with tracer.start_as_current_span("metodo_a") as span:
        span.set_attribute("method_name", "metodo_a")
        span.add_event("Inicio do metodo_a")
        time.sleep(2)  # Simula processamento
        span.add_event("Fim do metodo_a")

# Método auxiliar 2
def metodo_b():
    with tracer.start_as_current_span("metodo_b") as span:
        span.set_attribute("method_name", "metodo_b")
        span.add_event("Inicio do metodo_b")
        time.sleep(3)  # Simula processamento
        span.add_event("Fim do metodo_b")

# Método principal
def main():
    with tracer.start_as_current_span("span_test") as span:
        span.set_attribute("method_name", "main")
        span.add_event("Inicio do processamento principal")

        # Chamar os métodos auxiliares
        metodo_a()
        metodo_b()

        span.add_event("Fim do processamento principal")

# Executar o método principal
if __name__ == "__main__":
    main()
