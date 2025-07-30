"""
This script is the entry point for running a FastAPI server to handle API requests.

Key Components:
- FastAPI Application: Initializes the FastAPI app with necessary middleware and routes.
- CORS Middleware: Configures Cross-Origin Resource Sharing (CORS) to allow requests from any origin.
- API Routing: Includes a router from the `api.controller` module to manage endpoint handlers.

Environment Configurations:
- PORT: The server's port can be defined via the `APP_PORT` environment variable or defaults from `ApiConfig`.
- HOST: The server's host can be set by the `APP_HOST` environment variable or through `ApiConfig`.

Usage:
Execute this script to start the FastAPI application with predefined configurations.
"""
from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


from seed_index.populate_faiss_index import _populate_faiss_index
from api.router.query import router as query_router
from custom_logger import logger

# Import configuration class for API settings
from configurations.config import ApiConfig

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application startup and shutdown events.
    Code before 'yield' runs on startup.
    Code after 'yield' runs on shutdown.
    """
    logger._log("Application lifespan: Startup initiated.")
    await _populate_faiss_index(os.getenv("env", "local"))
    logger._log(f"FastAPI server is starting on {selected_host}:{selected_port}")
    yield

# Initialize the FastAPI app
app: FastAPI = FastAPI(lifespan=lifespan)
# Load configuration settings
cnf: ApiConfig = ApiConfig()

# Set the port and host using environment variables or fallback to config defaults
selected_port: int = int(os.environ.get("APP_PORT", cnf.PORT))
selected_host: str = str(os.environ.get("APP_HOST", cnf.HOST))

# Add CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

# Include router for process handling
app.include_router(query_router)