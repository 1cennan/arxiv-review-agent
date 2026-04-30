import streamlit as st
import urllib.request
import feedparser
from openai import OpenAI
import httpx  
import json

# ==========================================
# 页面基础设置
# ==========================================
st.set_page_config(page_title="AI 文献检索与综述 Agent", page_icon="🎓", layout="wide")

st.title("🎓 AI 学术文献检索与综述 Agent")
st.markdown("输入研究方向或关键词，Agent 将自动检索 ArXiv 上的最新相关论文，并生成结构化的文献综述。")

# ==========================================
# 侧边栏：配置区
# ==========================================
with st.sidebar:
    st.header("⚙️ Agent 配置")
    api_key = st.text_input("请输入你的 API Key", type="password")
    base_url = st.text_input("API Base URL (必填)", value="https://api.openai.com/v1")
    model_name = st.text_input("模型名称", value="gpt-3.5-turbo")
    
    st.markdown("---")
    max_results = st.slider("最大检索篇数", min_value=3, max_value=10, value=5)

# ==========================================
# 核心函数定义
# ==========================================
def search_arxiv(query, max_results=5):
    formatted_query = query.replace(' ', '+')
    url = f'http://export.arxiv.org/api/query?search_query=all:{formatted_query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending'
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=15.0)
        feed = feedparser.parse(response)
        
        papers = []
        for entry in feed.entries:
            papers.append({
                "title": entry.title.replace('\n', ' '),
                "authors": [author.name for author in entry.authors],
                "published": entry.published[:10],
                "summary": entry.summary.replace('\n', ' '),
                "link": entry.link
            })
        return papers
    except Exception as e:
        return None

def generate_literature_review(client, papers, query, model_name):
    context = ""
    for i, p in enumerate(papers):
        context += f"【文献 {i+1}】\n标题: {p['title']}\n摘要: {p['summary']}\n\n"
        
    system_prompt = """
    你是一个资深的工程与计算机科学领域的研究员。
    请根据用户提供的多篇学术文献摘要，针对检索主题写一份小型的文献综述（Literature Review）。
    请输出 JSON 格式，包含以下字段：
    1. "overview": 针对该研究方向的总体进展总结（约200字）。
    2. "methodologies": 提炼这些文献中主要使用的核心技术或方法论（数组格式）。
    3. "paper_insights": 对每篇文献的“一句话核心贡献”总结（数组格式，顺序需与提供文献对应）。
    
    【极其重要】：你必须严格只返回 JSON 字符串！绝对不要包含任何 Markdown 标记。
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"检索主题：{query}\n\n文献列表：\n{context}"}
            ]
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 主交互逻辑
# ==========================================
search_query = st.text_input("🔍 输入检索关键词 (支持英文，如 'robot', 'agent' 等)：", value="robotic arm motion retargeting")

if st.button("🚀 开始检索与综述生成", type="primary"):
    if not api_key:
        st.warning("⚠️ 请先在左侧边栏填写 API Key！")
    else:
        custom_client = httpx.Client(proxy=None, trust_env=False, timeout=120.0)
        client = OpenAI(api_key=api_key, base_url=base_url, http_client=custom_client)
        
        # 初始化变量
        papers = None
        review_result = None
        
        with st.status("Agent 正在执行文献调研...", expanded=True) as status:
            st.write(f"🌐 [1/3] 正在从 ArXiv 检索关于 '{search_query}' 的最新文献...")
            papers = search_arxiv(search_query, max_results)
            
            if not papers:
                status.update(label="检索失败", state="error", expanded=True)
                st.error("未能从 ArXiv 获取到文献，请检查网络或更换关键词。")
            else:
                st.write(f"✅ 成功抓取 {len(papers)} 篇相关文献。")
                st.write("🧠 [2/3] 综述 Agent 正在阅读摘要并提取核心方法论...")
                st.write("✍️ [3/3] 正在使用大模型生成结构化文献综述报告...")
                
                review_result = generate_literature_review(client, papers, search_query, model_name)
                
                if "error" in review_result:
                    status.update(label="处理失败", state="error", expanded=True)
                    st.error(f"API 调用失败: {review_result['error']}")
                else:
                    status.update(label="文献调研完成！", state="complete", expanded=False)
        
        # ==============================================================
        # 【关键修复】：把这部分代码移出了 st.status，彻底解决嵌套报错
        # ==============================================================
        if papers and review_result and "error" not in review_result:
            st.success(f"🎉 成功生成 '{search_query}' 的专属文献综述！")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("💡 AI 综合调研报告")
                st.markdown("**总体研究进展:**")
                st.info(review_result.get('overview', '未生成概述'))
                
                st.markdown("**主要研究方法/技术栈:**")
                for method in review_result.get('methodologies', []):
                    st.markdown(f"- {method}")
            
            with col2:
                st.subheader("📚 参考文献列表")
                insights = review_result.get('paper_insights', [])
                
                for i, p in enumerate(papers):
                    with st.expander(f"[{p['published']}] {p['title']}", expanded=False):
                        st.markdown(f"**Authors:** {', '.join(p['authors'])}")
                        st.markdown(f"**🔗 [ArXiv Link]({p['link']})**")
                        
                        if i < len(insights):
                            st.markdown("**🤖 AI 核心贡献提炼:**")
                            st.success(insights[i])
                        
                        st.markdown("**Abstract:**")
                        st.caption(p['summary'])
