from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.template import router as template_router
from app.api.routes.admin_template import router as admin_template_router

def create_app() -> FastAPI:
    app = FastAPI(title="Template Mongo Server")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(template_router, prefix="/api/template", tags=["template"])
    app.include_router(admin_template_router, prefix="/api/admin/template", tags=["admin-template"])

    return app

app = create_app()