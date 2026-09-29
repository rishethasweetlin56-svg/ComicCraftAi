from google import genai
from google.genai import types

from .config import settings
from .models import ComicOutline


# ============================================================
# GEMINI CLIENT
# ============================================================

def _client() -> genai.Client:

    if not settings.gemini_api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


# ============================================================
# GENERATE FIVE-PANEL OUTLINE
# ============================================================

def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> ComicOutline:

    prompt = f"""
You are the story-planning AI for ComicCraft.

Create a cohesive five-panel comic outline.

USER STORY:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}


REQUIREMENTS:

1. Create exactly five panels.
2. Number panels 1 through 5.
3. Maintain continuity between panels.
4. The main character must remain visually consistent.
5. Each panel must have a concise title.
6. scene_description must explain what happens visually.
7. image_prompt must be suitable for a Stable Diffusion image generator.
8. Do not put dialogue into image_prompt.
9. Include useful visual details such as:
   - character appearance
   - environment
   - action
   - lighting
   - composition
   - art style
10. Do not create additional panels.

Return only the structured response.
"""

    response = _client().models.generate_content(

        model=settings.gemini_flash_model,

        contents=prompt,

        config=types.GenerateContentConfig(

            temperature=0.8,

            response_mime_type="application/json",

            response_schema=ComicOutline,
        ),
    )


    if not response.text:

        raise RuntimeError(
            "Gemini Flash returned an empty response."
        )


    return ComicOutline.model_validate_json(
        response.text
    )