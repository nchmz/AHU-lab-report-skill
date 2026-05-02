# Lab Report - Claude Code Skill

一个基于 Claude Code 的实验报告自动生成工具，专为安徽大学（AHU）学生设计。只需提供实验代码、结果图片和 PPT，即可一键生成符合学校模板要求的 LaTeX 实验报告。

## 功能特性

- **一键生成**：通过 `/lab-report` 命令，自动完成从材料分析到 LaTeX 输出的全流程
- **PPT 内容提取**：自动解析实验 PPT，提取文本内容和图片资源
- **智能编号**：同一科目的实验报告自动递增编号（如 FPGA实验1、FPGA实验2...）
- **环境缓存**：首次运行后自动缓存 Python 环境配置，后续生成无需重复检测
- **去 AI 化写作**：生成的报告正文采用朴实的学术语言，避免 AI 痕迹
- **标准模板**：基于安徽大学实验报告 LaTeX 模板，封面、排版一键搞定

## 安装

### 前置条件

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI 已安装
- Python 3.10+（推荐通过 Conda 管理）
- XeLaTeX 编译环境（用于编译生成的 `.tex` 文件）

### 克隆项目

```bash
git clone https://github.com/<your-username>/skill-project.git
cd skill-project
```

项目会自动识别 `.claude/skills/lab-report/` 下的 skill 配置。

### 安装 Python 依赖

```bash
pip install python-pptx
```

或使用 Conda：

```bash
conda create -n report python=3.10 -y
conda install -n report python-pptx -y
```

## 使用方法

在 Claude Code 中运行：

```
/lab-report code/main.py images/ lab_intro.pptx 线性回归实验
```

**参数说明：**

| 参数 | 说明 | 必填 |
|------|------|------|
| 实验代码路径 | 你的实验代码文件（.py/.c/.m 等） | 是 |
| 实验结果图片目录 | 包含实验结果截图的文件夹 | 是 |
| 实验 PPT 路径 | 实验指导 PPT 文件 | 是 |
| 实验标题 | 报告标题，不填则从 PPT 推断 | 否 |

运行后 skill 会自动询问学号、姓名、专业、课程名称等封面信息。

## 输出结构

```
reports/
└── FPGA实验1/
    ├── report.tex          # 生成的 LaTeX 源文件
    ├── ahu_report.cls      # 模板 class 文件
    ├── background/         # 背景资源
    ├── logo/               # 校徽资源
    └── pic/                # 实验图片
```

### 编译报告

```bash
cd reports/FPGA实验1
xelatex report.tex
```

编译后会生成 `report.pdf`。

## 项目结构

```
.claude/skills/lab-report/
├── SKILL.md                # skill 定义文件
├── config.json             # 本地配置（环境缓存、报告记录）
├── scripts/
│   ├── pptx_extract.py     # PPT 内容提取脚本
│   └── config.py           # 配置管理脚本
└── templates/
    └── Template-for-AHU-report/   # 安徽大学 LaTeX 模板
        ├── ahu_report.cls
        ├── template_experiment.tex
        ├── background/
        └── logo/
```

## 配置说明

skill 会自动维护一个 `config.json` 配置文件，记录：

- **Python 环境**：首次检测后缓存，后续生成跳过环境检测
- **报告历史**：记录已生成的报告，用于自动编号

```json
{
  "python_env": {
    "cmd": "conda run -n pytorch python"
  },
  "reports": {
    "FPGA": [
      { "title": "FPGA实验1" },
      { "title": "FPGA实验2" }
    ]
  }
}
```

## 文本风格

生成的报告正文遵循"去 AI 化"约束：

- 段落化叙述，不使用列表格式
- 朴实精准的学术词汇，避免堆砌辞藻
- 自然的逻辑过渡，不使用机械连接词
- 正文不使用加粗或斜体
- 中文撰写

## 模板来源

本项目使用的 LaTeX 模板基于 [Template-for-AHU-report](https://github.com/Trinkle23897/Template-for-AHU-report)，感谢原作者的贡献。

## 致谢

感谢小米 100t 开源活动提供的算力支持，让本项目得以在 Claude Code 的强大能力下快速迭代和开发。本项目基于小米 MiMo-V2.5-Pro 模型驱动，活动详情请访问：[小米 100t 开源活动](https://100t.xiaomimimo.com/)。
