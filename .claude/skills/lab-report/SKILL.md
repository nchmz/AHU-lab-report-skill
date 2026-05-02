---
name: lab-report
description: 生成安徽大学实验报告 LaTeX 文件
user_invocable: true
---

生成安徽大学实验报告 LaTeX 文件。

## 输入参数

`$ARGUMENTS` 格式：`<实验代码路径> <实验结果图片目录> <实验PPT路径> [实验标题]`

示例：`code/main.py images/ lab_intro.pptx 线性回归实验`

如果用户没有提供参数，请依次询问：
1. 实验代码文件路径
2. 实验结果图片目录路径
3. 实验 PPT 文件路径
4. 实验标题（可选，可从代码/PPT推断）

## 工作流程

### 第0步：检测 Python 环境

**首先检查配置缓存：**
```bash
$PYTHON_CMD_CACHE=$(python .claude/skills/lab-report/scripts/config.py get-python-env)
```

如果缓存不为空，直接使用缓存的命令作为 `PYTHON_CMD`，**跳过下方的环境检测步骤**。

如果缓存为空，则按以下优先级检测 Python 环境，**执行对应的检测命令后根据结果选择分支**：

**1. 检测 conda 是否可用：**
```bash
conda --version
```

**如果 conda 存在：**
```bash
conda env list
```
- 若存在 `pytorch` 环境 → 使用该环境，设置激活命令：
  ```
  PYTHON_CMD="conda run -n pytorch python"
  ```
- 若不存在 `pytorch` 环境 → 创建 `report` 环境：
  ```bash
  conda create -n report python=3.10 -y
  conda install -n report python-pptx -y
  ```
  然后使用：
  ```
  PYTHON_CMD="conda run -n report python"
  ```

**如果 conda 不存在：**

使用 AskUserQuestion 询问用户：
- 选项1：安装 Miniconda（推荐，自动管理环境）
- 选项2：指定已有的 Python 解释器路径
- 选项3：直接使用系统 `python`（需确保已安装 python-pptx）

根据用户选择设置 `PYTHON_CMD` 变量。

**环境确认后，安装依赖并缓存配置：**
```bash
$PYTHON_CMD -m pip install python-pptx
python .claude/skills/lab-report/scripts/config.py set-python-env "$PYTHON_CMD"
```

### 第1步：收集材料

1. 读取实验代码文件，理解代码功能、算法逻辑、输入输出
2. 扫描结果图片目录，列出所有图片文件（png/jpg/pdf）
3. 使用脚本提取 PPT 内容：
   ```bash
   $PYTHON_CMD .claude/skills/lab-report/scripts/pptx_extract.py <PPT路径> <输出目录>
   ```
   然后读取生成的 `text.md` 获取 PPT 文本内容，查看 `images/` 获取 PPT 中的图片

### 第2步：分析实验内容

从代码和 PPT 中提取以下信息：

| 项目 | 来源 |
|------|------|
| 实验标题 | PPT 标题页或用户指定 |
| 实验目的 | PPT 说明或代码注释 |
| 实验原理 | 涉及的算法/理论，从代码推断 |
| 实验步骤 | 代码逻辑流程 |
| 实验结果 | 图片文件名推断含义 |

### 第2.5步：确定实验编号与输出目录

根据实验标题确定**科目名**（去掉"实验X"等后缀），然后使用配置脚本自动生成带编号的完整标题和输出目录：

```bash
# 例如用户输入"FPGA"，脚本会扫描已有报告自动编号
SUBJECT="FPGA"  # 从实验标题中提取的科目名
REPORT_TITLE=$(python .claude/skills/lab-report/scripts/config.py get-report-title "$SUBJECT")
```

- 如果 `reports/` 下已有 `FPGA实验一`，则输出 `FPGA实验二`
- 如果是全新科目，则输出 `{科目}实验一`
- 输出目录为 `reports/$REPORT_TITLE/`

**编号规则**：阿拉伯数字序列（1、2、3...），从已有的最大编号 +1

### 第3步：收集用户信息

向用户询问以下个人信息（用于报告封面）：
- 学号
- 姓名
- 专业
- 课程名称
- 实验日期（默认今天）

### 第4步：生成 LaTeX 文件

读取模板：`.claude/skills/lab-report/templates/Template-for-AHU-report/template_experiment.tex`

按照以下结构生成报告：

```latex
% TEX program=xelatex
\documentclass[experiment]{ahu_report}

\setbgopacity{0.4}

\stuid{用户学号}
\major{用户专业}
\name{用户姓名}
\expdate{实验日期}
\course{课程名称}

\begin{document}
\begin{spacing}{1.25}
    \makeahutitle
  \begin{center}
    {\zihao{2}\songti 实验标题}
  \end{center}

\section{实验目的}
% 用连贯段落描述，不要使用列表
% 将多个目的融合成自然的叙述

\section{实验原理}
% 算法原理、理论基础、公式推导
% 用段落叙述，公式用 $...$ 包裹

\section{实验内容与步骤}
% 用连贯段落描述步骤，不要使用列表
% 用"首先"、"随后"、"接着"等自然过渡词连接

\section{实验代码}
% 核心代码，使用 lstlisting 环境
% 根据代码语言设置 language=Python/C/...
% 添加 caption 和 label

\section{实验结果与分析}
% 插入结果图片
% 每张图片使用 figure[H] 环境
% 使用 subfigure 并排显示相关图片
% 每张图片后用段落分析结果，不要用列表

\section{实验结论}
% 用段落总结实验结果和收获，不要使用列表

\end{spacing}
\end{document}
```

### 第5步：图片处理

图片来源有两处，都需要处理：

**结果图片目录**（用户提供）和 **PPT 解析提取的图片**（`pptx_extract.py` 输出的 `images/` 目录）。

对于每张图片：
1. 复制图片到输出目录的 `pic/` 子目录（两处来源的图片统一放入 `pic/`）
2. 在 LaTeX 中使用 `\includegraphics[width=0.6\textwidth]{pic/文件名}` 引用
3. 根据文件名推断图片含义，撰写 `\caption`
4. 相关图片使用 `subfigure` 并排显示

PPT 中提取的图片通常包含实验原理图、电路图、流程图等，适合用于「实验原理」或「实验内容与步骤」章节。结果图片用于「实验结果与分析」章节。

图片引用格式：
```latex
\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\textwidth]{pic/图片文件名}
    \caption{图片描述}
    \label{fig:标签}
\end{figure}
```

### 第6步：保存输出

1. 创建输出目录：`reports/$REPORT_TITLE/`
2. 将生成的 `.tex` 文件保存为 `report.tex`
3. 复制模板资源到输出目录：
   ```bash
   cp .claude/skills/lab-report/templates/Template-for-AHU-report/ahu_report.cls reports/$REPORT_TITLE/
   cp -r .claude/skills/lab-report/templates/Template-for-AHU-report/background reports/$REPORT_TITLE/
   cp -r .claude/skills/lab-report/templates/Template-for-AHU-report/logo reports/$REPORT_TITLE/
   ```
4. 复制图片到 `reports/$REPORT_TITLE/pic/`
5. 注册报告到配置文件：
   ```bash
   python .claude/skills/lab-report/scripts/config.py add-report "$SUBJECT" "$REPORT_TITLE"
   ```
6. 显示生成结果和编译命令

## 输出结构

```
reports/$REPORT_TITLE/
├── report.tex
├── ahu_report.cls
├── background/
│   ├── background.pdf
│   └── backgroundwps.pdf
├── logo/
│   └── ahu.bmp
└── pic/
    └── 实验结果图片...
```

## 编译命令

```bash
cd reports/$REPORT_TITLE
xelatex report.tex
```

## 文本生成约束（去 AI 化）

生成报告正文时（实验目的、实验原理、实验步骤、实验结果与分析、实验结论），必须遵守以下约束：

### 词汇规范
- 优先使用朴实、精准的学术词汇，避免堆砌辞藻
- 除非特定语境，避免使用 leverage, delve into, tapestry 等被滥用的复杂词汇，改用 use, investigate, context 等
- 只有在必须表达特定技术含义时才使用术语

### 结构自然化
- **严禁使用列表格式**：将所有条目转化为逻辑连贯的普通段落
- 移除机械连接词：删除 First and foremost, It is worth noting that 等生硬过渡词，通过句子间的逻辑递进自然连接
- 减少破折号（—）的使用，改用逗号、括号或从句结构替代

### 排版规范
- **禁用强调格式**：正文中不使用加粗或斜体，通过句式结构体现重点
- 保持 LaTeX 纯净，不引入无关的格式指令

### 修改阈值
- 如果文本已经自然、地道且无明显 AI 特征，保留原文，不为修改而修改
- 生成后进行自查：拟人度检查（语气是否自然）、必要性检查（修改是否真的提升可读性）

### 语言要求
- 报告正文使用**中文**撰写
- 特殊字符需转义（`%`、`_`、`&`）
- 数学公式保留 `$` 符号

## 注意事项

- 代码块使用 `lstlisting` 环境，设置正确的 `language=` 参数（Python/C/Matlab 等）
- 中文内容直接书写，xeCJK 自动处理
- 特殊字符（`$`, `%`, `&`, `_`）在 lstlisting 中无需转义
- 图片路径相对于 `.tex` 文件位置
- 不需要参考文献时只需运行一次 xelatex
