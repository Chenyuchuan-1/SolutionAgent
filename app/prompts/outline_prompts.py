OUTLINE_GENERATION_PROMPT_ZH = """
请基于以下信息生成“解决方案生成 Agent”的可编辑 Markdown 大纲。

## 输入信息

用户领域：
{domain}

用户目标：
{goal}

应用场景：
{scenario}

用户原始提示词：
{user_prompt}

上传文档解析结果（内部证据，优先使用，但仍需识别不确定项）：
{parsed_documents}

文献使用要求：

* 上传文档解析结果按“文献 1 / 文献 2 / 文献 3 ...”组织，每篇都已经过 DeepSeek 深度归纳。
* 必须在证据地图的学术/专利来源中列出每一篇上传文献，不允许只引用第一篇。
* 必须在总体架构、Topic 设计和详细解决方案中综合使用所有上传文献：每篇至少贡献一个方法论、模块、流程、视觉元素或核验点。
* 如果多篇文献都讨论闭环、贝叶斯优化、自动化实验或材料发现，请区分它们的不同贡献，不要合并成一个泛泛的“上传论文依据”。

联网检索结果（外部证据，必须保留标题、URL、日期、来源类型和可信度）：
{retrieval_results}

用户要求 topic 数量：
{topic_count}

## 输出语言

请自动适配用户语言：

* 如果用户主要使用中文，输出中文。
* 如果用户主要使用英文，输出英文。
* 如果用户明确要求中英文双语或 bilingual，输出中英文双语。
* 双语输出时，标题可使用“中文 / English”，正文可采用“中文描述（English term）”，表格可使用双语表头或单元格中英并列。
* 专有名词、模型名、API 名、机构名可保留原文。

## 事实与证据约束

* 不允许编造政策、法规、标准编号、企业、市场规模、论文结论、专利或引用来源。
* 政策、产业、市场规模、最新动态必须基于检索结果；缺少可靠来源时写“需要核验”或 “Needs verification”。
* 学术结论、产业结论、政策结论和专利结论要分开表达。
* 重要来源必须以 Markdown 链接呈现，保留来源标题、URL、日期、来源类型和可信度。
* 来源之间冲突时，列出冲突点，并标注需要人工核验。

## Markdown 结构要求

输出必须是纯 Markdown，不要包裹代码块。结构必须包含以下部分：

# 解决方案标题 / Solution Title

## 1. 用户需求摘要 / Requirement Summary

用 1–2 段总结用户要解决的问题、目标受众、应用场景、交付物和关键约束。

## 2. 目标与边界 / Goals and Boundaries

用表格列出：目标、非目标、目标受众、关键利益相关方、交付物、约束、成功指标。

## 3. Todo 型任务拆解 / Todo-Style Task Breakdown

使用 checkbox 列表，列出 Agent 已完成/待完成的任务。至少覆盖：

* 需求解析
* 文档解析
* 检索规划
* 政策/产业/学术/专利/新闻检索
* 证据整理
* 方案设计
* 图片脚本生成
* 风险核验

## 4. 证据地图 / Evidence Map

分表列出政策/法规、产业/市场、技术/标准、学术/专利、新闻/竞品来源。

每个表格至少包含：来源标题、来源类型、发布机构、日期、关键结论、可信度、链接、是否需要核验。

## 5. 总体解决方案架构 / Overall Solution Architecture

描述业务、数据、模型、工具、Agent 流程、用户确认节点、图片生成节点和历史归档之间的关系。

## 6. Topic 列表 / Topic List

必须生成 {topic_count} 个 topic。

表格列：编号、Topic、目标、核心问题、需要呈现的图像内容、关键依据、核验状态。

编号必须稳定使用 T01、T02、T03 ...，便于后续图片生成解析。

## 7. 详细解决方案 / Detailed Solution

每个 topic 使用三级标题展开，格式必须稳定：

### T01 Topic 名称

* 核心问题：
* 解决思路：
* 需要的数据/工具/模型：
* 政策/产业/技术/学术依据：
* 关键交付物：
* 可视化表达建议：
* 需要核验：

## 8. 实施路线图 / Implementation Roadmap

按 MVP、内测、试点、上线、迭代列出阶段、任务、负责人角色、输入、输出、时间建议和验收条件。

## 9. 风险矩阵 / Risk Matrix

表格列：风险类型、风险描述、影响、概率、控制措施、预警信号、责任角色。

## 10. 验收指标 / Acceptance Metrics

表格列：指标、定义、目标值、评估方式、数据来源、验收频率。

## 11. 详细解决方案绘图提示词 / Detailed Solution Drawing Prompts

必须按照图片页码 index 为每个 topic 设计独立绘图提示词，后续图片生成只应优先使用本节，而不是直接把“详细解决方案”整段放进图片。

整体原则：

* 这是面向甲方汇报的解决方案图片，不是证据审计页。
* 前 1–2 页可适度呈现行业背景、政策方向、时代趋势和产业痛点；后续页面必须更多聚焦“我们针对问题可以怎么做”的方案流程、系统架构、能力模块、闭环优化和落地路径。
* 图片中文字只做辅助说明，优先使用图形、箭头、流程、模块、矩阵、图标和少量短标签表达。
* 每页建议 4–8 个核心视觉模块，每个模块文字尽量控制在 2–8 个字或一个短语，不要出现长段落。
* 不要在图片中出现“需要核验”“风险提示”“信息来源”“下一步计划”“证据地图”“Manual verification”“Needs verification”等字样。
* 不要生成真实公司 Logo、敏感标识、未经核验的具体政策编号、市场规模或标准编号。

请使用表格，列必须包含：

* 图片编号：固定为 P01、P02、P03 ...，数量等于 {topic_count}
* 对应 Topic：固定引用 T01、T02、T03 ...
* 页面短标题：这一页图片顶部显示的短标题
* 核心方案动作：这一页要表达的 3–5 个“做法”，聚焦解决方案动作而不是资料来源
* 主视觉结构：流程图、架构图、闭环图、矩阵、路线图、价值链或对比图
* 画面布局：左/中/右或上/中/下如何排布模块
* 辅助短标签：允许出现在图中的短词列表，避免长句
* 禁止出现：需要核验、风险提示、信息来源、下一步计划、真实 Logo、未经核验数字

每个 Pxx 必须和 Txx 一一对应，不要合并，不要跳号。

## 12. 人工核验清单 / Manual Verification Checklist

列出所有需要人工核验的政策、市场数据、标准编号、企业信息、论文/专利结论和敏感表述。
""".strip()

OUTLINE_GENERATION_PROMPT_EN = """
Generate an editable Markdown outline for a “Solution Generation Agent” based on the information below.

## Input Information

User domain:
{domain}

User goal:
{goal}

Application scenario:
{scenario}

Original user prompt:
{user_prompt}

Parsed uploaded documents (internal evidence; prioritize them while still identifying uncertainty):
{parsed_documents}

Document usage requirements:

* Parsed uploaded documents are organized as “Document 1 / Document 2 / Document 3 ...”, and each has a DeepSeek deep summary.
* List every uploaded document in the academic/patent evidence map. Do not cite only the first document.
* Use all uploaded documents across the overall architecture, topic design, and detailed solution. Each document should contribute at least one methodology, module, workflow, visual element, or verification item.
* If multiple documents discuss closed loops, Bayesian optimization, automated experimentation, or material discovery, distinguish their different contributions instead of merging them into a generic “uploaded paper evidence”.

Web retrieval results (external evidence; preserve titles, URLs, dates, source types, and confidence):
{retrieval_results}

Requested topic count:
{topic_count}

## Output Language

Adapt to the user’s language:

* If the user mainly writes in English, output in English.
* If the user mainly writes in Chinese, output in Chinese.
* If the user explicitly asks for bilingual / Chinese-English output, output a bilingual structure.
* For bilingual output, headings may use “中文 / English”; body text may use “Chinese description (English term)”; tables may use bilingual headers or bilingual text in the same cell.
* Keep proper nouns, model names, API names, and institution names in their original form when appropriate.

## Factual and Evidence Constraints

* Do not fabricate policies, regulations, standard numbers, companies, market sizes, paper conclusions, patents, or citation sources.
* Policies, industry trends, market size, and latest updates must be based on retrieval results. If reliable sources are missing, write “Needs verification”.
* Keep academic, industry, policy, and patent conclusions separate.
* Important sources must be presented as Markdown links, preserving source title, URL, date, source type, and confidence.
* If sources conflict, list the conflict and mark it as requiring manual verification.

## Markdown Structure Requirements

Output pure Markdown only. Do not wrap the output in a code block. The structure must include:

# Solution Title

## 1. Requirement Summary

Use 1–2 paragraphs to summarize the problem, target audience, application scenario, deliverables, and key constraints.

## 2. Goals and Boundaries

Use a table to list: goals, non-goals, target audience, key stakeholders, deliverables, constraints, and success metrics.

## 3. Todo-Style Task Breakdown

Use a checkbox list to show completed and pending Agent tasks. Cover at least:

* Requirement parsing
* Document parsing
* Retrieval planning
* Policy / industry / academic / patent / news retrieval
* Evidence organization
* Solution design
* Image script generation
* Risk verification

## 4. Evidence Map

Use separate tables for policy/regulation, industry/market, technology/standards, academic/patent, and news/competitor sources.

Each table must include at least: source title, source type, publisher, date, key conclusion, confidence, link, and verification status.

## 5. Overall Solution Architecture

Describe the relationship between business flow, data, models, tools, Agent workflow, user confirmation, image generation, and history archiving.

## 6. Topic List

Generate exactly {topic_count} topics.

Table columns: index, topic, objective, core problem, image content to present, key evidence, verification status.

Use stable IDs T01, T02, T03 ... so downstream image generation can parse them reliably.

## 7. Detailed Solution

Use a stable third-level heading for each topic:

### T01 Topic Name

* Core problem:
* Solution approach:
* Required data / tools / models:
* Policy / industry / technical / academic evidence:
* Key deliverables:
* Visualization suggestion:
* Needs verification:

## 8. Implementation Roadmap

List phases by MVP, internal test, pilot, launch, and iteration. Include tasks, owner role, inputs, outputs, timeline suggestion, and acceptance conditions.

## 9. Risk Matrix

Table columns: risk type, risk description, impact, probability, control measure, warning signal, owner role.

## 10. Acceptance Metrics

Table columns: metric, definition, target value, evaluation method, data source, acceptance frequency.

## 11. Detailed Solution Drawing Prompts

Design an independent drawing prompt for each topic by image page index. Downstream image generation should prioritize this section instead of directly rendering the full Detailed Solution text.

Overall principles:

* These are client-facing solution slides, not evidence audit pages.
* The first 1–2 pages may briefly show industry background, policy direction, macro trend, and pain points. The remaining pages must focus more on what we can do to solve the problems: solution flows, system architecture, capability modules, closed-loop optimization, and implementation paths.
* Text inside images should only be auxiliary. Prefer visuals, arrows, workflows, modules, matrices, icons, and concise labels.
* Each page should use 4–8 core visual modules. Keep each text label to a short phrase, not paragraphs.
* Do not show “Needs verification”, “risk warning”, “information sources”, “next steps”, “evidence map”, “Manual verification”, or similar text inside images.
* Do not generate real company logos, sensitive marks, unverified policy numbers, market sizes, or standard numbers.

Use a table with these required columns:

* Image index: fixed as P01, P02, P03 ... and the count must equal {topic_count}
* Related topic: fixed references T01, T02, T03 ...
* Short page title: short title shown at the top of the image page
* Core solution actions: 3–5 concrete actions or methods, focused on the solution rather than sources
* Main visual structure: flowchart, architecture diagram, closed-loop diagram, matrix, roadmap, value chain, or comparison
* Layout: how modules are arranged left/center/right or top/middle/bottom
* Auxiliary short labels: short labels allowed inside the image
* Forbidden content: needs verification, risk warnings, information sources, next steps, real logos, unverified numbers

Each Pxx must map one-to-one to Txx. Do not merge pages or skip indexes.

## 12. Manual Verification Checklist

List all policies, market data, standard numbers, company information, paper/patent conclusions, and sensitive statements that require manual verification.
""".strip()

OUTLINE_GENERATION_PROMPT = OUTLINE_GENERATION_PROMPT_ZH


def get_outline_generation_prompt(language: str = "zh") -> str:
    if language == "en":
        return OUTLINE_GENERATION_PROMPT_EN
    if language == "bilingual":
        return OUTLINE_GENERATION_PROMPT_ZH + "\n\n--- English Prompt Version ---\n\n" + OUTLINE_GENERATION_PROMPT_EN
    return OUTLINE_GENERATION_PROMPT_ZH
