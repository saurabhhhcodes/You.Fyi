from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import workspaces, assets, kits, sharing_links, rag
from fastapi.staticfiles import StaticFiles

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="You.fyi API",
    description="Smart workspace platform with RAG capabilities",
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
app.include_router(workspaces.router)
app.include_router(assets.router)
app.include_router(kits.router)
app.include_router(sharing_links.router)
app.include_router(rag.router)

# Serve minimal UI
app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")


from fastapi.responses import RedirectResponse, FileResponse

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")

@app.get("/", tags=["root"])
def read_root():
    """Redirect to UI"""
    return RedirectResponse(url="/ui/")


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
