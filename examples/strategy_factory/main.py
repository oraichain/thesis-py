from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import executables_router, blueprints_router, simulations_router
import uvicorn

app = FastAPI(
    title="Strategy Factory API",
    description="API for creating and executing strategy blueprints with executable chains",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(executables_router)
app.include_router(blueprints_router)
app.include_router(simulations_router)


@app.get("/")
async def root():
    return {
        "message": "Strategy Factory API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
