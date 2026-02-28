# Common Errors and Troubleshooting Guide

## LangGraph Errors

### "Checkpointer requires one or more of the following 'configurable' keys: thread_id, checkpoint_ns, checkpoint_id"

**Root Cause:**
This error occurs when LangGraph workflow is compiled with a checkpointer (memory/persistence layer) but the required configuration keys are not provided during workflow execution.

**Technical Explanation:**
- LangGraph uses checkpointers to maintain state across workflow executions
- When `MemorySaver()` or other checkpointers are used in `workflow.compile(checkpointer=memory)`, LangGraph expects configuration parameters
- The workflow execution requires at least one of these keys in the config parameter:
  - `thread_id`: Unique identifier for conversation/session thread
  - `checkpoint_ns`: Namespace for organizing checkpoints
  - `checkpoint_id`: Specific checkpoint identifier

**Code That Causes Error:**
```python
# This will cause the error
memory = MemorySaver()
workflow = workflow.compile(checkpointer=memory)
result = workflow.invoke(state)  # Missing config parameter
```

**Solutions:**

1. **Provide Required Configuration:**
```python
result = workflow.invoke(
    state, 
    config={"configurable": {"thread_id": "unique_session_id"}}
)
```

2. **Remove Checkpointer (Simpler):**
```python
workflow = workflow.compile()  # No checkpointer
result = workflow.invoke(state)  # Works without config
```

**Our Implementation Choice:**
We chose solution #2 for simplicity in the initial implementation. For production systems requiring state persistence, use solution #1 with proper session management.

## LLM Provider Errors

### "No endpoints found for model_name"

**Root Cause:**
The specified model is not available through OpenRouter or the model name format is incorrect.

**Common Invalid Models:**
- `mistralai/mistral-7b-instruct:free` (doesn't exist)
- `google/gemma-7b-it:free` (incorrect format)

**Working Models:**
- `openai/gpt-3.5-turbo`
- `anthropic/claude-3-haiku`
- `meta-llama/llama-2-7b-chat`

**Solution:**
Check OpenRouter's model list at https://openrouter.ai/models and use exact model names.

### "Provider returned error - model_not_available"

**Root Cause:**
The model requires a dedicated endpoint or is not accessible with current API credentials.

**Solution:**
- Use serverless models (most cost-effective)
- Check API credit balance
- Verify model availability in your region

## Validation Errors

### "Required field 'field_name' is missing or empty"

**Root Cause:**
Agent validation logic prevents execution when dependent data is missing.

**Technical Explanation:**
Each agent validates its required input fields before execution. If the previous agent in the workflow failed to populate required fields, subsequent agents will fail validation.

**Solution Flow:**
```python
# Planner needs: user_query
# Researcher needs: requirements (from Planner)
# Architect needs: research (from Researcher)
# Visualizer needs: architecture (from Architect)
# Critic needs: requirements, research, architecture
```

Ensure each agent successfully completes before the next agent executes.

## API Errors

### "Validation failed" (422 Status)

**Common Causes:**
- Empty query string
- Query too long (>5000 characters)
- Invalid characters in query
- Malformed JSON request

**Solution:**
Validate input:
```python
# Valid request
{
  "query": "Design a web API for user management"
}

# Invalid - too short
{
  "query": ""
}

# Invalid - contains script tags
{
  "query": "Design API <script>alert('xss')</script>"
}
```

### "Rate limit exceeded" (429 Status)

**Root Cause:**
Too many requests within the configured time window.

**Solution:**
- Reduce request frequency
- Implement client-side rate limiting
- Increase `RATE_LIMIT_PER_MINUTE` in configuration (if appropriate)

## API Response Errors

### "Object of type datetime is not JSON serializable"

**Root Cause:**
This critical error occurs when FastAPI exception handlers try to serialize Pydantic models containing `datetime` objects using the deprecated `.dict()` method instead of the modern `.model_dump(mode="json")` method.

**Technical Explanation:**
- Pydantic v2 changed serialization behavior for complex types like `datetime`
- `.dict()` method returns raw Python objects (including datetime objects)
- `.model_dump(mode="json")` properly serializes datetime to ISO strings
- JSON.dumps() cannot handle raw datetime objects, causing cascade errors

**Error Chain:**
1. Any error occurs (404, validation, etc.)
2. Exception handler creates ErrorResponse with datetime field
3. `.dict()` returns raw datetime object
4. JSONResponse tries to serialize → **TypeError**
5. This triggers the global exception handler
6. **Same error repeats infinitely** → Server completely broken

**Code That Causes Error:**
```python
# OLD (Broken) - causes cascade failures
return JSONResponse(
    content=ErrorResponse(
        error="Some error",
        timestamp=datetime.utcnow()  # This creates datetime object
    ).dict()  # .dict() keeps datetime as-is → JSON fails
)
```

**Correct Implementation:**
```python
# NEW (Fixed) - properly serializes datetime
return JSONResponse(
    content=ErrorResponse(
        error="Some error", 
        timestamp=datetime.utcnow()
    ).model_dump(mode="json")  # Converts datetime to ISO string
)
```

**Impact:**
- **Severity**: CRITICAL - Makes entire API unusable
- **Symptoms**: Every HTTP error returns 500, endless error loops
- **Detection**: Server logs show repeating JSON serialization errors

**Prevention:**
- Always use `.model_dump(mode="json")` with Pydantic v2
- Never use deprecated `.dict()` method
- Test error handling paths in development

## Configuration Errors

### "OpenRouter API key must be set"

**Root Cause:**
Missing or invalid `OPENROUTER_API_KEY` in environment configuration.

**Solution:**
1. Copy `.env.example` to `.env`
2. Set valid OpenRouter API key
3. Ensure key has sufficient credits

### "Secret key must be set"

**Root Cause:**
Missing or default `SECRET_KEY` in environment configuration.

**Solution:**
Generate secure key:
```python
import secrets
secret_key = secrets.token_urlsafe(32)
```

## Performance Issues

### Slow Response Times

**Common Causes:**
- Complex queries requiring multiple iterations
- Network latency to LLM provider
- Insufficient system resources

**Optimization Strategies:**
- Reduce `MAX_RETRIES` for faster responses
- Use faster models (GPT-3.5 vs GPT-4)
- Implement response streaming
- Add request caching

### High Memory Usage

**Causes:**
- Large workflow states retained in memory
- Excessive logging
- Memory leaks in long-running processes

**Solutions:**
- Implement state cleanup after workflow completion
- Use log rotation
- Monitor memory usage with metrics
- Restart workers periodically in production

## Development Environment Issues

### Import Errors

**Cause:**
Python path issues or missing dependencies.

**Solution:**
```bash
# Ensure virtual environment is activated
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify imports
python -c "import app.main"
```

### Port Already in Use

**Error:** "Address already in use: 8000"

**Solution:**
```bash
# Find process using port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Kill process or use different port
uvicorn app.main:app --port 8001
```

## Debugging Tips

### Enable Debug Logging
```bash
# Set in .env
LOG_LEVEL=DEBUG
DEBUG=true
```

### Test Individual Components
```python
# Test single agent
from app.agents.planner import PlannerAgent
planner = PlannerAgent()
result = planner.execute({"user_query": "test"})
```

### Monitor Metrics
- Access metrics at `http://localhost:8001` (development)
- Check request duration and error rates
- Monitor memory and CPU usage

### Health Checks
```bash
# API health
curl http://localhost:8000/api/v1/health

# Component status
python -c "from app.core.config import get_settings; print(get_settings())"
```