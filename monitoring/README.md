## Trace LLM API calls with Phoenix

This project uses Phoenix to automatically monitor and trace LLM API calls. The tracing is already configured and requires no additional code changes.

### Setup

1. Start all services including Phoenix dashboard:
   ```bash
   docker-compose up -d
   ```
2. Access the Phoenix dashboard at: http://localhost:6006

### Usage

Simply make LLM calls as usual in your code. Phoenix will automatically capture:
- Request/response data
- Latency metrics
- Token usage
- Error tracking

The tracing is initialized in `monitoring/tracing.py` and automatically instruments OpenAI API calls through the `OpenAIInstrumentor`.

### Viewing Traces

1. Use the Gradio interface at http://localhost:7860 to ask questions
2. View real-time traces in the Phoenix dashboard at http://localhost:6006
3. Traces appear automatically when LLM API calls are made

### Results

![Tracing](https://github.com/user-attachments/assets/a64df461-934e-440f-9479-945d5838e2bb)

![Dashboard](https://github.com/user-attachments/assets/7059a55d-d8f8-4f49-a4fe-8426c220e9b8)

