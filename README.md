# SolutionAgent使用说明

# **Solution Agent 用户使用手册**

demo示意图：

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MTZmZWZlYjA0NGYzMWNiMDE3NjQ4Y2ViOWRmZmQ3ZmRfZmFhYzM0MjM2ZTQ2ODE2MWI3MzAwYmIwOTdkNjkzNTVfSUQ6NzY1MTkwNDg1MDQ3MDY4NTY0MV8xNzgxNjAwMzU3OjE3ODE2ODY3NTdfVjM)

解决方案示例：

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MjE5OGQyOTEyZGY0NjNlNGEzNzM1N2RmZDVlZGI2MzdfNDg3Nzc4ODcyMzM5OGU5ZjQ1N2NiMjIyZWU5NGMyMjJfSUQ6NzY1MTkwNDk0NjQ0ODIyMzQ3MF8xNzgxNjAwMzU3OjE3ODE2ODY3NTdfVjM)

解决方案信息来源示例：

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NThlODA1YzZlNjE2MzE2Njc1YjllNzBkYWIyZGVkN2ZfNjRmZTY2MTY0MGM2ZTAzNDk0NjA3ZWI0ZTA4OGRhOWRfSUQ6NzY1MTkwNTAxODQ2OTk5MzQ0MF8xNzgxNjAwMzU3OjE3ODE2ODY3NTdfVjM)

图片提示词示例：

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MDFmZTQ5Njc2MjI5YWQ0Y2EwM2ZkYzhkNzVjOTEwNTVfMzQ0MjQ4YmZmZTBjMzA1NTA0M2Y2NWYxNThhZjQ3ZGVfSUQ6NzY1MTkwNTExNjUxMTE0NTIwM18xNzgxNjAwMzU3OjE3ODE2ODY3NTdfVjM)

前端图片展示窗口示例：

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MWJjYjhhZjE4ZDA0OWZiNzM4NWMyMTE0YWEzZjE0OTBfMDViNDQ2ZTFjZWM5N2FkNmM4NDBlNDJkNDRiMmFlNDVfSUQ6NzY1MTkwNTI2NjEyMTAxODU3OF8xNzgxNjAwMzU3OjE3ODE2ODY3NTdfVjM)

生成的图片示例：

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NjU0NjI3OTViZmE3ZDgzM2I5MmFhZmI5NGYwZTU4OWZfMGM1MDQ4Y2I1NmI0MzJlMzM0YzdhMWNlNDk2YTBjNzJfSUQ6NzY1MTkwNTU0OTM2MTcyODcwMF8xNzgxNjAwMzU3OjE3ODE2ODY3NTdfVjM)

本文档面向使用者、方案顾问、产品运营和项目交付人员，说明如何启动和使用 Solution Agent，如何配置后端 `.env`，如何理解生成出来的解决方案 Markdown，图片提示词从哪里来，以及如何按项目需要修改提示词工程。注意确认解决方案 Markdown，以及绘图提示词符合需求后再生成图片。**单任务时常大约10\-15min，成本大约5\-10元/次**。尽量想好了之后，确定具体需求后再提交哈。

**前端也可以自己DIY（本人不擅长前端设计），大家可以构建属于自己的解决方案助手和工作平台！**



SolutionAgent 的核心流程是：

```Plain Text
输入需求 + 上传文档
-> 文档解析与网页检索
-> DeepSeek 对文档/检索结果做深度归纳
-> GPT-5.5 生成可编辑 Markdown 解决方案大纲
-> 用户在前端确认或编辑 Markdown
-> 按第 11 节绘图提示词生成每页图片 prompt
-> 调用图片模型生成连续解决方案图片
-> 支持单图基于原图继续编辑
```

## **1\. 快速启动**

项目地址：/fs\_mol/cyc/code/SolutionAgent/solution\-agent

进入项目目录：

```Bash
cd solution-agent
```

安装依赖并启动后端：

```Bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

浏览器打开：

```Plain Text
http://127.0.0.1:8000
```

如果需要本地启动 SearXNG 检索服务：（具体网页查询如何本地部署SearXNG）

```Bash
docker compose up -d
```

然后在 `.env` 中配置：

```Plain Text
SEARXNG_ENDPOINT=http://localhost:8080/search
```



## **2\. 前端交互式使用说明**

### **2\.1 创建新方案**

1. 点击左侧或页面中的新建入口。

2. 填写输入需求：

    - `Domain / 领域`：行业或业务对象，例如“钙钛矿太阳能电池”。

    - `Goal / 目标`：希望 Agent 完成的目标，例如“AI Agent 赋能企业智能化转型”。

    - `Scenario / 应用场景`：使用场景，例如“企业汇报、科研平台设计、产业降本增效”。

    - `Text Prompt / 文本提示词`：用户更具体的要求，例如需要调研政策、产业、企业、科研痛点，并输出 8 张图片。

3. 设置 `Topics / Images` 数量，支持 5\-15 个 topic。

4. 选择图片比例和图片尺寸：

    - 图片比例用于提示词中的构图要求。

    - 图片尺寸会传给图片模型的 `size` 参数，例如 `1536x1024`、`3840x2160`。

### **2\.2 上传文档**

支持上传：

- PDF

- Word

- Markdown

- CSV

- Excel

PDF 会优先调用 MinerU API 进行真实解析，解析结果会保存到：

```Plain Text
storage/runs/{run_id}/parsed/parsed_documents.json
storage/runs/{run_id}/parsed/parsed_documents_summary.json
```

`parsed_documents_summary.json` 是每篇文档进入 text LLM 前的压缩结果。系统会对每篇文献单独做 DeepSeek 深度归纳，并构造：

```Plain Text
storage/runs/{run_id}/parsed/parsed_documents_outline_context.md
```

这个文件可以用来检查“每篇文献是否都进入了最终大纲生成上下文”，以及进入的内容。



### **2\.3 生成解决方案大纲**

点击“生成解决方案大纲”后，系统会执行：

```Plain Text
需求解析
-> 文档解析
-> 多源联网检索
-> 文献和检索结果深度归纳
-> GPT-5.5 生成 Markdown 大纲
```

生成后，前端会显示“可编辑 Markdown 大纲”。此时用户可以直接修改：

- topic 名称

- 表格内容

- 解决方案细节

- 第 11 节图片绘图提示词

- 风格锁定描述

- 人工核验清单

修改后的 Markdown 会作为后续图片生成的依据。



### **2\.4 编辑和预览 Markdown**

大纲区域提供两个模式：

- `编辑`：直接编辑 Markdown 原文。

- `预览`：查看 Markdown 渲染效果，支持表格、标题、列表、链接等。

建议在生成图片前重点检查：

```Plain Text
## 6. Topic 列表
## 7. 详细解决方案
## 11. 详细解决方案绘图提示词
```

第 11 节是后续图片生成最关键的部分。



### **2\.5 生成解决方案图片**

点击“确认并生成解决方案图片”后，系统会：

```Plain Text
读取当前前端 Markdown
-> 优先解析第 11 节 P01/P02/P03... 表格
-> 为每一页构造独立 image prompt
-> 合并统一风格锁定
-> 按并发数调用图片模型
-> 保存成功图片和失败记录
```

生成结果会保存到：

```Plain Text
storage/runs/{run_id}/images/
storage/runs/{run_id}/prompts/topic_prompts.json
storage/runs/{run_id}/images/parsed_drawing_topics.json
storage/runs/{run_id}/images/image_errors.json
```

其中：

- `parsed_drawing_topics.json`：系统从第 11 节解析出的 P01\-Pxx 结构。

- `topic_prompts.json`：每张图真实送给图片模型的最终 prompt。

- `image_errors.json`：单张图片失败时的错误记录。

如果某一张失败，系统会保留其他成功图片，不会让整批直接 500。



### **2\.6 下载结果**

前端支持：

- 下载当前 Markdown 大纲：`下载 MD`

- 下载 HTML 版本：`下载 HTML`

- 下载当前图片

- 下载全部图片 ZIP

对应后端导出接口在：

```Plain Text
app/api/exports.py
```



### **2\.7 单图对话式修改**

选择某一张图片后，可以在右侧输入修改要求，例如：

```Plain Text
把右侧 KPI 仪表区域放大，减少底部文字，保留 P05 页码和整体风格。
```

系统会使用 image edit/inpaint 链路：

```Plain Text
原始图片文件 + 原始 prompt + 用户修改指令
-> 图片编辑模型
-> 生成新版图片
-> 保存版本历史
```

单图修改结果会记录到：

```Plain Text
storage/runs/{run_id}/edits/
meta.json -> edit_history
```



## **3\. 后端\`\.env\` 配置说明**

`.env` 从 `.env.example` 复制得到：

```Bash
cp .env.example .env
```



### **3\.1 文本大模型配置**

```Plain Text
OPENAI_API_KEY=
OPENAI_TEXT_MODEL=Vendor2/GPT-5.5
OPENAI_TEXT_URL=https://api.gpugeek.com/v1/chat/completions
OPENAI_BASE_URL=
```

说明：

- `OPENAI_API_KEY`：文本模型、DeepSeek 总结模型、图片模型可共用的主 key。使用首云的api就可以。

- `OPENAI_TEXT_MODEL`：生成解决方案大纲的模型，当前GPT\-5\.5。

- `OPENAI_TEXT_URL`：OpenAI 兼容的 chat completions 地址。可以填完整 `/chat/`

- `OPENAI_BASE_URL`：SDK 模式下的 OpenAI base URL。当前如果使用 `OPENAI_TEXT_URL`，会优先走直接 HTTP 调用。

文本大纲生成调用位置：

```Plain Text
app/models/openai_client.py -> generate_outline()
```



### **3\.2 DeepSeek 文档/网页总结配置**

```Plain Text
DEEPSEEK_SUMMARY_BASE_URL=https://api.gpugeek.com/v1
DEEPSEEK_SUMMARY_MODEL=Vendor3/DeepSeek-V4-Flash
```

说明：

- 文档压缩和网页检索压缩使用 DeepSeek。

- API key 使用 `OPENAI_API_KEY`。

- 每篇 PDF 单独总结。

- 网页检索每 5 条为一组 batch 总结。

总结调用位置：

```Plain Text
app/models/openai_client.py -> summarize_with_deepseek()
app/services/outline_service.py -> _deep_summarize_document()
app/services/outline_service.py -> _deep_summarize_source_batch()
```



### **3\.3 图片模型配置**

```Plain Text
OPENAI_IMAGE_MODEL=GPT-image-2
OPENAI_IMAGE_URL=http://148.153.72.70/v1/images/generations
OPENAI_IMAGE_EDIT_URL=
OPENAI_IMAGE_API_KEY=
OPENAI_IMAGE_AUTH_ENABLED=true
OPENAI_IMAGE_INCLUDE_SIZE=false
OPENAI_IMAGE_RESPONSE_FORMAT=
DEFAULT_IMAGE_SIZE=1536x1024
DEFAULT_IMAGE_QUALITY=high
IMAGE_GENERATION_CONCURRENCY=3
MOCK_IMAGE_FALLBACK=false
REQUEST_TIMEOUT=1200
```

说明：

- `OPENAI_IMAGE_MODEL`：图片生成和图片编辑模型。

- `OPENAI_IMAGE_URL`：图片生成 endpoint。可以是 `/v1`，也可以是完整 `/v1/images/generations`。

- `OPENAI_IMAGE_EDIT_URL`：图片编辑 endpoint。为空时，系统会从图片生成地址推导 `/v1/images/edits`。

- `OPENAI_IMAGE_API_KEY`：图片模型独立 key；为空时使用 `OPENAI_API_KEY`。

- `OPENAI_IMAGE_AUTH_ENABLED`：是否加 Authorization Bearer 头。

- `OPENAI_IMAGE_INCLUDE_SIZE`：是否强制把 `size` 传给图片接口。当前代码只要有 size 就会传入。

- `OPENAI_IMAGE_RESPONSE_FORMAT`：如果供应商要求指定返回格式，可填 `b64_json` 等；为空则不传。

- `DEFAULT_IMAGE_SIZE`：默认图片大小。

- `DEFAULT_IMAGE_QUALITY`：默认图片质量。

- `IMAGE_GENERATION_CONCURRENCY`：多张图片并发生成数量。

- `MOCK_IMAGE_FALLBACK=false`：默认不允许静默生成 SVG mock，避免误以为调用了真实模型。

- `REQUEST_TIMEOUT`：请求超时时间。图片生成较慢时建议设置大一些。

图片调用位置：

```Plain Text
app/models/openai_client.py -> generate_image()
app/models/openai_client.py -> edit_image()
```



### **3\.4 检索配置**

```Plain Text
TAVILY_API_KEY=
EXA_API_KEY=
EXA_SEARCH_TYPE=auto
EXA_NUM_RESULTS=20
EXA_CONTENT_MODE=highlights
BRAVE_API_KEY=
SERPAPI_API_KEY=
SEARXNG_ENDPOINT=
```

说明：

- 开源信息检索工具我只做了几个示例，大家可以按照自己的需求添加更多更好的信息源，添加在tools里即可

- `TAVILY_API_KEY`：Tavily 搜索。

- `EXA_API_KEY`：Exa 搜索。

- `EXA_SEARCH_TYPE`：Exa 搜索类型，默认 `auto`。

- `EXA_NUM_RESULTS`：Exa 返回结果数量。

- `EXA_CONTENT_MODE`：可选 `highlights`、`text`、`summary`。

- `BRAVE_API_KEY`：Brave 搜索。

- `SERPAPI_API_KEY`：SerpApi。

- `SEARXNG_ENDPOINT`：本地或远程 SearXNG 搜索接口。

检索结果会保存到：

```Plain Text
storage/runs/{run_id}/retrieval/search_plan.json
storage/runs/{run_id}/retrieval/search_results.json
storage/runs/{run_id}/retrieval/search_results_summary.json
storage/runs/{run_id}/retrieval/search_results_outline_context.md
```

`search_results_outline_context.md` 是实际进入 text LLM 的网页检索上下文。



### **3\.5 MinerU PDF 解析配置**

```Plain Text
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

说明：

- `MINERU_API_TOKEN` 必须配置，否则 PDF 无法真实解析。

- `MINERU_MODEL_VERSION=vlm` 适合图文混合 PDF。

- `MINERU_ENABLE_TABLE=true` 会解析表格。

- `MINERU_ENABLE_FORMULA=true` 会解析公式。

- `MINERU_IS_OCR=true` 可用于扫描件，但速度会更慢。

MinerU 调用位置：

```Plain Text
tools/document/mineru_parser.py
app/services/document_service.py
```



### **3\.6 存储配置**

```Plain Text
STORAGE_ROOT=storage/runs
```

每次任务会生成一个 run 目录：

```Plain Text
storage/runs/{run_id}/
```



## **4\. 解决方案 Markdown 各部分对应什么内容**

大纲由 text LLM 生成，用户可在前端编辑。默认结构如下。

### **4\.1\`\# 解决方案标题\`**

方案总标题，用于：

- 前端历史记录显示

- 图片生成中的全局方案标题

- 下载文件命名

### **4\.2\`\#\# 1\. 用户需求摘要\`**

总结用户输入的领域、目标、场景、受众和最终交付物。

适合用户检查：Agent 是否理解了需求。

### **4\.3\`\#\# 2\. 目标与边界\`**

定义：

- 目标

- 非目标

- 目标受众

- 利益相关方

- 交付物

- 成功指标

适合项目启动会或甲方确认范围。

### **4\.4\`\#\# 3\. Todo 型任务拆解\`**

展示 Agent 的工作过程，例如：

- 需求解析

- 文档解析

- 检索规划

- 多源检索

- 证据整理

- 方案设计

- 图片脚本生成

- 风险核验

适合说明方案不是模型直接编出来的，而是经过工作流生成。

### **4\.5\`\#\# 4\. 证据地图\`**

列出政策、产业、技术、学术、专利、新闻、竞品等来源。

这一节应该包含：

- 上传文档作为内部证据

- 网页检索作为外部证据

- 来源标题、URL、日期、来源类型、可信度

- 是否需要核验

如果上传了多篇文献，所有文献都应该出现在学术/专利来源中。

### **4\.6\`\#\# 5\. 总体解决方案架构\`**

描述方案的整体系统结构，例如：

- 业务层

- 数据层

- 知识层

- 模型层

- Agent 层

- 工具层

- 闭环与确认层

适合画成系统架构图。

### **4\.7\`\#\# 6\. Topic 列表\`**

定义后续图片和详细方案的 topic。

每个 topic 使用稳定编号：

```Plain Text
T01, T02, T03 ...
```

图片生成时会对应：

```Plain Text
P01 -> T01
P02 -> T02
P03 -> T03
```

### **4\.8\`\#\# 7\. 详细解决方案\`**

逐个展开每个 topic，包含：

- 核心问题

- 解决思路

- 需要的数据/工具/模型

- 政策/产业/技术/学术依据

- 关键交付物

- 可视化表达建议

- 需要核验

这一节适合人阅读，不会被整段直接塞给图片模型。图片生成优先看第 11 节。

### **4\.9\`\#\# 8\. 实施路线图\`**

按阶段拆解落地路径，例如：

- MVP

- 内测

- 试点

- 上线

- 迭代

### **4\.10\`\#\# 9\. 风险矩阵\`**

列出事实风险、数据风险、模型风险、产线风险、合规风险、ROI 风险等。

这节用于方案审查，不建议直接进入图片内容。

### **4\.11\`\#\# 10\. 验收指标\`**

定义项目验收指标，例如：

- 文献抽取准确率

- 引用可追溯率

- 实验推荐采纳率

- 工艺异常识别准确率

- 图片脚本一致性

### **4\.12\`\#\# 11\. 详细解决方案绘图提示词\`**

这是图片生成最重要的章节。

它包含两部分：

1. 统一风格锁定

2. P01\-Pxx 绘图表格

示例：

```Plain Text
统一风格锁定：
画幅比例 16:9；企业咨询汇报风格；深蓝、青绿、浅灰为主色；白色背景；细线条科技感；...
```

这段会进入每一张图片的最终 prompt，用于控制整组图片风格。

P01\-Pxx 表格用于控制每一页画什么：

```Plain Text
图片编号
对应 Topic
页面短标题
核心方案动作
主视觉结构
画面布局
辅助短标签
禁止出现
```

图片生成只取前 7 列作为绘图内容，`禁止出现` 列不会作为画面内容进入 `topic_content`。

### **4\.13\`\#\# 12\. 人工核验清单\`**

列出政策、市场、企业、论文、专利、标准、图片敏感内容等需要人工核验的内容。

这节是审计和交付前确认用，不应该直接画进图片。

## **5\. 图片提示词**

图片提示词不是直接来自 `image_prompts.py`，也不是直接来自整篇 Markdown。

真实链路是：

```Plain Text
前端当前 Markdown
-> app/services/image_service.py
-> 优先解析第 11 节 Detailed Solution Drawing Prompts
-> 得到 P01/P02/P03... 每页 topic_content
-> 提取第 11 节统一风格锁定
-> 合并 app/prompts/image_prompts.py 的通用图片模板
-> 得到每张图最终 image_prompt
-> 调用图片模型
```

每张图的最终 prompt 会保存到：

```Plain Text
storage/runs/{run_id}/prompts/topic_prompts.json
```

如果想检查图片为什么这么画，优先看这个文件。



如果想检查第 11 节有没有被正确解析，查看：

```Plain Text
storage/runs/{run_id}/images/parsed_drawing_topics.json
```



## **6\.\`app/prompts\` 提示词文件说明与可自定义项**

提示词集中在：

```Plain Text
app/prompts/
```

包含：

```Plain Text
system_prompts.py
outline_prompts.py
image_prompts.py
edit_prompts.py
__init__.py
```

### **6\.1\`system\_prompts\.py\`**

作用：

- 定义 text LLM 的系统身份。

- 控制 Agent 的总体工作原则。

- 约束其必须做需求理解、证据检索、todo 拆解、Markdown 输出、topic 图片脚本准备。

- 支持中文、英文和双语适配。

可自定义内容：

- Agent 角色定位，例如从“解决方案调研与可视化总监”改成“产业研究顾问”。

- 是否更强调政策、商业、技术、科研、投融资或产品方案。

- 输出风格，例如咨询报告、项目申报书、销售方案、路演材料。

- 事实约束强度，例如是否必须标注“需要核验”。

不建议修改：

- “不允许编造政策、标准、市场数据、论文结论”的约束。

- “用户确认后的 Markdown 是图片生成最终依据”的约束。

### **6\.2\`outline\_prompts\.py\`**

作用：

- 定义生成 Markdown 大纲的用户 prompt 模板。

- 把用户输入、文档总结、检索总结、topic 数量注入 text LLM。

- 规定 Markdown 必须包含哪些章节。

- 规定第 11 节必须输出 P01\-Pxx 绘图提示词表。

可自定义内容：

- Markdown 结构，比如增加“商业模式”“预算估算”“竞品对比”章节。

- Topic 表格字段。

- 详细解决方案字段。

- 第 11 节图片脚本的列名和绘图要求。

- 文献使用要求，例如“每篇上传文献必须进入证据地图”。

- 图片文字密度要求，例如“文字只保留短标签”。

如果希望生成结果更适合甲方汇报，建议重点修改：

```Plain Text
## 11. 详细解决方案绘图提示词
```



### **6\.3\`image\_prompts\.py\`**

作用：

- 定义图片生成的通用风格锁定。

- 定义每张 topic 图片的最终 prompt 模板。

- 支持中文、英文、双语。

可自定义内容：

- 图片统一视觉风格，例如咨询 PPT、科技信息图、白底极简、深色大屏。

- 颜色体系，例如深蓝、青绿、灰白。

- 页码和标题位置。

- 文字密度。

- 是否强调流程图、架构图、矩阵、路线图。

- 禁止出现的内容，例如真实 Logo、未经核验数字、风险提示等。

注意：

第 11 节中的“统一风格锁定”优先级高于 `image_prompts.py` 的通用风格。如果两者冲突，当前代码会提示模型以上方第 11 节风格为准。



### **6\.4\`edit\_prompts\.py\`**

作用：

- 定义单图修改时的 prompt。

- 会把原始图片 prompt 和用户修改要求一起传给 image edit 模型。

- 要求保留原图风格、页码、topic 含义和信息层级。

可自定义内容：

- 修改时保留哪些信息。

- 是否允许大幅重绘。

- 是否保持页面布局。

- 是否允许新增文字、图标、模块。

- 单图编辑的安全约束。

- 

## **7\. 资源整合链路**

资源整合指的是系统如何把用户输入、上传文档和网页检索结果整理成可供 text LLM 使用的上下文。

### **7\.1 用户输入**

来自前端：

```Plain Text
domain
goal
scenario
prompt / user_prompt
topic_count
uploaded_files
```

保存到：

```Plain Text
storage/runs/{run_id}/input/user_input.json
```

### **7\.2 文档解析**

上传文件保存到：

```Plain Text
storage/runs/{run_id}/uploads/
```

解析结果保存到：

```Plain Text
parsed/parsed_documents.json
```

文档摘要保存到：

```Plain Text
parsed/parsed_documents_summary.json
```

进入 outline LLM 的文档上下文保存到：

```Plain Text
parsed/parsed_documents_outline_context.md
```

当前策略：

```Plain Text
每篇文献单独 DeepSeek 深度归纳
每篇独立预算
按文献数量线性增加上下文
```



### **7\.3 网页检索**

检索计划保存到：

```Plain Text
retrieval/search_plan.json
```

原始检索结果保存到：

```Plain Text
retrieval/search_results.json
```

检索总结保存到：

```Plain Text
retrieval/search_results_summary.json
```

进入 outline LLM 的检索上下文保存到：

```Plain Text
retrieval/search_results_outline_context.md
```

当前策略：

```Plain Text
所有网页检索结果
-> 每 5 条为一个 batch
-> 不限制 batch 组数
-> 每个 batch 的 DeepSeek 归纳保留约 10000 字符
-> 所有 batch 拼接进入 text LLM
```



### **7\.4 Text LLM 生成大纲**

最终注入 text LLM 的内容包括：

```Plain Text
system prompt
outline prompt template
用户输入
文档 outline context
检索 outline context
topic_count
```

保存到：

```Plain Text
prompts/system_prompt.txt
prompts/outline_prompt.txt
outline/outline.md
outline/outline_versions/v01.md
```



## **8\. 如何自定义图片风格**

最推荐的方式是在 Markdown 第 11 节修改：

```Plain Text
统一风格锁定：
画幅比例 16:9；企业咨询汇报风格；深蓝、青绿、浅灰为主色；白色背景；细线条科技感；半扁平化图标；...
```

可修改为：

```Plain Text
统一风格锁定：
画幅比例 16:9；高端企业战略咨询 PPT 风格；白色背景；深海蓝、钛金灰、青绿色为主色；极简科技线框；轻量 3D 图标；模块卡片圆角；箭头统一为青绿色；每页顶部左侧放置页码 Pxx，顶部居中放页面短标题；画面留白充足；文字极少，只保留短标签；不使用真实公司 Logo；不出现未经核验数字、政策编号、市场规模或标准编号。
```

如果希望所有项目默认都使用同一种图片风格，可以修改：

```Plain Text
app/prompts/image_prompts.py
```

但单次项目更推荐直接改 Markdown 第 11 节。



## **10\. 如何自定义每张图的内容**

修改第 11 节 P01\-Pxx 表格。

例如 P05：

```Plain Text
| P05 | T05 | 工艺数字孪生 | 接入产线数据；模拟关键工艺；推荐参数；监测异常；提升一致性 | 产线流程图 + 数字孪生看板 | 横向产线流程贯穿页面；上方传感器数据；下方 AI 参数推荐；右侧 KPI 仪表 | 涂布、退火、结晶、封装、检测、参数推荐、异常预警 | 需要核验、风险提示、信息来源、下一步计划、真实 Logo、未经核验数字 |
```

每列作用：

- `图片编号`：页面编号，必须为 P01、P02\.\.\.

- `对应 Topic`：对应 T01、T02\.\.\.

- `页面短标题`：图片顶部标题。

- `核心方案动作`：这一页要表达的方案动作。

- `主视觉结构`：画成流程图、架构图、闭环图还是矩阵。

- `画面布局`：页面模块如何摆放。

- `辅助短标签`：允许出现在图片上的短文本。

- `禁止出现`：约束模型不要出现这些内容。



## **11\. 常见问题**

### **11\.1 为什么生成图片和 Markdown 不一致？**

优先检查：

```Plain Text
images/parsed_drawing_topics.json
prompts/topic_prompts.json
```

如果 `parsed_drawing_topics.json` 里 P05 不是预期 topic，说明第 11 节表格没有被正确解析。

如果 `topic_prompts.json` 里内容正确，但图片仍然偏离，说明图片模型没有很好遵循 prompt，可进一步强化第 11 节的布局约束。



### **11\.2 旧的\`topic\_prompts\.json\` 会影响重新生成吗？**

不会。

`topic_prompts.json` 是上一次生成记录。重新生成图片时，后端会重新读取当前 Markdown，重新解析第 11 节，再覆盖保存新的 `topic_prompts.json`。



### **11\.3 图片生成很慢怎么办？**

可以调整：

```Plain Text
IMAGE_GENERATION_CONCURRENCY=3
REQUEST_TIMEOUT=1200
```

如果供应商支持高并发，可把 `IMAGE_GENERATION_CONCURRENCY` 调大。如果接口限流或偶发失败，建议调小。



### **11\.4 为什么前端显示历史记录已有图片，不能重新生成？**

旧 run 可能保留了 `meta.json` 中的 `images` 和 `status=done`。

可以清空该 run 的：

```Plain Text
meta.json -> images
meta.json -> image_errors
meta.json -> status
prompts/topic_prompts.json
```

然后刷新前端重新生成。



## **12\. 推荐工作流**

建议实际使用时按下面流程操作：

1. 配置 `.env`，确保 text、DeepSeek、image、MinerU key 可用。

2. 启动后端，打开前端。

3. 创建 run，填写领域、目标、场景和文本提示词。

4. 上传 PDF 或项目资料。

5. 生成解决方案大纲。

6. 检查 `parsed_documents_outline_context.md` 和 `search_results_outline_context.md`，确认资料进入上下文。

7. 在前端编辑 Markdown，重点修改第 11 节绘图提示词。

8. 点击确认生成图片。

9. 检查 `parsed_drawing_topics.json` 和 `topic_prompts.json`。

10. 对不满意的单图进行对话式修改。

11. 下载 MD、HTML、图片或 ZIP。

