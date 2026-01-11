"""
Chinese AI Terminology Synonym Dictionary

This module provides comprehensive mappings between English and Chinese AI terms
for search optimization in Meilisearch. Supports bidirectional search so users
can find tools using either English or Chinese terminology.

Usage:
    from shared.chinese_synonyms import CHINESE_AI_SYNONYMS, get_synonym_pairs

    # Get all synonym pairs for Meilisearch
    synonyms = get_synonym_pairs()
"""

import logging

logger = logging.getLogger(__name__)


# Comprehensive AI terminology mappings (English ↔ Chinese)
# Format: Each entry creates bidirectional synonyms
CHINESE_AI_SYNONYMS = {
    # === Core AI Concepts ===
    "ai": ["人工智能", "AI"],
    "artificial intelligence": ["人工智能", "AI"],
    "machine learning": ["机器学习", "ML"],
    "ml": ["机器学习", "machine learning"],
    "deep learning": ["深度学习", "DL"],
    "dl": ["深度学习", "deep learning"],
    "neural network": ["神经网络", "NN"],
    "nn": ["神经网络", "neural network"],

    # === NLP & Language Models ===
    "natural language processing": ["自然语言处理", "NLP"],
    "nlp": ["自然语言处理", "natural language processing"],
    "large language model": ["大语言模型", "大模型", "LLM"],
    "llm": ["大语言模型", "大模型", "large language model"],
    "gpt": ["生成预训练模型", "GPT"],
    "transformer": ["转换器", "变换器", "Transformer"],
    "bert": ["伯特", "BERT"],
    "chatbot": ["聊天机器人", "对话机器人", "智能客服"],
    "chat": ["聊天", "对话", "交流"],
    "conversation": ["对话", "会话", "交流"],
    "dialogue": ["对话", "会话"],

    # === Computer Vision ===
    "computer vision": ["计算机视觉", "CV"],
    "cv": ["计算机视觉", "computer vision"],
    "image generation": ["图像生成", "图片生成", "画图"],
    "image recognition": ["图像识别", "图片识别"],
    "object detection": ["目标检测", "物体检测"],
    "face recognition": ["人脸识别", "面部识别"],
    "ocr": ["光学字符识别", "文字识别", "OCR"],

    # === Generative AI ===
    "generative ai": ["生成式AI", "生成式人工智能", "AIGC"],
    "aigc": ["AI生成内容", "生成式AI", "AIGC"],
    "text generation": ["文本生成", "文字生成"],
    "text-to-image": ["文生图", "文本生成图像"],
    "text to image": ["文生图", "文本生成图像"],
    "image-to-text": ["图生文", "图像生成文本"],
    "image to text": ["图生文", "图像生成文本"],
    "text-to-speech": ["文字转语音", "语音合成", "TTS"],
    "tts": ["文字转语音", "语音合成", "text-to-speech"],
    "speech-to-text": ["语音转文字", "语音识别", "STT"],
    "stt": ["语音转文字", "语音识别", "speech-to-text"],
    "video generation": ["视频生成", "视频制作"],

    # === Model Training & Optimization ===
    "training": ["训练", "模型训练"],
    "fine-tuning": ["微调", "精调", "模型微调"],
    "finetune": ["微调", "精调"],
    "pretrain": ["预训练", "pre-training"],
    "pre-training": ["预训练", "pretrain"],
    "prompt": ["提示词", "提示", "prompts"],
    "prompt engineering": ["提示词工程", "提示工程"],
    "few-shot": ["少样本", "小样本", "few-shot learning"],
    "zero-shot": ["零样本", "zero-shot learning"],
    "transfer learning": ["迁移学习", "转移学习"],

    # === RAG & Knowledge ===
    "rag": ["检索增强生成", "RAG"],
    "retrieval augmented generation": ["检索增强生成", "RAG"],
    "embedding": ["嵌入", "向量化", "embeddings"],
    "vector": ["向量", "矢量"],
    "vector database": ["向量数据库", "向量库"],
    "knowledge base": ["知识库", "知识图谱"],
    "semantic search": ["语义搜索", "智能搜索"],

    # === AI Applications ===
    "assistant": ["助手", "助理", "AI助手"],
    "copilot": ["副驾驶", "助手", "智能助手"],
    "agent": ["智能体", "代理", "AI代理"],
    "automation": ["自动化", "智能自动化"],
    "workflow": ["工作流", "流程"],
    "code assistant": ["代码助手", "编程助手"],
    "coding": ["编程", "写代码", "代码"],
    "programming": ["编程", "程序设计"],
    "translation": ["翻译", "机器翻译"],
    "summarization": ["摘要", "总结", "文本摘要"],
    "writing": ["写作", "文案", "创作"],
    "content creation": ["内容创作", "内容生成"],

    # === Popular AI Tools & Platforms ===
    "chatgpt": ["ChatGPT", "聊天GPT"],
    "midjourney": ["Midjourney", "MJ"],
    "stable diffusion": ["Stable Diffusion", "SD"],
    "dall-e": ["DALL-E", "DALLE"],
    "claude": ["Claude", "克劳德"],
    "gemini": ["Gemini", "双子座"],
    "copilot": ["Copilot", "副驾驶"],

    # === Technical Terms ===
    "api": ["接口", "应用程序接口", "API"],
    "model": ["模型", "AI模型"],
    "dataset": ["数据集", "数据"],
    "algorithm": ["算法", "演算法"],
    "inference": ["推理", "推断"],
    "prediction": ["预测", "预估"],
    "classification": ["分类", "分类任务"],
    "clustering": ["聚类", "集群"],
    "regression": ["回归", "回归分析"],

    # === AI Ethics & Safety ===
    "bias": ["偏见", "偏差", "模型偏见"],
    "fairness": ["公平性", "公正性"],
    "privacy": ["隐私", "隐私保护"],
    "security": ["安全", "安全性"],
    "hallucination": ["幻觉", "模型幻觉"],

    # === Performance & Metrics ===
    "accuracy": ["准确率", "精确度"],
    "precision": ["精准率", "查准率"],
    "recall": ["召回率", "查全率"],
    "performance": ["性能", "表现"],
    "optimization": ["优化", "性能优化"],
    "latency": ["延迟", "时延"],
    "throughput": ["吞吐量", "处理量"],

    # === AI Features ===
    "multimodal": ["多模态", "多模"],
    "real-time": ["实时", "即时"],
    "online": ["在线", "线上"],
    "offline": ["离线", "本地"],
    "cloud": ["云", "云端", "云服务"],
    "edge": ["边缘", "边缘计算"],
    "local": ["本地", "离线"],

    # === Chinese-specific Terms ===
    "中文": ["chinese", "中文", "汉语"],
    "简体中文": ["simplified chinese", "简体"],
    "繁体中文": ["traditional chinese", "繁体"],

    # === Action Verbs ===
    "generate": ["生成", "创建", "产生"],
    "create": ["创建", "生成", "制作"],
    "analyze": ["分析", "解析"],
    "detect": ["检测", "识别", "发现"],
    "recognize": ["识别", "辨认"],
    "understand": ["理解", "理解能力"],
    "learn": ["学习", "学会"],
    "predict": ["预测", "预估"],
    "optimize": ["优化", "改进"],
    "enhance": ["增强", "提升", "改善"],

    # === Common Use Cases ===
    "search": ["搜索", "检索", "查找"],
    "recommendation": ["推荐", "推荐系统"],
    "personalization": ["个性化", "定制化"],
    "automation": ["自动化", "自动"],
    "productivity": ["效率", "生产力", "工作效率"],
    "creativity": ["创意", "创造力"],
    "design": ["设计", "设计工具"],
    "art": ["艺术", "艺术创作"],
    "music": ["音乐", "音乐生成"],
    "video": ["视频", "影片"],
    "audio": ["音频", "声音"],
    "voice": ["语音", "声音", "语音识别"],

    # === Business & Enterprise ===
    "enterprise": ["企业", "企业级"],
    "business": ["商业", "业务", "商务"],
    "professional": ["专业", "专业版"],
    "free": ["免费", "免费版"],
    "premium": ["高级", "付费", "专业版"],
    "subscription": ["订阅", "订阅制"],

    # === Additional Models & Architectures ===
    "diffusion": ["扩散", "扩散模型"],
    "gan": ["生成对抗网络", "GAN"],
    "vae": ["变分自编码器", "VAE"],
    "rlhf": ["人类反馈强化学习", "RLHF"],
    "reinforcement learning": ["强化学习", "增强学习"],
    "supervised learning": ["监督学习", "有监督学习"],
    "unsupervised learning": ["无监督学习", "非监督学习"],

    # === Platform & Deployment ===
    "saas": ["软件即服务", "SaaS"],
    "open source": ["开源", "开放源代码"],
    "opensource": ["开源", "开放源代码"],
    "plugin": ["插件", "扩展"],
    "extension": ["扩展", "插件"],
    "integration": ["集成", "整合"],
    "sdk": ["软件开发工具包", "SDK"],

    # === Data & Processing ===
    "data": ["数据", "资料"],
    "processing": ["处理", "加工"],
    "analysis": ["分析", "解析"],
    "visualization": ["可视化", "视觉化"],
    "annotation": ["标注", "注释"],
    "labeling": ["标注", "打标签"],
}


def get_synonym_pairs() -> list[list[str]]:
    """
    Convert the synonym dictionary to Meilisearch-compatible format.

    Meilisearch expects synonyms as a list of lists, where each inner list
    contains terms that are synonymous with each other.

    Returns:
        list[list[str]]: List of synonym groups for Meilisearch configuration

    Example:
        [
            ["ai", "人工智能", "AI"],
            ["machine learning", "机器学习", "ML"],
            ...
        ]
    """
    synonym_pairs = []

    for key, values in CHINESE_AI_SYNONYMS.items():
        # Create a synonym group with the key and all its values
        # This creates bidirectional synonyms
        synonym_group = [key] + values
        synonym_pairs.append(synonym_group)

    logger.info(f"Generated {len(synonym_pairs)} synonym groups with {sum(len(group) for group in synonym_pairs)} total terms")

    return synonym_pairs


def get_flat_synonyms() -> dict[str, list[str]]:
    """
    Get the raw synonym dictionary.

    Returns:
        dict[str, list[str]]: Raw synonym mappings
    """
    return CHINESE_AI_SYNONYMS


def search_term_synonyms(term: str) -> list[str]:
    """
    Find all synonyms for a given search term (case-insensitive).

    Args:
        term: The search term to find synonyms for

    Returns:
        list[str]: List of synonyms including the original term

    Example:
        >>> search_term_synonyms("ai")
        ["ai", "人工智能", "AI"]
    """
    term_lower = term.lower().strip()

    # Check if term is a key
    if term_lower in CHINESE_AI_SYNONYMS:
        return [term_lower] + CHINESE_AI_SYNONYMS[term_lower]

    # Check if term is in any values
    for key, values in CHINESE_AI_SYNONYMS.items():
        if term in values or term_lower in [v.lower() for v in values]:
            return [key] + values

    # No synonyms found, return original term
    return [term]


def get_statistics() -> dict:
    """
    Get statistics about the synonym dictionary.

    Returns:
        dict: Statistics including total terms, groups, etc.
    """
    total_groups = len(CHINESE_AI_SYNONYMS)
    total_terms = sum(len(values) + 1 for values in CHINESE_AI_SYNONYMS.values())  # +1 for the key

    # Count Chinese vs English terms
    chinese_terms = 0
    english_terms = 0

    for key, values in CHINESE_AI_SYNONYMS.items():
        all_terms = [key] + values
        for term in all_terms:
            # Simple heuristic: if contains Chinese characters
            if any('\u4e00' <= char <= '\u9fff' for char in term):
                chinese_terms += 1
            else:
                english_terms += 1

    return {
        "total_groups": total_groups,
        "total_terms": total_terms,
        "chinese_terms": chinese_terms,
        "english_terms": english_terms,
        "average_synonyms_per_group": round(total_terms / total_groups, 2) if total_groups > 0 else 0
    }


# Example usage and validation
if __name__ == "__main__":
    # Print statistics
    stats = get_statistics()
    print("=== Chinese AI Synonym Dictionary Statistics ===")
    print(f"Total synonym groups: {stats['total_groups']}")
    print(f"Total terms: {stats['total_terms']}")
    print(f"Chinese terms: {stats['chinese_terms']}")
    print(f"English terms: {stats['english_terms']}")
    print(f"Average synonyms per group: {stats['average_synonyms_per_group']}")
    print()

    # Test some lookups
    print("=== Example Synonym Lookups ===")
    test_terms = ["ai", "人工智能", "chatbot", "大模型", "code"]
    for term in test_terms:
        synonyms = search_term_synonyms(term)
        print(f"{term} -> {synonyms}")
    print()

    # Show sample synonym pairs for Meilisearch
    print("=== Sample Synonym Pairs for Meilisearch (first 5) ===")
    pairs = get_synonym_pairs()
    for i, pair in enumerate(pairs[:5], 1):
        print(f"{i}. {pair}")
