from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config.settings import settings
from app.core.config.firebase import initialize_firebase
from app.api.v1 import auth, exercises, workouts

def create_application() -> FastAPI:
    initialize_firebase()
    
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    application.include_router(
        auth.router,
        prefix=settings.API_V1_STR
    )
    application.include_router(
        exercises.router,
        prefix=settings.API_V1_STR
    )
    application.include_router(
        workouts.router,
        prefix=settings.API_V1_STR
    )

    return application

app = create_application()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}