# Research-to-Investment Agent（AI投资研究智能体）

一个基于大模型的多Agent协作系统，用于将非结构化的公司资料、论文内容和产品信息自动转化为结构化的投资研究备忘录（Investment Memo）。

---

## 🚀 项目简介

在AI投资研究和技术评估过程中，分析师通常需要阅读大量公司介绍、论文摘要和产品文档，并手动整理核心信息、技术判断和风险分析。

本项目通过构建一个多Agent协作系统，将这一流程自动化，实现从“原始文本输入”到“结构化投资结论输出”的完整流程，大幅提升研究效率。

---

## 🧠 核心功能

- 多Agent协作分析（5个独立智能体）
- 长文本理解与信息提取
- 技术与商业双维度分析
- 风险识别与尽调问题生成
- 自动生成结构化 Investment Memo
- 基于 Streamlit 的可视化交互界面

---

## 🏗 系统架构

系统采用多Agent流水线架构：

1. 信息提取 Agent  
2. 技术分析 Agent  
3. 商业分析 Agent  
4. 风险分析 Agent  
5. 投资备忘录生成 Agent  

每个Agent负责不同分析任务，最终生成统一结构的投资研究报告。

---

## 📊 输出内容

系统自动生成以下结构化内容：

- Executive Summary（项目总结）
- Project Overview（项目概述）
- Technology Analysis（技术分析）
- Market & Business Analysis（商业分析）
- Risk Analysis（风险分析）
- Due Diligence Questions（尽调问题）
- Go / No-Go 投资建议

---

## 💡 应用场景

- AI创业项目初筛
- 技术可行性评估
- 投资研究辅助
- 科研成果商业化分析

---

## ⚡ 项目价值

本项目展示了大模型从“对话工具”向“决策系统”的演进路径，通过多Agent协作和结构化输出，实现真正可用于业务流程的AI应用。

---

## 🛠 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
