const state = {
  runId: null,
  uploadedFiles: [],
  currentImages: [],
  currentImageIndex: 0,
  currentTitle: '',
  lang: localStorage.getItem('solution-agent-lang') || 'zh',
};

const $ = (id) => document.getElementById(id);

const els = {
  domainInput: $('domainInput'),
  goalInput: $('goalInput'),
  scenarioInput: $('scenarioInput'),
  promptInput: $('promptInput'),
  fileInput: $('fileInput'),
  fileList: $('fileList'),
  topicSlider: $('topicSlider'),
  topicValue: $('topicValue'),
  imageAspectSelect: $('imageAspectSelect'),
  imageSizeSelect: $('imageSizeSelect'),
  outlineBtn: $('outlineBtn'),
  generateImagesBtn: $('generateImagesBtn'),
  downloadMdLink: $('downloadMdLink'),
  downloadHtmlLink: $('downloadHtmlLink'),
  downloadCurrentImageLink: $('downloadCurrentImageLink'),
  downloadAllImagesLink: $('downloadAllImagesLink'),
  outlineEditor: $('outlineEditor'),
  outlinePreview: $('outlinePreview'),
  progressModal: $('progressModal'),
  modalTitle: $('modalTitle'),
  modalSubtitle: $('modalSubtitle'),
  progressBar: $('progressBar'),
  progressSteps: $('progressSteps'),
  historyList: $('historyList'),
  mainImage: $('mainImage'),
  imageIndex: $('imageIndex'),
  imageCaption: $('imageCaption'),
  thumbStrip: $('thumbStrip'),
  stageMeta: $('stageMeta'),
  prevImage: $('prevImage'),
  nextImage: $('nextImage'),
  chatMessages: $('chatMessages'),
  imageEditInput: $('imageEditInput'),
  sendEditBtn: $('sendEditBtn'),
  newRunBtn: $('newRunBtn'),
  dropZone: $('dropZone'),
  langToggle: $('langToggle'),
};

const i18n = {
  zh: {
    newRun: '+ 新建解决方案',
    historyTitle: '历史记录',
    heroTitle: '面向政策、产业与技术调研的解决方案生成 Agent',
    heroDesc: '上传文档、输入目标和场景，Agent 先生成可编辑 Markdown 大纲，再生成连续一致的解决方案图片，并支持历史记录与单图对话式修改。',
    agentReady: 'Agent Ready',
    featureDocTitle: '多文档解析',
    featureDocDesc: '支持 PDF、Word、Markdown、CSV 等输入，PDF 通过 MinerU 服务 API 解析。',
    featureResearchTitle: '联网调研',
    featureResearchDesc: '通过 Tavily、DuckDuckGo/SearXNG、政策站点和产业信息源构建证据链。',
    featureOutlineTitle: '大纲确认',
    featureOutlineDesc: '先生成 todo 型方案大纲，用户可编辑 Markdown、表格、链接和 topic。',
    featureImagesTitle: '连续图片',
    featureImagesDesc: '控制比例、风格一致性和图片数量，支持单张图片继续对话式修改。',
    featureHistoryTitle: '历史归档',
    featureHistoryDesc: '每次运行保留输入、解析、检索、大纲、prompt、图片和单图修改版本。',
    inputTitle: '输入需求',
    inputDesc: '领域 / 目标 / 场景越明确，Agent 的调研和视觉化越稳定。',
    domainLabel: '领域',
    domainPlaceholder: '如：钙钛矿太阳能电池、智慧实验室、AI4Chem',
    goalLabel: '目标',
    goalPlaceholder: '如：形成产业落地解决方案',
    scenarioLabel: '应用场景',
    scenarioPlaceholder: '如：政府项目申报、企业汇报、科研平台设计',
    promptLabel: '文本型提示词',
    promptPlaceholder: '描述你希望 Agent 解决的问题、受众、约束、输出形式、图片风格等。',
    defaultPrompt: '请围绕 AI 化学实验室平台，调研近期政策、产业趋势和科研痛点，生成一个可用于汇报的解决方案，并输出 8 张连续风格一致的解决方案图片。',
    uploadTitle: '上传文档用于解析',
    uploadDesc: 'PDF / Word / Markdown / CSV / Excel，可一次上传多篇文献或项目材料。',
    topicCountLabel: 'Topic / 图片数量：',
    imageAspectLabel: '图片比例',
    imageSizeLabel: '图片尺寸',
    aspectSquare: '方形 1:1',
    aspectPortrait34: '竖版 3:4',
    aspectStory: '故事版 9:16',
    aspectLandscape43: '横版 4:3',
    aspectWide: '宽屏 16:9',
    sizeSquare: '1024x1024 方形',
    sizeLandscape: '1536x1024 横版',
    sizePortrait: '1024x1536 竖版',
    size2kSquare: '2048x2048 2K 方形',
    size2kLandscape: '2048x1152 2K 横版',
    size4kLandscape: '3840x2160 4K 横版',
    size4kPortrait: '2160x3840 4K 竖版',
    outlineBtn: '生成解决方案大纲',
    markdownTitle: '可编辑 Markdown 大纲',
    markdownDesc: '确认前可以修改 topic、表格、链接和具体实施路径。',
    downloadMd: '下载 MD',
    downloadHtml: '下载 HTML',
    downloadImage: '下载当前图片',
    downloadAllImages: '全部图片 ZIP',
    generateImagesBtn: '确认并生成解决方案图片',
    editTab: '编辑',
    previewTab: '预览',
    outlinePlaceholder: 'Agent 生成的大纲会显示在这里，可编辑。',
    viewerTitle: '连续方案图片可视化窗口',
    notGenerated: '尚未生成',
    prevImage: '上一张',
    nextImage: '下一张',
    waitingImages: '等待生成解决方案图片',
    editImageTitle: '对当前图片继续修改',
    chatHint: '选择一张图片后，可以像 GPT 对话框一样输入修改建议，例如“把政策分析部分放大，加入产业链箭头”。',
    imageEditPlaceholder: '输入对当前图片的修改要求...',
    sendEditBtn: '发送修改',
    modalDefaultTitle: 'Agent 正在生成',
    modalDefaultSubtitle: '正在规划任务...',
    unnamedDomain: '未命名领域',
    solution: '解决方案',
    uploadBusy: '正在上传文件...',
    outlineBusy: 'Agent 生成中...',
    imageBusy: '图片生成中...',
    editBusy: '生成中...',
    outlineModalTitle: 'Agent 正在生成解决方案大纲',
    outlineModalSubtitle: '第一部分：语言智能体 GPT-5.5 正在进行解决方案大纲生成',
    outlineSteps: ['解析用户需求', '解析上传文档', '检索政策与产业信息', '构建 todo 计划', '生成 Markdown 大纲'],
    imageModalTitle: 'Agent 正在生成解决方案',
    imageModalSubtitle: '正在生成连续风格一致的解决方案图片',
    imageSteps: ['读取用户确认后的 Markdown 大纲', '拆解 topic 并锁定统一视觉风格', '为每张图片生成独立 image prompt', '调用图片模型生成连续解决方案图片', '保存过程文件、图片和历史记录'],
    generatedImages: (count) => `解决方案已生成 · ${count} 张图片 · 点击查看`,
    generatedImagesPartial: (success, failed) => `图片部分生成完成 · 成功 ${success} 张 · 失败 ${failed} 张`,
    historyImages: (count) => `${count} 张图`,
    noHistory: '暂无历史记录',
    historyRecordWithImages: (count) => `历史记录 · ${count} 张图片`,
    historyRecordNoImages: '历史记录 · 未生成图片',
    currentImagePrompt: (title) => `当前图片：${title || '未选择'}。请输入你希望修改的内容。`,
    uploadFailed: (msg) => `上传失败：${msg}`,
    outlineFailed: (msg) => `生成失败：${msg}`,
    imageFailed: (msg) => `图片生成失败：${msg}`,
    editFailed: (msg) => `图片修改失败：${msg}`,
    langButton: 'EN',
  },
  en: {
    newRun: '+ New Solution',
    historyTitle: 'History',
    heroTitle: 'Solution Generation Agent for Policy, Industry and Technology Research',
    heroDesc: 'Upload documents, define goals and scenarios, let the Agent create an editable Markdown outline first, then generate a consistent image deck with history and single-image conversational edits.',
    agentReady: 'Agent Ready',
    featureDocTitle: 'Document Parsing',
    featureDocDesc: 'Supports PDF, Word, Markdown, CSV and Excel inputs. PDFs are parsed through the MinerU service API.',
    featureResearchTitle: 'Web Research',
    featureResearchDesc: 'Build evidence chains with Tavily, DuckDuckGo/SearXNG, policy sites and industry sources.',
    featureOutlineTitle: 'Outline Review',
    featureOutlineDesc: 'Generate a todo-style solution outline first; edit Markdown, tables, links and topics before confirmation.',
    featureImagesTitle: 'Consistent Images',
    featureImagesDesc: 'Control aspect ratio, style consistency and image count, with conversational edits for each image.',
    featureHistoryTitle: 'Run Archive',
    featureHistoryDesc: 'Each run keeps inputs, parsing, retrieval, outline, prompts, images and image edit versions.',
    inputTitle: 'Input Requirements',
    inputDesc: 'Clearer domain, goal and scenario inputs help the Agent research and visualize more reliably.',
    domainLabel: 'Domain',
    domainPlaceholder: 'e.g. perovskite solar cells, smart lab, AI4Chem',
    goalLabel: 'Goal',
    goalPlaceholder: 'e.g. create an industry implementation solution',
    scenarioLabel: 'Scenario',
    scenarioPlaceholder: 'e.g. government proposal, executive briefing, research platform design',
    promptLabel: 'Text Prompt',
    promptPlaceholder: 'Describe the problem, audience, constraints, output format, image style and other expectations.',
    defaultPrompt: 'Please research recent policies, industry trends and research pain points around an AI chemistry lab platform, generate a presentation-ready solution, and output 8 consistent solution images.',
    uploadTitle: 'Upload Documents for Parsing',
    uploadDesc: 'PDF / Word / Markdown / CSV / Excel. Upload multiple papers or project documents at once.',
    topicCountLabel: 'Topics / Images: ',
    imageAspectLabel: 'Image Ratio',
    imageSizeLabel: 'Image Size',
    aspectSquare: 'Square 1:1',
    aspectPortrait34: 'Portrait 3:4',
    aspectStory: 'Story 9:16',
    aspectLandscape43: 'Landscape 4:3',
    aspectWide: 'Wide 16:9',
    sizeSquare: '1024x1024 Square',
    sizeLandscape: '1536x1024 Landscape',
    sizePortrait: '1024x1536 Portrait',
    size2kSquare: '2048x2048 2K Square',
    size2kLandscape: '2048x1152 2K Landscape',
    size4kLandscape: '3840x2160 4K Landscape',
    size4kPortrait: '2160x3840 4K Portrait',
    outlineBtn: 'Generate Solution Outline',
    markdownTitle: 'Editable Markdown Outline',
    markdownDesc: 'Before confirmation, you can edit topics, tables, links and implementation details.',
    downloadMd: 'Download MD',
    downloadHtml: 'Download HTML',
    downloadImage: 'Download Image',
    downloadAllImages: 'All Images ZIP',
    generateImagesBtn: 'Confirm and Generate Images',
    editTab: 'Edit',
    previewTab: 'Preview',
    outlinePlaceholder: 'The generated outline will appear here and remain editable.',
    viewerTitle: 'Visual Solution Viewer',
    notGenerated: 'Not generated yet',
    prevImage: 'Previous image',
    nextImage: 'Next image',
    waitingImages: 'Waiting for solution images',
    editImageTitle: 'Continue Editing Current Image',
    chatHint: 'Select an image and enter edit requests like a GPT chat, for example “enlarge the policy analysis area and add an industry-chain arrow”.',
    imageEditPlaceholder: 'Enter edits for the current image...',
    sendEditBtn: 'Send Edit',
    modalDefaultTitle: 'Agent is generating',
    modalDefaultSubtitle: 'Planning tasks...',
    unnamedDomain: 'Untitled Domain',
    solution: 'Solution',
    uploadBusy: 'Uploading files...',
    outlineBusy: 'Agent working...',
    imageBusy: 'Generating images...',
    editBusy: 'Generating...',
    outlineModalTitle: 'Agent is generating the solution outline',
    outlineModalSubtitle: 'Part 1: GPT-5.5 language agent is creating the solution outline',
    outlineSteps: ['Parse user requirements', 'Parse uploaded documents', 'Retrieve policy and industry information', 'Build todo plan', 'Generate Markdown outline'],
    imageModalTitle: 'Agent is generating the solution',
    imageModalSubtitle: 'Generating a consistent sequence of solution images',
    imageSteps: ['Read confirmed Markdown outline', 'Split topics and lock visual style', 'Generate image prompt for each topic', 'Call image model for consistent solution images', 'Archive files, images and history'],
    generatedImages: (count) => `Solution generated · ${count} images · Click to view`,
    generatedImagesPartial: (success, failed) => `Images partially generated · ${success} succeeded · ${failed} failed`,
    historyImages: (count) => `${count} images`,
    noHistory: 'No history yet',
    historyRecordWithImages: (count) => `History · ${count} images`,
    historyRecordNoImages: 'History · No images yet',
    currentImagePrompt: (title) => `Current image: ${title || 'None selected'}. Enter what you want to change.`,
    uploadFailed: (msg) => `Upload failed: ${msg}`,
    outlineFailed: (msg) => `Generation failed: ${msg}`,
    imageFailed: (msg) => `Image generation failed: ${msg}`,
    editFailed: (msg) => `Image edit failed: ${msg}`,
    langButton: '中文',
  },
};

const statusI18n = {
  en: {
    'Run 已创建': 'Run created',
    '解析用户需求、目标受众和输出约束': 'Parsing requirements, audience and output constraints',
    '解析上传文档，提取标题、摘要、表格和样例': 'Parsing uploaded documents and extracting titles, summaries, tables and samples',
    '生成政策、产业、学术、专利、新闻和竞品检索计划': 'Planning policy, industry, academic, patent, news and competitor searches',
    '执行多源联网检索并按可信度/时效性排序': 'Running multi-source web retrieval and ranking by credibility and freshness',
    'GPT-5.5 正在综合证据并生成 Markdown 大纲': 'GPT-5.5 is synthesizing evidence and generating the Markdown outline',
    '解决方案大纲已生成，等待用户确认': 'Solution outline generated, waiting for confirmation',
    '拆解用户确认后的 Markdown 并生成 topic prompts': 'Splitting confirmed Markdown and generating topic prompts',
    '调用图片模型生成连续风格一致的解决方案图片': 'Calling the image model to generate a consistent solution image sequence',
    '解决方案图片已生成': 'Solution images generated',
    '根据用户要求生成单图新版本': 'Generating a new version for the selected image',
    '单图修改已保存': 'Single-image edit saved',
  },
};

function t(key, ...args) {
  const value = i18n[state.lang]?.[key] ?? i18n.zh[key] ?? key;
  return typeof value === 'function' ? value(...args) : value;
}

function translateStatusMessage(message) {
  return state.lang === 'en' ? (statusI18n.en[message] || message) : message;
}

const api = {
  async post(url, body) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await readableError(res));
    return res.json();
  },
  async get(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(await readableError(res));
    return res.json();
  },
};

const aspectDefaultSize = {
  '1:1': '1024x1024',
  '3:4': '1024x1536',
  '9:16': '1024x1536',
  '4:3': '1536x1024',
  '16:9': '1536x1024',
};

const sizeAspect = {
  '1024x1024': '1:1',
  '1536x1024': '16:9',
  '1024x1536': '9:16',
  '2048x2048': '1:1',
  '2048x1152': '16:9',
  '3840x2160': '16:9',
  '2160x3840': '9:16',
};

async function readableError(res) {
  try {
    const data = await res.json();
    return data.detail || JSON.stringify(data);
  } catch (_) {
    return res.text();
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function escapeHtml(text) {
  return String(text || '').replace(/[&<>'"]/g, (m) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;' }[m]));
}

function applyI18n() {
  document.documentElement.lang = state.lang === 'zh' ? 'zh-CN' : 'en';
  document.querySelectorAll('[data-i18n]').forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
  document.querySelectorAll('[data-i18n-aria-label]').forEach((node) => {
    node.setAttribute('aria-label', t(node.dataset.i18nAriaLabel));
  });
  els.langToggle.textContent = t('langButton');
  if (!state.runId && (!els.promptInput.value || Object.values(i18n).some((dict) => dict.defaultPrompt === els.promptInput.value))) {
    els.promptInput.value = t('defaultPrompt');
  }
  if (!state.currentImages.length) {
    els.stageMeta.textContent = t('notGenerated');
    els.imageCaption.textContent = t('waitingImages');
  } else {
    els.stageMeta.textContent = t('historyRecordWithImages', state.currentImages.length);
  }
  renderChatForCurrentImage();
  refreshCustomSelects();
  loadHistory().catch(console.warn);
}

function switchLanguage() {
  state.lang = state.lang === 'zh' ? 'en' : 'zh';
  localStorage.setItem('solution-agent-lang', state.lang);
  applyI18n();
}

function setBusy(button, busy, label) {
  if (!button) return;
  if (busy) button.dataset.oldText = button.textContent;
  button.disabled = busy;
  button.textContent = busy ? label : (button.dataset.oldText || button.textContent);
}

async function ensureRun() {
  if (state.runId) return state.runId;
  const title = `${els.domainInput.value.trim() || t('unnamedDomain')} · ${els.goalInput.value.trim() || t('solution')}`;
  const run = await api.post('/api/runs', { title });
  state.runId = run.run_id;
  state.currentTitle = run.title;
  await loadHistory();
  return state.runId;
}

async function pollStatusUntilDone(runId, fallbackSteps) {
  for (let i = 0; i < 120; i++) {
    const status = await api.get(`/api/runs/${runId}/status`).catch(() => null);
    if (status) {
      els.progressBar.style.width = `${Math.max(8, status.progress || 0)}%`;
      els.modalSubtitle.textContent = status.message ? translateStatusMessage(status.message) : els.modalSubtitle.textContent;
      const steps = status.steps?.length ? status.steps.map((s) => translateStatusMessage(s.message)) : fallbackSteps;
      els.progressSteps.innerHTML = steps.map((step, index) => `<div class="step ${index < steps.length - 1 ? 'done' : 'active'}">${escapeHtml(step)}</div>`).join('');
      if (status.status === 'done' || status.status === 'failed') return status;
    }
    await sleep(650);
  }
  return null;
}

async function runProgress(title, subtitle, steps, action, runIdProvider) {
  els.modalTitle.textContent = title;
  els.modalSubtitle.textContent = subtitle;
  els.progressBar.style.width = '6%';
  els.progressSteps.innerHTML = steps.map((step, index) => `<div class="step" data-step="${index}">${escapeHtml(step)}</div>`).join('');
  els.progressModal.classList.remove('hidden');
  const work = action();
  const runId = typeof runIdProvider === 'function' ? runIdProvider() : state.runId;
  if (runId) pollStatusUntilDone(runId, steps).catch(console.warn);
  const result = await work;
  els.progressBar.style.width = '100%';
  els.progressSteps.innerHTML = steps.map((step) => `<div class="step done">${escapeHtml(step)}</div>`).join('');
  await sleep(350);
  els.progressModal.classList.add('hidden');
  return result;
}

function renderFiles() {
  els.fileList.innerHTML = state.uploadedFiles.map((file) => {
    const name = file.name || file.stored_name || 'upload';
    const size = file.size ? `${Math.ceil(file.size / 1024)} KB` : '';
    return `<span class="file-chip">${escapeHtml(name)}${size ? `<small>${size}</small>` : ''}</span>`;
  }).join('');
}

function updateMarkdownPreview() {
  const html = marked.parse(els.outlineEditor.value || '');
  els.outlinePreview.innerHTML = DOMPurify.sanitize(html);
}

function switchTab(tabName) {
  document.querySelectorAll('.tab').forEach((tab) => tab.classList.toggle('active', tab.dataset.tab === tabName));
  els.outlineEditor.classList.toggle('hidden', tabName !== 'editor');
  els.outlinePreview.classList.toggle('hidden', tabName !== 'preview');
  if (tabName === 'preview') updateMarkdownPreview();
}

function setDownloadLink(link, href, enabled) {
  link.href = enabled ? href : '#';
  link.classList.toggle('disabled', !enabled);
  link.setAttribute('aria-disabled', enabled ? 'false' : 'true');
}

function updateDownloadLinks() {
  const hasRun = Boolean(state.runId);
  const hasOutline = hasRun && Boolean(els.outlineEditor.value.trim());
  const currentImage = state.currentImages[state.currentImageIndex];
  setDownloadLink(els.downloadMdLink, `/api/runs/${state.runId}/outline.md`, hasOutline);
  setDownloadLink(els.downloadHtmlLink, `/api/runs/${state.runId}/outline.html`, hasOutline);
  setDownloadLink(
    els.downloadCurrentImageLink,
    currentImage ? `/api/runs/${state.runId}/images/${encodeURIComponent(currentImage.filename)}/download` : '#',
    hasRun && Boolean(currentImage?.filename),
  );
  setDownloadLink(els.downloadAllImagesLink, `/api/runs/${state.runId}/images.zip`, hasRun && state.currentImages.length > 0);
}

function initCustomSelects() {
  document.querySelectorAll('.custom-select').forEach((wrapper) => {
    const nativeSelect = $(wrapper.dataset.selectTarget);
    if (!nativeSelect || wrapper.dataset.ready === 'true') return;
    wrapper.dataset.ready = 'true';
    wrapper.innerHTML = `
      <button type="button" class="custom-select-trigger">
        <span class="custom-select-value"></span>
        <span class="custom-select-arrow"></span>
      </button>
      <div class="custom-select-menu"></div>
    `;
    wrapper.querySelector('.custom-select-trigger').addEventListener('click', (event) => {
      event.stopPropagation();
      document.querySelectorAll('.custom-select.open').forEach((item) => {
        if (item !== wrapper) item.classList.remove('open');
      });
      wrapper.classList.toggle('open');
      document.querySelector('.input-panel')?.classList.toggle('select-open', Boolean(document.querySelector('.custom-select.open')));
    });
  });
  refreshCustomSelects();
}

function refreshCustomSelects() {
  document.querySelectorAll('.custom-select').forEach((wrapper) => {
    const nativeSelect = $(wrapper.dataset.selectTarget);
    if (!nativeSelect) return;
    const valueNode = wrapper.querySelector('.custom-select-value');
    const menu = wrapper.querySelector('.custom-select-menu');
    const selectedOption = nativeSelect.options[nativeSelect.selectedIndex];
    if (valueNode && selectedOption) valueNode.textContent = selectedOption.textContent;
    if (!menu) return;
    menu.innerHTML = Array.from(nativeSelect.options).map((option) => `
      <button type="button" class="custom-select-option ${option.selected ? 'selected' : ''}" data-value="${escapeHtml(option.value)}">
        ${escapeHtml(option.textContent)}
      </button>
    `).join('');
    menu.querySelectorAll('.custom-select-option').forEach((optionNode) => {
      optionNode.addEventListener('click', (event) => {
        event.stopPropagation();
        nativeSelect.value = optionNode.dataset.value;
        nativeSelect.dispatchEvent(new Event('change', { bubbles: true }));
        wrapper.classList.remove('open');
        document.querySelector('.input-panel')?.classList.remove('select-open');
        refreshCustomSelects();
      });
    });
  });
}

function safeDownloadName(name, suffix) {
  const base = (name || state.runId || 'solution').replace(/[\\/:*?"<>|]+/g, '_').slice(0, 80);
  return `${base || 'solution'}_${suffix}`;
}

function downloadBlob(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function downloadCurrentMarkdown(event) {
  event.preventDefault();
  const markdown = els.outlineEditor.value.trim();
  if (!markdown) return;
  downloadBlob(safeDownloadName(state.currentTitle, 'outline.md'), markdown, 'text/markdown;charset=utf-8');
}

function downloadCurrentHtml(event) {
  event.preventDefault();
  const markdown = els.outlineEditor.value.trim();
  if (!markdown) return;
  const body = DOMPurify.sanitize(marked.parse(markdown));
  const html = `<!doctype html>
<html lang="${state.lang === 'en' ? 'en' : 'zh-CN'}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(state.currentTitle || 'Solution Outline')}</title>
  <style>
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f8fafc; color: #0f172a; }
    main { max-width: 1080px; margin: 0 auto; padding: 48px 28px; }
    article { background: white; border: 1px solid #e2e8f0; border-radius: 24px; padding: 34px; box-shadow: 0 20px 70px rgba(15,23,42,.08); }
    h1, h2, h3 { line-height: 1.25; }
    p, li { line-height: 1.75; }
    table { width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 14px; }
    th, td { border: 1px solid #cbd5e1; padding: 10px 12px; vertical-align: top; }
    th { background: #f1f5f9; }
    a { color: #0284c7; }
  </style>
</head>
<body><main><article>${body}</article></main></body>
</html>`;
  downloadBlob(safeDownloadName(state.currentTitle, 'outline.html'), html, 'text/html;charset=utf-8');
}

async function uploadFiles(files) {
  const selected = Array.from(files || []);
  if (!selected.length) return;
  const runId = await ensureRun();
  const form = new FormData();
  form.append('run_id', runId);
  selected.forEach((file) => form.append('files', file));
  setBusy(els.outlineBtn, true, t('uploadBusy'));
  try {
    const res = await fetch('/api/upload', { method: 'POST', body: form });
    if (!res.ok) throw new Error(await readableError(res));
    const data = await res.json();
    state.uploadedFiles = [...state.uploadedFiles, ...(data.saved || [])];
    renderFiles();
    await loadHistory();
  } finally {
    setBusy(els.outlineBtn, false);
  }
}

async function createOutline() {
  const runId = await ensureRun();
  const payload = {
    run_id: runId,
    domain: els.domainInput.value.trim(),
    goal: els.goalInput.value.trim(),
    scenario: els.scenarioInput.value.trim(),
    prompt: els.promptInput.value.trim(),
    topic_count: Number(els.topicSlider.value),
    uploaded_files: state.uploadedFiles.map((f) => f.stored_name || f.name),
  };
  const steps = t('outlineSteps');
  setBusy(els.outlineBtn, true, t('outlineBusy'));
  try {
    const result = await runProgress(
      t('outlineModalTitle'),
      t('outlineModalSubtitle'),
      steps,
      () => api.post('/api/outline', payload),
      () => runId,
    );
    state.runId = result.run_id;
    state.currentTitle = result.title;
    els.outlineEditor.value = result.outline_markdown;
    els.generateImagesBtn.disabled = false;
    updateMarkdownPreview();
    updateDownloadLinks();
    await loadHistory();
  } finally {
    setBusy(els.outlineBtn, false);
  }
}

async function generateImages() {
  if (!state.runId) return;
  const topicCount = Number(els.topicSlider.value);
  const steps = t('imageSteps');
  setBusy(els.generateImagesBtn, true, t('imageBusy'));
  try {
    const result = await runProgress(
      t('imageModalTitle'),
      t('imageModalSubtitle'),
      steps,
      () => api.post('/api/images', {
        run_id: state.runId,
        outline_markdown: els.outlineEditor.value,
        style_preset: 'glass-card enterprise consulting diagram',
        aspect_ratio: els.imageAspectSelect.value,
        image_size: els.imageSizeSelect.value,
        topic_count: topicCount,
      }),
      () => state.runId,
    );
    state.currentImages = result.images || [];
    state.currentImageIndex = 0;
    renderImages();
    const failedCount = (result.image_errors || []).length;
    els.stageMeta.textContent = failedCount ? t('generatedImagesPartial', state.currentImages.length, failedCount) : t('generatedImages', state.currentImages.length);
    updateDownloadLinks();
    await loadHistory();
    document.getElementById('imageStage').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } finally {
    setBusy(els.generateImagesBtn, false);
    els.generateImagesBtn.disabled = !els.outlineEditor.value;
  }
}

function renderImages() {
  const images = state.currentImages || [];
  const img = images[state.currentImageIndex];
  if (!img) {
    els.mainImage.style.display = 'none';
    els.imageIndex.textContent = '00 / 00';
    els.imageCaption.textContent = t('waitingImages');
    els.thumbStrip.innerHTML = '';
    renderChatForCurrentImage();
    updateDownloadLinks();
    return;
  }
  els.mainImage.src = img.url;
  els.mainImage.style.display = 'block';
  els.imageIndex.textContent = `${String(state.currentImageIndex + 1).padStart(2, '0')} / ${String(images.length).padStart(2, '0')}`;
  els.imageCaption.textContent = img.title;
  els.thumbStrip.innerHTML = images.map((image, index) => `
    <button class="thumb ${index === state.currentImageIndex ? 'active' : ''}" data-index="${index}">
      <img src="${image.url}" alt="${escapeHtml(image.title)}" />
    </button>
  `).join('');
  els.thumbStrip.querySelectorAll('.thumb').forEach((thumb) => {
    thumb.addEventListener('click', () => {
      state.currentImageIndex = Number(thumb.dataset.index);
      renderImages();
    });
  });
  renderChatForCurrentImage();
  updateDownloadLinks();
}

function renderChatForCurrentImage() {
  const image = state.currentImages[state.currentImageIndex];
  const base = `<div class="message agent">${escapeHtml(t('currentImagePrompt', image?.title))}</div>`;
  const edits = image?.edits || [];
  els.chatMessages.innerHTML = base + edits.map((msg) => `<div class="message ${msg.role === 'user' ? 'user' : 'agent'}">${escapeHtml(msg.content)}</div>`).join('');
  els.chatMessages.scrollTop = els.chatMessages.scrollHeight;
}

async function sendImageEdit() {
  const image = state.currentImages[state.currentImageIndex];
  const instruction = els.imageEditInput.value.trim();
  if (!state.runId || !image || !instruction) return;
  els.imageEditInput.value = '';
  setBusy(els.sendEditBtn, true, t('editBusy'));
  try {
    const updated = await api.post('/api/image-edit', { run_id: state.runId, image_id: image.image_id, instruction });
    state.currentImages = updated.images || state.currentImages;
    renderImages();
    await loadHistory();
  } catch (error) {
    alert(t('editFailed', error.message));
  } finally {
    setBusy(els.sendEditBtn, false);
  }
}

async function loadHistory() {
  const data = await api.get('/api/history');
  const items = data.items || [];
  els.historyList.innerHTML = items.length ? items.map((item) => `
    <button class="history-item" data-run="${item.run_id}">
      <div class="history-title">${escapeHtml(item.title || item.run_id)}</div>
      <div class="history-date">${escapeHtml(item.created_at || '')} · ${escapeHtml(t('historyImages', (item.images || []).length))}</div>
    </button>
  `).join('') : `<div class="history-date">${escapeHtml(t('noHistory'))}</div>`;
  els.historyList.querySelectorAll('.history-item').forEach((node) => {
    node.addEventListener('click', async () => {
      const run = await api.get(`/api/history/${node.dataset.run}`);
      state.runId = run.run_id;
      state.currentTitle = run.title;
      state.uploadedFiles = run.uploaded_files || [];
      els.domainInput.value = run.domain || '';
      els.goalInput.value = run.goal || '';
      els.scenarioInput.value = run.scenario || '';
      els.promptInput.value = run.user_input?.prompt || run.user_input?.user_prompt || '';
      els.topicSlider.value = run.topic_count || 8;
      els.topicValue.textContent = els.topicSlider.value;
      els.outlineEditor.value = run.outline_markdown || '';
      els.generateImagesBtn.disabled = !els.outlineEditor.value;
      state.currentImages = run.images || [];
      state.currentImageIndex = 0;
      els.stageMeta.textContent = state.currentImages.length ? t('historyRecordWithImages', state.currentImages.length) : t('historyRecordNoImages');
      renderFiles();
      updateMarkdownPreview();
      renderImages();
      updateDownloadLinks();
    });
  });
}

function resetWorkspace() {
  state.runId = null;
  state.uploadedFiles = [];
  state.currentImages = [];
  state.currentImageIndex = 0;
  els.domainInput.value = '';
  els.goalInput.value = '';
  els.scenarioInput.value = '';
  els.promptInput.value = '';
  els.imageAspectSelect.value = '16:9';
  els.imageSizeSelect.value = '1536x1024';
  els.outlineEditor.value = '';
  els.generateImagesBtn.disabled = true;
  els.stageMeta.textContent = t('notGenerated');
  renderFiles();
  renderImages();
  updateDownloadLinks();
  switchTab('editor');
}

els.topicSlider.addEventListener('input', () => { els.topicValue.textContent = els.topicSlider.value; });
els.imageAspectSelect.addEventListener('change', () => {
  els.imageSizeSelect.value = aspectDefaultSize[els.imageAspectSelect.value] || '1536x1024';
  refreshCustomSelects();
});
els.imageSizeSelect.addEventListener('change', () => {
  els.imageAspectSelect.value = sizeAspect[els.imageSizeSelect.value] || els.imageAspectSelect.value;
  refreshCustomSelects();
});
els.fileInput.addEventListener('change', (event) => uploadFiles(event.target.files).catch((error) => alert(t('uploadFailed', error.message))));
['dragenter', 'dragover'].forEach((name) => els.dropZone.addEventListener(name, (event) => { event.preventDefault(); els.dropZone.classList.add('dragging'); }));
['dragleave', 'drop'].forEach((name) => els.dropZone.addEventListener(name, (event) => { event.preventDefault(); els.dropZone.classList.remove('dragging'); }));
els.dropZone.addEventListener('drop', (event) => uploadFiles(event.dataTransfer.files).catch((error) => alert(t('uploadFailed', error.message))));
els.outlineBtn.addEventListener('click', () => createOutline().catch((error) => alert(t('outlineFailed', error.message))));
els.generateImagesBtn.addEventListener('click', () => generateImages().catch((error) => alert(t('imageFailed', error.message))));
els.downloadMdLink.addEventListener('click', downloadCurrentMarkdown);
els.downloadHtmlLink.addEventListener('click', downloadCurrentHtml);
els.outlineEditor.addEventListener('input', () => {
  updateMarkdownPreview();
  updateDownloadLinks();
});
els.prevImage.addEventListener('click', () => { if (!state.currentImages.length) return; state.currentImageIndex = (state.currentImageIndex - 1 + state.currentImages.length) % state.currentImages.length; renderImages(); });
els.nextImage.addEventListener('click', () => { if (!state.currentImages.length) return; state.currentImageIndex = (state.currentImageIndex + 1) % state.currentImages.length; renderImages(); });
els.sendEditBtn.addEventListener('click', () => sendImageEdit());
els.imageEditInput.addEventListener('keydown', (event) => { if (event.key === 'Enter') sendImageEdit(); });
els.newRunBtn.addEventListener('click', resetWorkspace);
els.langToggle.addEventListener('click', switchLanguage);
document.querySelectorAll('.tab').forEach((tab) => tab.addEventListener('click', () => switchTab(tab.dataset.tab)));
document.addEventListener('click', () => {
  document.querySelectorAll('.custom-select.open').forEach((item) => item.classList.remove('open'));
  document.querySelector('.input-panel')?.classList.remove('select-open');
});

initCustomSelects();
applyI18n();
renderImages();
