from __future__ import annotations

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from .config import settings

from .exporters import save_pdf

from .gemini_flash import (
    generate_outline
)

from .gemini_pro import (
    generate_story
)

from .image_generator import (
    generate_image
)

from .layout_builder import (
    build_comic_layout
)

from .models import (
    ComicResponse,
    PromptRequest
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(

    directory=str(
        settings.templates_dir
    )
)


# ============================================================
# MAIN GENERATION PIPELINE
# ============================================================

def generate_comic(
    request: PromptRequest
) -> ComicResponse:

    # --------------------------------------------------------
    # STEP 1: GEMINI FLASH
    # --------------------------------------------------------

    outline = generate_outline(

        request.story_prompt,

        request.character_name,

        request.setting,

        request.tone,

        request.art_style,
    )


    # --------------------------------------------------------
    # STEP 2: GEMINI PRO
    # --------------------------------------------------------

    story = generate_story(

        outline,

        request.story_prompt,

        request.character_name,

        request.setting,

        request.tone,

        request.art_style,
    )


    # --------------------------------------------------------
    # STEP 3: IMAGE GENERATION
    # --------------------------------------------------------

    image_urls = []


    for panel in story.panels:

        image_url = generate_image(

            panel.image_prompt,

            panel.panel_number
        )


        image_urls.append(
            image_url
        )


    # --------------------------------------------------------
    # STEP 4: LAYOUT
    # --------------------------------------------------------

    layout = build_comic_layout(

        story,

        image_urls
    )


    # --------------------------------------------------------
    # STEP 5: PDF
    # --------------------------------------------------------

    title = (
        f"{request.character_name}'s Comic"
    )


    pdf_url = save_pdf(

        layout,

        title
    )


    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    return ComicResponse(

        title=title,

        layout=layout,

        pdf_url=pdf_url
    )


# ============================================================
# HOME PAGE
# ============================================================

@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={

            "max_prompt_length":
                settings.max_prompt_length
        }
    )


# ============================================================
# HTML GENERATION ROUTE
# ============================================================

@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate(

    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):

    try:

        data = PromptRequest(

            story_prompt=story_prompt,

            character_name=character_name,

            setting=setting,

            tone=tone,

            art_style=art_style,
        )


        comic = generate_comic(
            data
        )


        return templates.TemplateResponse(

            request=request,

            name="comic_preview.html",

            context={
                "comic": comic
            }
        )


    except Exception as exc:

        return templates.TemplateResponse(

            request=request,

            name="index.html",

            context={

                "error": str(exc),

                "max_prompt_length":
                    settings.max_prompt_length
            },

            status_code=500
        )


# ============================================================
# JSON API
# ============================================================

@router.post(
    "/generate-comic/json",
    response_model=ComicResponse
)
async def generate_comic_json(
    payload: PromptRequest
):

    try:

        return generate_comic(
            payload
        )


    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=str(exc)
        ) from exc


# ============================================================
# EXPORT SUCCESS
# ============================================================

@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(

    request: Request,

    pdf_url: str = "/"
):

    return templates.TemplateResponse(

        request=request,

        name="export_success.html",

        context={
            "pdf_url": pdf_url
        }
    )


# ============================================================
# IMAGE TEST ENDPOINT
# ============================================================

@router.get("/test-image")
async def test_image(

    prompt: str =
        "a heroic fox in a colorful comic book forest"
):

    try:

        image_url = generate_image(

            prompt,

            0
        )


        return {

            "ok": True,

            "image_url": image_url
        }


    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=str(exc)
        ) from exc