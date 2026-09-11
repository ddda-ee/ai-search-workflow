# AI Research Workflow（自动化科研综述与深度调研流水线）

`AI Research Workflow` 是一个模块化、高并发、带自我校验闭环的自动化科研调研与报告生成引擎。系统覆盖从课题规划、意图拆解、多学术源并发检索、PDF/HTML 正文采集、内联事实核验、同行评审自愈重写到生成带学术引用的 Markdown 报告全流程。

---

## 核心特性

- **多源并发检索矩阵**：内置 SearXNG、arXiv、OpenAlex、Semantic Scholar、Crossref 等专业学术与网页搜索插件，提供统一抽象与按源独立限流。
- **多厂家模型分流与路由（Stage-to-Model Routing）**：解耦大模型绑定，通过 YAML 配置可对规划、搜索分析、事实核查、长文撰写、同行评审等环节分别绑定不同模型提供商（DeepSeek、OpenAI、SiliconFlow、Anthropic、通义千问、智谱、Moonshot、OpenRouter、Ollama 等）。
- **学术全文多格式抓取与降级兜底**：自动将 arXiv 摘要页升维为 HTML 全文或直接解析原生 PDF 数据流；遇到反爬或超时自动使用检索 Snippet 兜底，保障流水线稳定性。
- **高性价比内联事实核查（Inline Fact-Checking & RAG Verification）**：单次推理同时输出技术事实与原文引据（Evidence），减少重复长文本调用；针对长论文采用基于局部词重合/Jaccard 的切片检索（RAG 模式）送审，削减事实核查上下文消耗。
- **同行评审自愈重写闭环（Self-Correction Loop）**：报告初稿生成后，由 Reviewer 从论据一致性、引用真实性、推断严谨性多维度检验；审稿未通过时自动携带批注反哺修正，实现自愈收敛。
- **本地持久化缓存机制**：持久化关键词消歧结果与检索返回，避免重复耗费搜索 API 额度与 LLM 消耗。

---

## 系统架构与工作流

```text
[1. 课题输入 (User Request)]
       │
       ▼
[阶段 1: 制定计划 (Planner - Strong Model)]
       │
       ▼
[阶段 2: 拆解任务 (Search Task Generator - Fast Model)]
       │
       ▼
[阶段 3: 多源并发检索 (Search Manager / 搜索插件)] ──> [本地持久化缓存 (SimpleJsonCache)]
       │
       ▼
[阶段 4: 全局去重与权威度筛选 (Global Selector)]
       │
       ▼
[阶段 5: 并发正文采集 (Collector: ArXiv HTML / PDF 解析 / 熔断降级)]
       │
       ▼
[阶段 6: 观点抽取与 RAG 局部事实核验 (Analyzer & Fact-Checker - Fast Model)]
       │
       ▼
[阶段 7: 综述合成 (Synthesizer - Strong Model)]
       │
       ▼
[阶段 8: 同行评审 (Reviewer - Strong Model)] <──┐
       │ (审查未通过且未达轮次上限)                 │ 携带审稿批注反哺
       └─────────────────────────> [自愈重写修正] ──┘
       │ (审查通过)
       ▼
[阶段 9: 报告落盘 (Report Generator: 动态命名为 问题_时间戳.md)]
```

---

## 项目结构（文件级说明）

### 根目录

| 文件 | 说明 |
| --- | --- |
| `main.py` | 统一主入口。提供 `run_research()` 可编程接口与 `argparse` 命令行入口，串联 9 个阶段。 |
| `switch_llm.py` | 交互式大模型配置工具。选择服务商、填 API Key、选模型，保存到 `.env` 并支持多套配置切换。 |
| `test_llm.py` | 单模型连通性快速测试脚本（走旧版 `LLMClient`）。 |
| `requirements.txt` | 项目依赖清单。 |
| `.gitignore` | Git 忽略规则，排除密钥、缓存、输出物与虚拟环境。 |
| `.env.example` | 环境变量模板，可复制为 `.env` 后填入真实 Key。 |

### config/

| 文件 | 说明 |
| --- | --- |
| `providers.py` | 内置大模型服务商预设（OpenAI 兼容接口），含 base_url、Key 环境变量名与候选模型。 |
| `settings.py` | 基于 `.env` 的旧版单模型配置（保留兼容），从 `providers.py` 读取预设。 |
| `research_type.py` | 研究类型定义：`scientific`（科研）与 `market`（市场）。 |
| `llm_config.yaml` | 多厂家模型与环节路由配置（`LLMManager` 使用）。 |
| `llm_profiles.json` | `switch_llm.py` 保存的多套模型配置（运行时生成，不提交）。 |

### models/

| 文件 | 说明 |
| --- | --- |
| `llm.py` | 旧版单模型 `LLMClient`，基于 OpenAI 兼容接口，保留兼容。 |
| `llm_manager.py` | `LLMManager`：多厂家连接池与环节路由调度器，读取 `llm_config.yaml`。 |
| `query.py` | `QueryAnalysis` 数据模型（关键词意图/消歧/双语扩展）。 |
| `research.py` | 核心数据模型（Pydantic V2）与 JSON Schema，贯穿全流程。 |

### prompts/

| 文件 | 说明 |
| --- | --- |
| `system.py` | 全局系统级约束 Prompt（诚实、不虚构、区分事实与推断）。 |
| `scientific.py` | 学术科研向引导 Prompt。 |
| `market.py` | 市场/商业调研引导 Prompt。 |

### storage/

| 文件 | 说明 |
| --- | --- |
| `cache.py` | `SimpleJsonCache` 本地 JSON 缓存。 |
| `cache.json` | 持久化缓存文件（运行时生成，不提交）。 |
| `database.py` | 预留空文件（数据库接口待实现）。 |
| `documents.py` | 预留空文件（文档存储接口待实现）。 |

### tools/（工具与搜索插件）

| 文件 | 说明 |
| --- | --- |
| `academic_reader.py` | 学术正文多格式解析（ArXiv/PDF/HTML）。 |
| `arxiv_search.py` | arXiv API 底层工具。 |
| `crossref.py` | Crossref API 底层工具。 |
| `openalex.py` | OpenAlex API 底层工具。 |
| `semantic_scholar.py` | Semantic Scholar API 底层工具。 |
| `web_search.py` | SearXNG 网页搜索底层工具。 |
| `webpage_reader.py` | 通用网页正文提取器。 |
| `rate_limiter.py` | 线程安全限速器。 |
| `text_matcher.py` | 轻量切片与 Jaccard 相关性检索器（RAG 模式）。 |
| `search/base.py` | `BaseSearchPlugin` 插件抽象基类。 |
| `search/registry.py` | `SearchPluginRegistry` 插件注册表。 |
| `search/arxiv.py` | `ArxivPlugin` 插件封装。 |
| `search/crossref.py` | `CrossrefPlugin` 插件封装。 |
| `search/openalex.py` | `OpenAlexPlugin` 插件封装。 |
| `search/semantic_scholar.py` | `SemanticScholarPlugin` 插件封装。 |
| `search/searxng.py` | `SearXNGPlugin` 插件封装。 |

### workflow/（9 阶段流水线）

| 文件 | 说明 |
| --- | --- |
| `planner.py` | 阶段 1：制定研究计划。 |
| `search_task_generator.py` | 阶段 2：拆解检索任务。 |
| `query_analyzer.py` | 关键词意图识别、消歧与中英双语扩展。 |
| `search_manager.py` | 阶段 3：多源并发搜索调度（新版，基于插件注册表）。 |
| `search_router.py` | 根据任务类型判断所需搜索能力。 |
| `searcher.py` | 旧版 `Searcher`（基于底层工具直调，保留兼容）。 |
| `research_pipeline.py` | 阶段 3～6 的流水线编排。 |
| `selector.py` | 阶段 4：全局去重与权威度综合筛选。 |
| `collector.py` | 阶段 5：正文并发拉取与异常熔断。 |
| `chunker.py` | 长文切片工具（待接入主流程）。 |
| `analyzer.py` | 阶段 6：单次调用完成观点抽取与内联事实核查。 |
| `fact_checker.py` | 阶段 6：RAG 局部切片精准复核。 |
| `synthesizer.py` | 阶段 7：综述长文撰写与自愈修复。 |
| `reviewer.py` | 阶段 8：逻辑与证据审稿。 |
| `report_generator.py` | 阶段 9：Markdown 报告生成。 |

### tests/

| 文件 | 说明 |
| --- | --- |
| `test_offline_units.py` | 离线逻辑单元测试（不依赖网络与 LLM），可直接 `pytest` 运行。 |
| `test_analyzer.py` | `analyze_and_verify_document` 测试。 |
| `test_fact_checker.py` | `fact_check_finding` 测试。 |
| `test_reviewer.py` | `review_report` 测试。 |
| `test_planner.py` | 研究计划测试（当前为空）。 |
| `test_pipeline.py` | 端到端流水线测试。 |
| `test_collector.py` | 正文采集测试。 |
| `test_chunker.py` | 长文切片测试。 |
| `test_selector.py` | 全局去重与筛选测试。 |
| `test_router.py` | 搜索路由测试。 |
| `test_searcher_router.py` | 旧版搜索器与路由测试。 |
| `test_search.py` | 旧版搜索器测试。 |
| `test_search_manager.py` | 搜索管理器测试。 |
| `test_query_analyzer.py` | 查询分析器测试。 |
| `test_search_plugin.py` | 搜索插件测试。 |
| `test_search_registry.py` | 插件注册表测试。 |
| `test_academic_search.py` | 学术搜索底层工具测试。 |
| `test_academic_plugins.py` | 学术插件封装测试。 |
| `test_report_generator.py` | 报告生成器测试。 |
| `test_webpage-reader.py` | 网页正文读取测试。 |

### output/

生成的 Markdown 报告落盘目录。

---

## 快速上手

### 1. 环境准备与依赖安装

建议使用 Python 3.10+ 环境：

```bash
# 进入项目根目录
cd ai-search-workflow

# 创建并激活虚拟环境
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置密钥环境（`.env`）

在项目根目录创建 `.env` 文件，填入所需的大模型 Key。可参考 `.env.example`：

```ini
# 大模型服务商 Key（按需配置）
DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
SILICONFLOW_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```

> 也可以直接运行 `python switch_llm.py`，以交互方式选择服务商、填写 Key、选择模型并保存多套配置，脚本会自动写入 `.env`。

### 3. 配置模型环节路由（`config/llm_config.yaml`）

编辑 `config/llm_config.yaml`，自由指定每个环节执行的模型：

```yaml
providers:
  deepseek:
    api_key: "${DEEPSEEK_API_KEY}"
    base_url: "https://api.deepseek.com/v1"

# 环节模型路由分配
stage_routing:
  planner:
    provider: "deepseek"
    model: "deepseek-chat"
  search_task_generator:
    provider: "deepseek"
    model: "deepseek-chat"
  query_analyzer:
    provider: "deepseek"
    model: "deepseek-chat"
  analyzer:
    provider: "deepseek"
    model: "deepseek-chat"
  fact_checker:
    provider: "deepseek"
    model: "deepseek-chat"
  synthesizer:
    provider: "deepseek"
    model: "deepseek-chat"
  reviewer:
    provider: "deepseek"
    model: "deepseek-chat"
```

内置服务商参见 `config/providers.py`：openai、deepseek、qwen、moonshot、zhipu、siliconflow、openrouter、ollama、custom。

---

## 运行方式

### 命令行运行

```bash
# 使用默认课题执行
python main.py

# 自定义调研课题与篇数
python main.py --request "调研 3D Gaussian Splatting 的核心算法演进、实时渲染优化及当前主流工业落地现状" --max-docs 5

# 指定研究类型为商业市场调研
python main.py --request "2026年全球具身智能人形机器人产业链与竞争格局分析" --type market
```

### 参数说明

| 参数项 | 缩写 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--request` | `-r` | 调研 NeRF 基本原理... | 调研需求或学术课题 |
| `--type` | `-t` | `scientific` | 研究类型：`scientific`（科研）或 `market`（市场） |
| `--max-docs` | `-m` | `5` | 全局精选保留的核心文献/网页篇数 |
| `--output-file` | `-o` | `None` | 指定报告输出文件名（不传则按 `问题_YYYYMMDD_HHMM.md` 自动命名） |
| `--config` | `-c` | `config/llm_config.yaml` | 多厂家大模型配置文件路径 |

### 其他工具

```bash
# 快速验证单模型连通性
python test_llm.py

# 交互式配置/切换大模型
python switch_llm.py
```

---

## 报告输出

执行完成后，Markdown 报告保存至 `output/` 目录，默认命名格式为：

```text
output/请调研_NeRF_的基本原理_核心技术_代表性方法_20260907_1117.md
```

报告包含以下章节结构：

- 摘要
- 研究背景
- 研究现状
- 主要研究方法
- 主要研究发现
- 方法比较
- 局限性
- 研究空白
- 未来研究方向
- 参考文献

---

## 搜索源说明

| 插件 | 类型 | 说明 |
| --- | --- | --- |
| `searxng` | Web | 依赖本地/远程 SearXNG 实例，默认地址 `http://localhost:8080` |
| `arxiv` | 学术 | arXiv API，限速约 2.5s/次 |
| `openalex` | 学术 | OpenAlex 开放学术图谱 |
| `semantic_scholar` | 学术 | Semantic Scholar，限速约 1.5s/次，支持重试 |
| `crossref` | 学术 | Crossref 元数据与 DOI |

---

## 当前状态与已知问题

> 项目已完成“旧版单模型 → 多模型路由”的关键接口对齐修复：`config/research_type.py` 语法错误已修正，`query_analyzer` / `analyzer` / `reviewer` 的 LLM 调用方式已统一，过时的测试用例已同步更新，并补充了 `.gitignore` 与 `.env.example`。具体进度见根目录《工作计划.md》。

运行 `python main.py` 前还需确认：

- 使用已安装完整依赖的 Python 环境执行 `pip install -r requirements.txt`。
- 配置 `.env` 中的大模型 Key，并确保 `config/llm_config.yaml` 中 provider 与 Key 对应。
- 使用 Web 搜索时需要本地或远程 SearXNG 实例，地址通过 `SEARXNG_BASE_URL` 配置，默认 `http://localhost:8080`。
- 完整端到端流程依赖网络访问学术源与大模型 API，请在网络可用环境下运行。

---

## License

