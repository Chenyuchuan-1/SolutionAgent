IMAGE_EDIT_PROMPT_ZH = """
你正在修改一个解决方案图片集中的单张图片。

原始方案标题：
{solution_title}

当前图片编号：
{image_index}/{total}

当前图片 topic：
{topic_title}

原始 image prompt：
{original_prompt}

用户修改要求：
{edit_instruction}

请保留：

1. 同一 run 的整体视觉风格，以原图为准，不要额外套用与原图无效果。
2. 原始画幅比例、页面边距、标题位置和主题编号。
3. 主要信息层级：左侧依据/输入，中间主流程/架构，右侧输出/价值。
4. 同一图片集的颜色、图标语言、线条粗细、阴影和构图密度。
5. 原始 topic 的核心含义，不要把图片改成另一个 topic。

语言适配：

* 跟随原图和用户修改要求的主要语言。
* 中文方案保持中文短标签。
* 双语方案可保留短双语标签，例如“风险控制 / Risk Control”。
* 不要在图片里加入长段落或复杂说明。

事实与安全约束：

* 重点修改用户指定部分，不要无关重绘。
* 不要新增未经核验的政策编号、标准编号、市场规模、真实公司 Logo、专利结论或论文结论。
* 如果用户要求加入未经核验的数据或来源，只能用“需核验 / Needs verification”表达，不要编造细节。
* 不要改变其他图片的统一风格，不要破坏连续图片集的一致性。
""".strip()

IMAGE_EDIT_PROMPT_EN = """
You are editing one image from a continuous solution image deck.

Solution title:
{solution_title}

Image index:
{image_index}/{total}

Current topic:
{topic_title}

Original image prompt:
{original_prompt}

User edit instruction:
{edit_instruction}

Must preserve:

1. The overall visual style of the same run, following the original image.
2. The original aspect ratio, page margins, title position, and topic number.
3. The main information hierarchy: evidence/input on the left, main process/architecture in the center, output/value on the right.
4. The color palette, icon language, line weight, shadows, and composition density of the same image deck.
5. The core meaning of the original topic. Do not turn the image into a different topic.

Language adaptation:

* Follow the main language of the original image and the user edit instruction.
* English solutions should keep concise English labels.
* Bilingual solutions may keep short bilingual labels, such as “Risk Control / 风险控制”.
* Do not add long paragraphs or complex explanations inside the image.

Factual and safety constraints:

* Focus on the user-specified change. Do not redraw unrelated parts.
* Do not add unverified policy numbers, standard numbers, market sizes, real company logos, patent conclusions, or paper conclusions.
* If the user asks to add unverified data or sources, only express it as “Needs verification”; do not fabricate details.
* Do not change the unified style of the other images, and do not break consistency across the image deck.
""".strip()

IMAGE_EDIT_PROMPT = IMAGE_EDIT_PROMPT_ZH


def get_image_edit_prompt(language: str = "zh") -> str:
    if language == "en":
        return IMAGE_EDIT_PROMPT_EN
    if language == "bilingual":
        return IMAGE_EDIT_PROMPT_ZH + "\n\n--- English Edit Prompt ---\n\n" + IMAGE_EDIT_PROMPT_EN
    return IMAGE_EDIT_PROMPT_ZH
