## Main Python Modules and Their Functionalities

### 1. **api**
- **api.py**: Main FastAPI application, sets up endpoints, logging (with Loguru), and response handling. Integrates with the shell and DTOs for request/response models.
- **dto.py**: Defines data models (using Pydantic) for API requests and responses, such as authentication and chat requests.

### 2. **dm050**
- **setup.py**: Initializes the main shell and tools, connects to OpenAI for LLM-based features, and wraps SQL context and tool handlers.
- **shell.py**: Implements the logic for parsing and handling shell commands, error handling, and tool definitions for database operations.

### 3. **langutils**
- **context.py**: Provides database connection and query execution logic using `psycopg` and `pandas`. Also includes utilities for reading DDL and inspecting table structures.
- **llm_tools.py**: Implements chart generation (pie, line, bar) using `matplotlib`, fuzzy matching with `rapidfuzz`, and manages image caching for generated charts.

### 4. **t2sqltools**
- **tools.py**: Defines abstract base classes for tools that interact with the database, including similarity search, data retrieval, and chart generation.

### 5. **shell**
- **__init__.py**: Defines abstract and concrete classes for shell elements (text, graphics, tables) and the shell wrapper interface.

---

## Key Libraries and Their Roles

- **FastAPI**: Web framework for building the API.
- **Loguru**: Advanced logging.
- **Pydantic**: Data validation and settings management.
- **Uvicorn**: ASGI server for running FastAPI.
- **OpenAI**: Access to LLMs for advanced querying and chat features.
- **psycopg**: PostgreSQL database driver.
- **pandas**: Data manipulation and display.
- **matplotlib**: Chart and image generation (pie, line, bar charts).
- **rapidfuzz**: Fuzzy string matching for similarity search.
- **tabulate**: (Not shown in code, but listed as a dependency) For pretty-printing tables.
- **pyyaml**: (Not shown in code, but listed as a dependency) For YAML parsing.
- **aiostomp**: (Not shown in code, but listed as a dependency) For asynchronous messaging (STOMP protocol).
- **websocket-client**: (Not shown in code, but listed as a dependency) For WebSocket communication.
- **pytest**: For testing.

---

## Example Functionalities

- **Database Operations**: Connects to a PostgreSQL database, executes SQL queries, and retrieves results as Python dictionaries or pandas DataFrames.
- **Chart Generation**: Generates pie, line, and bar charts from SQL query results, caches images, and returns image identifiers.
- **Similarity Search**: Uses fuzzy matching to find similar values in the database.
- **LLM Integration**: Uses OpenAI’s API to process natural language queries and generate SQL or analytical responses.
- **API Endpoints**: Exposes endpoints for authentication, chat, and data retrieval.

---
