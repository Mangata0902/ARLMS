import os
from sqlalchemy.orm import Session
from openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.models.all_models import Material, AIReadAnalytic
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 1. 初始化与 Ingestion 相同的 Embedding 模型
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 2. 向量数据库存储路径
CHROMA_DB_DIR = os.path.join("storage", "chroma_db")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

async def get_chat_response(material_id: int, user_query: str, db: Session):
    """
    RAG 对话核心逻辑
    """
    # --- A. 获取文档对应的向量索引 ID ---
    material = db.query(Material).filter(Material.material_id == material_id).first()
    if not material or not material.vector_index:
        return "抱歉，该文档尚未完成向量化索引，无法进行深度对话。"

    vector_collection_name = material.vector_index

    # --- B. 向量检索：从 ChromaDB 中寻找最相关的片段 ---
    # 加载该文档专属的向量集合
    vector_db = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings,
        collection_name=vector_collection_name
    )
    
    # 检索最相关的 5 个片段 (k=5)
    # score 越小表示越相关
    search_results = vector_db.similarity_search(user_query, k=5)
    
    # 将检索到的片段拼接成背景上下文
    context_segments = [doc.page_content for doc in search_results]
    context_text = "\n\n---\n\n".join(context_segments)

    # --- C. 构建增强 Prompt 喂给 DeepSeek ---
    system_prompt = """你是一位严谨的学术导师。
    我会为你提供学生论文中的【相关片段】。请你结合这些片段回答学生的问题。
    
    规则：
    1. 如果片段中包含答案，请详细回答并引用原文逻辑。
    2. 如果片段中完全没有提到相关信息，请诚实告知：“在论文的相关章节中未找到关于此问题的具体描述”，不要凭空捏造。
    3. 保持学术、客观、鼓励的语气。
    """

    user_prompt = f"""
    【参考资料（来自论文原文）】：
    {context_text}

    【学生提问】：
    {user_query}

    请根据参考资料给出你的指导建议：
    """

    # --- D. 调用 DeepSeek ---
    response = client.chat.completions.create(
        model="deepseek-chat", # 或者使用 deepseek-reasoner (R1) 效果更好
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=False
    )

    return response.choices[0].message.content