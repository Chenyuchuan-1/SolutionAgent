IMAGE_STYLE_LOCK_PROMPT_ZH = """
统一视觉风格：

内容优先的企业级解决方案信息图，适合放入咨询报告、项目申报书和路演 PPT。画面应清晰、专业，重点表达“如何解决问题”的方案逻辑、关键模块、业务流程、系统架构、闭环优化和交付成果，而不是追求玻璃拟态特效。

同一 run 内所有图片必须保持一致：

* 画幅比例、页面边距、标题位置、编号方式一致。
* 配色、字体感觉、图标系统、线条粗细、箭头样式和模块布局一致。
* 构图密度适中但保持可读，优先使用清晰分区、流程图、架构图、矩阵、时间线和图标模块。
* 每页只显示当前图片页码，例如 P01；不要额外生成无关编号。
* 中心区域展示主流程、解决方案架构或业务闭环；侧边区域展示输入、能力模块、输出价值或交付物。
* 每张图建议包含 4–8 个视觉模块，文字只作为辅助短标签，不要堆长段落。
* 适合放入产品汇报、项目申报、企业咨询方案或路演 PPT。

内容安全与事实约束：

* 避免真实公司 Logo、未经授权品牌标识和敏感信息。
* 不要展示未经核验的具体政策编号、市场规模、标准编号、论文/专利结论。
* 不要在图片中出现“需要核验”“风险提示”“信息来源”“下一步计划”等文字。
* 可以使用必要的短文本标签，确保结构明确、可用于甲方汇报。
""".strip()

IMAGE_STYLE_LOCK_PROMPT_EN = """
Unified visual style:

Use a content-first enterprise solution infographic style suitable for consulting reports, project proposals, and roadshow slides. The image should be clear and professional, focusing on how to solve the problems: solution logic, key modules, business workflows, system architecture, closed-loop optimization, and deliverables instead of glassmorphism effects.

All images in the same run must remain consistent:

* Keep aspect ratio, page margins, title position, and numbering method consistent.
* Keep color palette, typography feel, icon system, line weight, arrow style, module layout, and information hierarchy consistent.
* Use a readable composition with clear sections, flowcharts, architecture diagrams, matrices, timelines, and icon modules.
* Show only the current page index, such as P01. Do not add unrelated extra numbering.
* The center area should show the main process, solution architecture, or business loop; side areas should show inputs, capability modules, output value, or deliverables.
* Each image should contain about 4–8 visual modules. Text should be auxiliary short labels, not long paragraphs.
* The image should be suitable for product briefings, project proposals, enterprise consulting decks, or roadshow slides.

Content safety and factual constraints:

* Avoid real company logos, unauthorized brand marks, and sensitive information.
* Do not show unverified policy numbers, market sizes, standard numbers, paper conclusions, or patent conclusions.
* Do not show text such as “Needs verification”, “risk warning”, “information sources”, or “next steps” inside images.
* Use necessary short labels to make the structure clear and presentation-ready.
""".strip()

SINGLE_TOPIC_IMAGE_PROMPT_TEMPLATE_ZH = """
你要为一个连续解决方案图片集生成第 {index}/{total} 张图片。

最高优先级：

* 必须严格按照“当前 topic 内容”里的页面短标题、核心方案动作、主视觉结构、画面布局和辅助短标签生成。
* 不要把证据地图、详细解决方案长段落、核验清单、风险矩阵或其他 topic 内容画进当前页。
* 如果“当前 topic 内容”和通用风格要求冲突，以“当前 topic 内容”为准。

当前图片页码：
{image_index}

全局方案标题：
{solution_title}

当前 topic：
{topic_title}

当前 topic 内容：
{topic_content}

统一风格锁定：
{style_lock_prompt}

画幅：
{aspect_ratio}

语言适配：

* 跟随方案标题和 topic 内容的主要语言。
* 如果内容主要是中文，图片中文字使用简短中文。
* 如果内容为中英文双语，图片可以使用短双语标题，例如“政策依据 / Policy Evidence”。
* 不要在图片中放长段落，文字只做辅助说明：模块标题、短标签、步骤名、能力名或交付物名。

图片要求：

1. 必须在页面角落清晰显示当前图片页码 “{image_index}”，不要额外显示 “{index}/{total}”。
2. 页面主标题必须使用当前 topic 内容中的“页面短标题”或当前 topic 标题。
3. 主画面必须使用当前 topic 内容中的“主视觉结构”。
4. 模块位置必须遵循当前 topic 内容中的“画面布局”。
5. 图中文字优先使用当前 topic 内容中的“辅助短标签”。
6. 使用企业级解决方案信息图风格，内容清晰、模块丰富、适合汇报；不要把玻璃拟态作为生成图片的主要风格。
7. 保持与同一方案其他图片在布局、色彩、编号、图标语言和字体感上的一致性。
8. 优先使用图形、箭头、图标、流程、矩阵和分层模块表达，避免空洞装饰图。
9. 不要生成真实公司 Logo、敏感标识、未经核验的政策编号、市场规模或标准编号。
10. 不要在图中出现“需要核验”“风险提示”“信息来源”“下一步计划”等文字。
11. 输出应适合放入产品汇报、项目申报、企业咨询方案或路演 PPT。
""".strip()

SINGLE_TOPIC_IMAGE_PROMPT_TEMPLATE_EN = """
You are generating image {index}/{total} for a continuous solution image deck.

Highest priority:

* Strictly follow the short page title, core solution actions, main visual structure, layout, and auxiliary labels in “Topic content”.
* Do not render evidence maps, long detailed-solution paragraphs, verification checklists, risk matrices, or content from other topics on the current page.
* If “Topic content” conflicts with general style rules, follow “Topic content”.

Current image page index:
{image_index}

Solution title:
{solution_title}

Current topic:
{topic_title}

Topic content:
{topic_content}

Style lock:
{style_lock_prompt}

Aspect ratio:
{aspect_ratio}

Language adaptation:

* Follow the main language of the solution title and topic content.
* If the content is mainly English, use concise English text in the image.
* If the content is bilingual, short bilingual labels are acceptable, such as “Policy Evidence / 政策依据”.
* Do not put long paragraphs in the image. Text should only be auxiliary: module titles, short labels, step names, capability names, or deliverable names.

Image requirements:

1. Clearly show only the current image page index “{image_index}” in a page corner. Do not additionally show “{index}/{total}”.
2. The main page title must use the short page title from Topic content or the current topic title.
3. The main visual must follow the main visual structure from Topic content.
4. Module placement must follow the layout from Topic content.
5. Text inside the image should prioritize the auxiliary short labels from Topic content.
6. Use an enterprise solution infographic style that is clear, modular, information-rich, and presentation-ready. Do not make glassmorphism the main generated-image style.
7. Keep layout, colors, numbering, icon language, and typography feel consistent with the other images in the same solution.
8. Prefer graphics, arrows, icons, workflows, matrices, and layered modules. Avoid decorative empty visuals.
9. Do not generate real company logos, sensitive marks, unverified policy numbers, market sizes, or standard numbers.
10. Do not show “Needs verification”, “risk warning”, “information sources”, or “next steps” inside the image.
11. The output should be suitable for product briefings, project proposals, enterprise consulting decks, or roadshow slides.
""".strip()

IMAGE_STYLE_LOCK_PROMPT = IMAGE_STYLE_LOCK_PROMPT_ZH
SINGLE_TOPIC_IMAGE_PROMPT_TEMPLATE = SINGLE_TOPIC_IMAGE_PROMPT_TEMPLATE_ZH


def get_image_style_lock_prompt(language: str = "zh") -> str:
    if language == "en":
        return IMAGE_STYLE_LOCK_PROMPT_EN
    if language == "bilingual":
        return IMAGE_STYLE_LOCK_PROMPT_ZH + "\n\n--- English Style Lock ---\n\n" + IMAGE_STYLE_LOCK_PROMPT_EN
    return IMAGE_STYLE_LOCK_PROMPT_ZH


def get_single_topic_image_prompt_template(language: str = "zh") -> str:
    if language == "en":
        return SINGLE_TOPIC_IMAGE_PROMPT_TEMPLATE_EN
    if language == "bilingual":
        return SINGLE_TOPIC_IMAGE_PROMPT_TEMPLATE_ZH + "\n\n--- English Template ---\n\n" + SINGLE_TOPIC_IMAGE_PROMPT_TEMPLATE_EN
    return SINGLE_TOPIC_IMAGE_PROMPT_TEMPLATE_ZH
