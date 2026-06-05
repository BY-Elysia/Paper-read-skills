# Paper-read-skills

面向大模型与多模态论文阅读的 Codex Agent Skill。当前包含 `llm-paper-reader`：给 Agent 一篇本地 PDF、论文链接或正文后，生成正式的中文 Markdown 图文讲解报告。

## llm-paper-reader

它不只概括或翻译论文，而是优先讲清楚：

- 论文要解决的问题、完整模型架构和信息流
- 训练与推理过程中，一个输入或 batch 实际如何运行
- 核心公式中每个符号、相似度、softmax、loss 和更新目标如何计算
- 论文专有名词在当前机制中的具体含义
- 主实验、消融实验及其真正支持的结论
- 复现路线、实现风险和论文没有说明的细节

报告会在对应位置嵌入裁剪后的论文原图和原始实验表格，只保留图表主体，不使用夹带正文的整页截图。论文缺少清晰架构图时，Agent 会优先调用当前环境可用的图像生成能力；无法生图时则输出 grounded diagram prompt。

辅助脚本支持：

- 从 PDF 提取带页码正文
- 提取候选论文图片
- 自动检测并裁剪论文表格
- 根据论文证据生成架构图或流程图 prompt

## 安装

Codex CLI、IDE Extension 和 Codex app 都支持 Agent Skills。Codex 会从个人目录 `$HOME/.agents/skills` 和仓库内 `.agents/skills` 等位置发现 skills。

### 方式一：让 Codex 安装

在 Codex 中输入：

```text
使用 $skill-installer 从 https://github.com/BY-Elysia/Paper-read-skills/tree/main/llm-paper-reader 安装 llm-paper-reader
```

如果安装后没有立即出现，重新启动 Codex，或在支持的客户端中执行 **Force Reload Skills**。

### 方式二：安装为个人 Skill

安装后，该 skill 会对当前用户的所有项目生效。

Linux、macOS 或 WSL：

```bash
git clone https://github.com/BY-Elysia/Paper-read-skills.git
mkdir -p "$HOME/.agents/skills"
cp -R Paper-read-skills/llm-paper-reader "$HOME/.agents/skills/llm-paper-reader"
```

Windows PowerShell：

```powershell
git clone https://github.com/BY-Elysia/Paper-read-skills.git
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item -Recurse -Force ".\Paper-read-skills\llm-paper-reader" "$HOME\.agents\skills\llm-paper-reader"
```

### 方式三：安装到某个仓库

仅希望当前项目使用时，将 skill 放入项目根目录的 `.agents/skills`：

```bash
mkdir -p .agents/skills
cp -R /path/to/Paper-read-skills/llm-paper-reader .agents/skills/llm-paper-reader
```

## PDF 解析依赖

Skill 本身可以被 Agent 直接读取。若希望使用附带的 PDF 正文、图片和表格提取脚本，需要 Python 3，并安装：

```bash
python -m pip install pymupdf pdfplumber
```

其中 `PyMuPDF` 用于主要的 PDF 解析、图片提取和表格裁剪；`pdfplumber` 是正文提取的备用解析器。

## 使用

安装后，可以让 Codex 自动匹配该 skill，也可以显式调用：

```text
使用 $llm-paper-reader 阅读这篇论文：/path/to/paper.pdf
生成一份中文图文报告，重点讲清模型架构、一次完整训练过程、公式计算和实验结论。
```

默认生成 Markdown 报告。报告中的公式、伪代码、原文图表和实验分析会嵌入对应的讲解位置。

## 目录结构

```text
llm-paper-reader/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/
    ├── extract_paper_text.py
    ├── extract_figures.py
    ├── extract_tables.py
    └── build_diagram_prompt.py
```

## 说明

- 默认输出语言为中文，并保留必要的英文技术术语。
- 原文未明确说明的内容会直接标注，不猜测模型模块、超参数或实验结果。
- 生成图只作为原图缺失时的补充，并应严格基于论文证据。
- `test_outputs/` 是本地测试生成物，不提交到仓库。
