# 🎓 AI Literature Review Agent

基于大语言模型（LLMs）的学术文献检索与自动综述生成工具。专为解决科研开发人员在面对海量论文时“检索效率低、快速评估难”的痛点而设计。

## ✨ 核心特性
- **自动化文献抓取**: 自动连接 ArXiv 开放 API，并具备反爬虫伪装机制，稳定抓取最新文献。
- **跨模型兼容**: 完美支持 OpenAI 及 Claude 系列（如 Claude 3.5 Sonnet），兼容各大第三方中转 API。
- **结构化知识萃取**: 长链推理分析多篇摘要，自动提炼“总体研究进展”、“核心技术/方法论”以及“单篇核心贡献”。
- **开箱即用的 Web UI**: 基于 Streamlit 构建，提供清爽的侧边栏配置与响应式结果展示。

## 🚀 快速运行
1. 安装依赖：`pip install -r requirements.txt`
2. 启动应用：`streamlit run app.py`
3. 在网页左侧填入你的 API Key 和 Base URL，输入研究方向即可开始检索。
<img width="1850" height="971" alt="运行页面" src="https://github.com/user-attachments/assets/cb7a603e-ae5d-4e35-842c-6349ce0838a6" />
