# Solution Agent

面向政策、产业、技术调研和方案可视化的“解决方案生成 Agent”。后端使用 FastAPI，前端沿用 `solution-agent-demo` 的卡片式、玻璃拟态 SaaS 产品界面。

## 功能

- 上传 PDF、Word、Markdown、CSV、Excel 文件，并保存到 run 目录。
- Agent 按 todo 流程执行输入解析、文档解析、多源检索、证据排序、Markdown 大纲生成。
- 大纲先返回前端，可编辑、预览表格/链接/标题/列表，用户确认后再生成图片。
- 图片生成使用统一 style lock，同一 run 内保存 topic prompt、图片、版本和单图修改历史。
- 无 OpenAI API key 时文本大纲可使用 mock 兜底；图片生成默认必须真实调用图片模型。只有显式设置 `MOCK_IMAGE_FALLBACK=true` 时才会生成 SVG mock。

## 快速启动

```bash
cd solution-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

打开：`http://127.0.0.1:8000`

## 环境变量

```env
OPENAI_API_KEY=
OPENAI_TEXT_MODEL=gpt-5.5
OPENAI_TEXT_URL=
OPENAI_IMAGE_MODEL=gpt-image-2
OPENAI_IMAGE_URL=
OPENAI_IMAGE_EDIT_URL=
OPENAI_IMAGE_API_KEY=
OPENAI_IMAGE_AUTH_ENABLED=true
OPENAI_IMAGE_INCLUDE_SIZE=false
OPENAI_IMAGE_RESPONSE_FORMAT=
TAVILY_API_KEY=
EXA_API_KEY=
EXA_SEARCH_TYPE=auto
EXA_NUM_RESULTS=10
EXA_CONTENT_MODE=highlights
BRAVE_API_KEY=
SERPAPI_API_KEY=
SEARXNG_ENDPOINT=
STORAGE_ROOT=storage/runs
DEFAULT_IMAGE_SIZE=1536x1024
DEFAULT_IMAGE_QUALITY=high
IMAGE_GENERATION_CONCURRENCY=3
MOCK_IMAGE_FALLBACK=false
REQUEST_TIMEOUT=300
MINERU_MCP_URL=https://mineru.net/api/v4/extract/task
MINERU_API_TOKEN=
MINERU_MODEL_VERSION=vlm
MINERU_LANGUAGE=ch
MINERU_ENABLE_FORMULA=true
MINERU_ENABLE_TABLE=true
MINERU_IS_OCR=false
MINERU_TIMEOUT=600
MINERU_POLL_INTERVAL=5
```

如果供应商分别提供 endpoint，可以配置 `OPENAI_TEXT_URL=https://.../v1` 或 `https://.../v1/chat/completions`；图片可以配置 `OPENAI_IMAGE_URL=http://148.153.72.70/v1` 或完整 `http://148.153.72.70/v1/images/generations`。单图修改会优先使用 `OPENAI_IMAGE_EDIT_URL`，未配置时会从图片生成地址自动推导 `/v1/images/edits`。

图片生成链路默认不会静默 fallback 到 SVG。请确保 `.env` 中配置了 `OPENAI_IMAGE_MODEL` 和 `OPENAI_IMAGE_URL`。当前 `http://148.153.72.70/v1/images/generations` 实测无鉴权会返回 `401 No API Key found`，因此应设置 `OPENAI_IMAGE_AUTH_ENABLED=true`，并使用 `OPENAI_IMAGE_API_KEY` 或 `OPENAI_API_KEY`。如仅需本地 UI 演示，可设置 `MOCK_IMAGE_FALLBACK=true`。

多张 topic 图片会按 `IMAGE_GENERATION_CONCURRENCY` 受限并发生成，默认 `3`。如果供应商接口允许更高并发，可以调大；如果出现限流、排队过久或偶发失败，建议调小到 `1-2`。

Exa 默认使用官方推荐的 `/search` raw JSON 形态：`type=auto`、`numResults=10`、`contents.highlights=true`。`EXA_CONTENT_MODE` 可选 `highlights`、`text`、`summary`，Agent 检索默认推荐 `highlights` 以控制 token 成本。

## API

- `POST /api/runs` 创建 run。
- `POST /api/upload` 上传文件，参数 `run_id` 和 `files`。
- `POST /api/outline` 执行阶段 1-6，返回 `outline_markdown`、`todos`、`topics`、`retrieval_sources`。
- `POST /api/images` 使用用户确认后的 Markdown 生成 topic prompts 和图片。
- `POST /api/image-edit` 对单张图片生成新版本并保存 edit history。
- `GET /api/history` 获取历史列表。
- `GET /api/history/{run_id}` 获取完整 run 记录。
- `GET /api/runs/{run_id}/status` 获取当前进度。

## 归档结构

每次运行会保存到 `storage/runs/{run_id}/`：

```text
meta.json
input/user_input.json
uploads/
parsed/parsed_documents.json
retrieval/search_plan.json
retrieval/search_results.json
outline/outline.md
outline/outline_versions/
prompts/outline_prompt.txt
prompts/topic_prompts.json
images/
edits/
```

`meta.json` 包含 run_id、title、created_at、updated_at、domain、goal、scenario、topic_count、outline_markdown、topics、images、retrieval_sources、uploaded_files、edit_history。

## OpenAI 接入

所有 OpenAI 调用都封装在 `app/models/openai_client.py`，业务路由不直接接触 API key。

- 文本大纲优先调用 Responses API，模型由 `app/models/registry.py` 的 `solution_planner` 管理。
- 图片生成调用 Image API，模型由 `image_generator` 管理。
- 单图修改通过 image edit 接口执行，会把当前图片文件以 multipart `image` 字段传给模型，并携带用户修改 prompt 生成新版。

## 检索系统

`app/services/retrieval_service.py` 会生成 `search_plan.json`，并按类别调度多源工具：

- 通用 AI 搜索：Tavily、Exa、Brave。
- SERP 结构化：SerpApi。
- 网页正文抽取预留：Jina Reader。
- 学术：OpenAlex、Crossref、PubMed、Semantic Scholar、arXiv。
- 政策：gov/gov.cn/europa 等域名优先的 `PolicySearchTool`。
- 产业：报告、白皮书、企业和新闻的 `IndustrySearchTool`。
- 未配置 API key 时返回人工核验搜索入口，不编造政策、市场规模、标准编号或论文结论。

所有检索结果标准化为 `source_id/title/url/published_date/source_type/publisher/snippet/content/tool/query/relevance_score/credibility_score/freshness_score/confidence/need_verification`，并按：

```text
final_score = 0.45 * relevance_score + 0.25 * credibility_score + 0.20 * freshness_score + 0.10 * source_diversity_score
```

排序。

## MinerU 接入

`tools/document/mineru_parser.py` 已接入 MinerU v4 服务 API。PDF 上传后会走官方本地文件流程：申请签名上传 URL、PUT 上传文件、轮询 batch 结果、下载解析 zip，并提取 `full.md` 和 `content_list.json` 转成 `title/chunks/tables/figures`。

`MINERU_MCP_URL` 可以填 `https://mineru.net/api/v4/extract/task`，代码会自动推导同域的 `/file-urls/batch` 和 `/extract-results/batch/{batch_id}`。`MINERU_API_TOKEN` 必须配置，否则 PDF 解析会返回失败状态，不再使用 mock。

## 当前仍未完全落地的预留能力

- 网页正文抽取的 Jina Reader 仍是预留说明，当前检索主要依赖搜索结果 snippet/content。
- 部分检索源依赖 API key；未配置时会降级为可人工核验的搜索入口或较弱结果。

## 前端说明

前端位于 `frontend/`，使用原生 HTML/CSS/JS，保持运行简单：

- 左侧历史记录、新建方案。
- Hero 与功能卡片。
- 拖拽/点击上传文件 chip。
- Markdown 编辑/预览，使用 `marked` + `DOMPurify` 做 sanitize。
- 生成进度弹窗和按钮 loading。
- 图片主视图、左右箭头、缩略图、单图对话式修改。
