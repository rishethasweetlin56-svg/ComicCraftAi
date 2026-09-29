from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from .config import settings

from .routes import router


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(

    title="ComicCraft API",

    description=(
        "AI-powered five-panel "
        "comic story creator."
    ),

    version="1.0.0"
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(

    "/static",

    StaticFiles(
        directory=str(
            settings.static_dir
        )
    ),

    name="static"
)


# ============================================================
# ROUTES
# ============================================================

app.include_router(
    router
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {

        "status": "ok",

        "service": "ComicCraft",

        "image_provider":
            settings.image_provider,

        "gemini_flash_model":
            settings.gemini_flash_model,

        "gemini_pro_model":
            settings.gemini_pro_model
    }