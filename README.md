# DM050 Project

## Overview

DM050 is a full-stack application designed to convert natural language queries into SQL statements and provide analytical insights. The project consists of a **backend** powered by FastAPI and Python, and a **frontend** built with React and TypeScript. Together, they deliver a seamless experience for querying databases, visualizing results, and interacting with advanced AI-driven features.

---

## Backend

### Main Python Modules and Their Functionalities

- **api/**
  - `api.py`: Main FastAPI application, sets up endpoints, logging (with Loguru), and response handling. Integrates with the shell and DTOs for request/response models.
  - `dto.py`: Defines data models (using Pydantic) for API requests and responses, such as authentication and chat requests.

- **dm050/**
  - `setup.py`: Initializes the main shell and tools, connects to OpenAI for LLM-based features, and wraps SQL context and tool handlers.
  - `shell.py`: Implements the logic for parsing and handling shell commands, error handling, and tool definitions for database operations.

- **langutils/**
  - `context.py`: Provides database connection and query execution logic using `psycopg` and `pandas`. Includes utilities for reading DDL and inspecting table structures.
  - `llm_tools.py`: Implements chart generation (pie, line, bar) using `matplotlib`, fuzzy matching with `rapidfuzz`, and manages image caching for generated charts.

- **t2sqltools/**
  - `tools.py`: Defines abstract base classes for tools that interact with the database, including similarity search, data retrieval, and chart generation.

- **shell/**
  - `__init__.py`: Defines abstract and concrete classes for shell elements (text, graphics, tables) and the shell wrapper interface.

#### Key Libraries

- **FastAPI**: Web framework for building the API.
- **Loguru**: Advanced logging.
- **Pydantic**: Data validation and settings management.
- **Uvicorn**: ASGI server for running FastAPI.
- **OpenAI**: Access to LLMs for advanced querying and chat features.
- **psycopg**: PostgreSQL database driver.
- **pandas**: Data manipulation and display.
- **matplotlib**: Chart and image generation.
- **rapidfuzz**: Fuzzy string matching for similarity search.
- **tabulate**, **pyyaml**, **aiostomp**, **websocket-client**, **pytest**: Additional utilities for table formatting, YAML parsing, messaging, WebSocket communication, and testing.

#### Example Functionalities

- **Database Operations**: Connects to PostgreSQL, executes SQL queries, retrieves results as Python dictionaries or pandas DataFrames.
- **Chart Generation**: Generates pie, line, and bar charts from SQL query results, caches images, and returns image identifiers.
- **Similarity Search**: Uses fuzzy matching to find similar values in the database.
- **LLM Integration**: Uses OpenAI’s API to process natural language queries and generate SQL or analytical responses.
- **API Endpoints**: Exposes endpoints for authentication, chat, and data retrieval.

---

## Frontend

### Technical Description

The frontend is a React and TypeScript application designed for translating natural language into SQL and visualizing results. It leverages a modern JavaScript/TypeScript ecosystem with a focus on scalability, maintainability, and user experience.

#### Core Libraries and Their Functionalities

- **UI & Styling**
  - **React**: Component-based UI library.
  - **Material UI (@mui/material, @mui/icons-material, @mui/joy, @mui/system, @mui/material-nextjs)**: Pre-built, customizable UI components and icon sets.
  - **@emotion/react, @emotion/styled**: CSS-in-JS for dynamic and themeable styling.
  - **@mui/x-data-grid**: Advanced data grid for tabular data.
  - **@mui/x-date-pickers**: Date and time picker components.
  - **framer-motion**: Animations and transitions.
  - **react-markdown, remark-gfm**: Markdown rendering with GitHub Flavored Markdown support.
  - **react-syntax-highlighter**: Syntax highlighting for code blocks.
  - **react-toastify**: Toast notifications for user feedback.

- **State Management & Utilities**
  - **zustand**: Minimal, fast, and scalable state management.
  - **immer**: Ergonomic immutable state updates.
  - **copy-to-clipboard**: Copy text to clipboard.
  - **zod**: TypeScript-first schema validation.

- **Routing**
  - **react-router, react-router-dom**: Client-side routing and navigation.

- **Development & Build Tooling**
  - **vite**: Fast build tool and dev server.
  - **@vitejs/plugin-react, vite-plugin-svgr**: Enhanced React support and SVG imports.
  - **typescript**: Static typing for JavaScript.
  - **eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, typescript-eslint**: Code quality and linting.
  - **@types/react, @types/react-dom, @types/react-syntax-highlighter**: TypeScript type definitions.
  - **globals**: Recognized global variables for linting.

#### Summary

The frontend is architected for a rich, interactive user experience, combining robust UI frameworks, modern state management, and a powerful developer toolchain. It communicates with the backend API to process natural language queries, display results, and visualize data.

---

## Getting Started

1. **Backend**: Set up Python environment, install dependencies, and run the FastAPI server.
2. **Frontend**: Install Node.js dependencies and start the Vite development server.
3. **Configuration**: Ensure environment variables and API endpoints are correctly set for backend/frontend communication.

For detailed setup instructions, refer to the respective backend and frontend documentation.

---

## License

This project is provided under the terms specified in the repository. Please see the LICENSE file for details.