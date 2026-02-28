
## Planned Enhancements

* **Streaming Token Output** — Enable real-time token streaming from LLM to client using FastAPI streaming responses and LangChain streaming callbacks.

* **Session Memory (Multi-Turn)** — Maintain conversational state per `session_id` allowing incremental refinement of architecture across multiple user turns.

* **Redis Persistence** — Store LangGraph state in Redis for scalable, fault-tolerant session management across distributed instances.

* **Parallel Agents Execution** — Execute independent agents (e.g., Researcher & Risk Analyzer) concurrently using LangGraph parallel branches to reduce latency.

* **Structured JSON Parsing (Safe Mode)** — Use Pydantic + LangChain structured output parser to enforce schema-safe responses and eliminate JSON parsing failures.

* **Tool Usage (Search / Code Execution)** — Integrate LangChain Tools for web search, Python execution, and external APIs to enhance reasoning accuracy.

* **Token Cost Tracking** — Log token usage per agent using callback handlers for cost monitoring and optimization.

* **Docker Deployment** — Containerize FastAPI + LangGraph app with Docker and enable horizontal scaling via Docker Compose.

* **Production Configuration** — Add environment-based configuration, logging middleware, and health-check endpoints for deployment readiness.

* **Persistent Conversation Memory** — Store long-term design evolution history for advanced iterative system refinement.

* **MCP Integration** — Connect to Model Context Protocol (MCP) servers to allow external tool orchestration and shared context across AI systems.

* **vLLM Stack Support** — Replace OpenRouter with self-hosted vLLM backend for high-throughput, low-latency inference in production environments.

* **Prometheus/Grafana Monitoring** — Full observability stack with metrics dashboards and alerting.
