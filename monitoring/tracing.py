import os
from opentelemetry import trace

def _init_tracer():
    try:
        from phoenix.otel import register 
        from openinference.instrumentation.openai import OpenAIInstrumentor
        
        project_name = os.getenv("PHOENIX_PROJECT_NAME", "vantrails")
        
        tp = register(
            project_name=project_name,
            endpoint="http://host.docker.internal:6006/v1/traces",
            auto_instrument=True
        )
        
        # Explicitly instrument OpenAI
        OpenAIInstrumentor().instrument(tracer_provider=tp)
        
        return tp.get_tracer(project_name)
    except Exception as e:
        print(f"Warning: Phoenix tracing failed to initialize: {e}")
        # Return no-op tracer
        return trace.NoOpTracer()

tracer = _init_tracer()