from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from contextlib import asynccontextmanager

from config import settings
from backend.app.core import setup_logging
from app.middleware.logging import LoggingMiddleware, SecurityHeadersMiddleware, RateLimitingMiddleware
from app.db.mongodb import connect_to_mongo, close_mongo_connection

# Import API routes
from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")

    # Connect to databases
    await connect_to_mongo()
    logger.info("Database connections established")

    yield

    # Shutdown
    logger.info("Shutting down application")
    await close_mongo_connection()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="DocBot API with RAG capabilities and user authentication",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Add custom middlewares
app.add_middleware(
    LoggingMiddleware,
    skip_paths=["/health", "/docs", "/openapi.json", "/favicon.ico"]
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RateLimitingMiddleware,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
)

# Include routers
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "request_id": getattr(request.state, "request_id", "unknown"),
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": "2024-01-01T00:00:00Z",  # Should be current timestamp
            "path": request.url.path
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        f"Validation error: {exc.errors()}",
        extra={
            "request_id": getattr(request.state, "request_id", "unknown"),
            "endpoint": request.url.path,
            "method": request.method,
            "validation_errors": exc.errors()
        }
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "status_code": 422,
            "timestamp": "2024-01-01T00:00:00Z",  # Should be current timestamp
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "request_id": getattr(request.state, "request_id", "unknown"),
            "endpoint": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        },
        exc_info=True
    )

    # Don't expose internal errors in production
    detail = str(exc) if settings.DEBUG else "Internal server error"

    return JSONResponse(
        status_code=500,
        content={
            "detail": detail,
            "status_code": 500,
            "timestamp": "2024-01-01T00:00:00Z",  # Should be current timestamp
            "path": request.url.path
        }
    )


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=False,  # We handle access logging in middleware
    )

#
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.api import chat, health
#
# # Create FastAPI instance
# app = FastAPI(title="RAG Chatbot API", version="0.1.0")
#
# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Add your frontend URLs
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
# )
#
# # Include routers
# app.include_router(health.router, prefix="/api")
# app.include_router(chat.router, prefix="/api")
#
# # Root endpoint
# @app.get("/")
# async def root():
#     return {"message": "Welcome to RAG Chatbot Backend!"}
