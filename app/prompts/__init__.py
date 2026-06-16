from app.prompts.edit_prompts import IMAGE_EDIT_PROMPT_EN, IMAGE_EDIT_PROMPT_ZH, get_image_edit_prompt
from app.prompts.image_prompts import (
    IMAGE_STYLE_LOCK_PROMPT_EN,
    IMAGE_STYLE_LOCK_PROMPT_ZH,
    SINGLE_TOPIC_IMAGE_PROMPT_TEMPLATE_EN,
    SINGLE_TOPIC_IMAGE_PROMPT_TEMPLATE_ZH,
    get_image_style_lock_prompt,
    get_single_topic_image_prompt_template,
)
from app.prompts.outline_prompts import OUTLINE_GENERATION_PROMPT_EN, OUTLINE_GENERATION_PROMPT_ZH, get_outline_generation_prompt
from app.prompts.system_prompts import (
    SOLUTION_AGENT_SYSTEM_PROMPT_EN,
    SOLUTION_AGENT_SYSTEM_PROMPT_ZH,
    detect_prompt_language,
    get_solution_system_prompt,
)
