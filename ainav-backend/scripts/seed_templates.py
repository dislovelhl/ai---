import asyncio
import uuid
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import os
import sys

# Adjust sys.path to import shared and app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.config import settings
from shared.database import SessionLocal, engine
from shared.models import AgentWorkflow, User


async def seed_content_generation_templates():
    """Create 3 content generation workflow templates"""
    async with SessionLocal() as db:
        # 1. Get a user (templates need to be owned by someone)
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            print("❌ No user found. Please create a user first.")
            print("   You can run: cd ainav-backend && python seed_users.py")
            return

        print(f"✅ Using user: {user.username} ({user.email})")

        # Define content generation templates
        templates = [
            {
                "name": "Blog Article Generator",
                "name_zh": "博客文章生成器",
                "slug": "blog-article-generator",
                "description": "Generate high-quality blog articles with SEO optimization, outlines, and engaging content.",
                "description_zh": "智能生成高质量博客文章,包含SEO优化、文章大纲和吸引人的内容。支持多种写作风格,自动生成标题、摘要和标签建议。",
                "category": "content-generation",
                "use_case": "Content creators, bloggers, and marketers who need to produce SEO-friendly blog posts efficiently",
                "usage_instructions_zh": """### 使用步骤

1. **输入主题**: 输入你想写的博客主题或关键词
2. **选择风格**: 选择文章风格(专业/轻松/技术/故事化)
3. **设置长度**: 指定目标字数(800-3000字)
4. **SEO设置**: 可选填入目标关键词和受众
5. **生成文章**: 系统将自动生成:
   - 吸引人的标题(含3个备选)
   - 完整文章大纲
   - 正文内容
   - SEO元描述
   - 相关标签建议

### 适用场景
- 个人博客内容创作
- 企业博客运营
- 技术文档撰写
- 产品评测文章
- 行业观点文章

### 输出示例
生成的文章包含结构化内容,可直接复制到WordPress、掘金、知乎等平台使用。""",
                "tags": ["content-creation", "blogging", "seo", "writing", "marketing"],
                "icon": "📝",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个专业的内容创作专家,擅长撰写引人入胜的博客文章。你的文章结构清晰、观点鲜明、SEO友好,能够吸引读者并提升搜索引擎排名。",
                "temperature": 0.7,
                "is_public": True,
                "is_template": True,
                "star_count": 0,
                "fork_count": 0,
                "run_count": 0,
                "graph_json": {
                    "nodes": [
                        {
                            "id": "input-1",
                            "type": "input",
                            "position": {"x": 100, "y": 100},
                            "data": {
                                "label": "用户输入",
                                "fields": [
                                    {"name": "topic", "type": "text", "label": "博客主题", "required": True},
                                    {"name": "style", "type": "select", "label": "写作风格", "options": ["专业", "轻松", "技术", "故事化"], "default": "专业"},
                                    {"name": "word_count", "type": "number", "label": "目标字数", "default": 1500},
                                    {"name": "keywords", "type": "text", "label": "SEO关键词(可选)", "required": False}
                                ]
                            }
                        },
                        {
                            "id": "llm-1",
                            "type": "llm",
                            "position": {"x": 400, "y": 100},
                            "data": {
                                "label": "生成文章大纲",
                                "prompt": "根据主题「{{topic}}」,风格为{{style}},生成一个清晰的博客文章大纲,包括:\n1. 3个吸引人的标题选项\n2. 引言要点\n3. 3-5个主要章节\n4. 结论要点\n\n目标字数: {{word_count}}字\nSEO关键词: {{keywords}}",
                                "model": "deepseek-chat",
                                "temperature": 0.8
                            }
                        },
                        {
                            "id": "llm-2",
                            "type": "llm",
                            "position": {"x": 700, "y": 100},
                            "data": {
                                "label": "撰写完整文章",
                                "prompt": "基于以下大纲,撰写一篇完整的博客文章:\n\n{{llm-1.output}}\n\n要求:\n- 使用{{style}}风格\n- 总字数约{{word_count}}字\n- 自然融入关键词: {{keywords}}\n- 段落清晰,逻辑连贯\n- 包含具体例子或数据支持观点",
                                "model": "deepseek-chat",
                                "temperature": 0.7
                            }
                        },
                        {
                            "id": "llm-3",
                            "type": "llm",
                            "position": {"x": 1000, "y": 100},
                            "data": {
                                "label": "生成SEO元信息",
                                "prompt": "为以下文章生成SEO优化内容:\n\n{{llm-2.output}}\n\n请生成:\n1. 元描述(150-160字)\n2. 5-10个相关标签\n3. 社交媒体分享文案(适用于微信、微博)",
                                "model": "deepseek-chat",
                                "temperature": 0.6
                            }
                        },
                        {
                            "id": "output-1",
                            "type": "output",
                            "position": {"x": 1300, "y": 100},
                            "data": {
                                "label": "文章输出",
                                "format": "markdown",
                                "fields": [
                                    {"name": "outline", "source": "llm-1.output", "label": "文章大纲"},
                                    {"name": "article", "source": "llm-2.output", "label": "完整文章"},
                                    {"name": "seo_meta", "source": "llm-3.output", "label": "SEO信息"}
                                ]
                            }
                        }
                    ],
                    "edges": [
                        {"id": "e1", "source": "input-1", "target": "llm-1", "type": "default"},
                        {"id": "e2", "source": "llm-1", "target": "llm-2", "type": "default"},
                        {"id": "e3", "source": "llm-2", "target": "llm-3", "type": "default"},
                        {"id": "e4", "source": "llm-3", "target": "output-1", "type": "default"}
                    ],
                    "viewport": {"x": 0, "y": 0, "zoom": 0.8}
                },
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "博客主题"},
                        "style": {"type": "string", "enum": ["专业", "轻松", "技术", "故事化"], "default": "专业"},
                        "word_count": {"type": "integer", "default": 1500, "minimum": 800, "maximum": 3000},
                        "keywords": {"type": "string", "description": "SEO关键词(可选)"}
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "Social Media Post Creator",
                "name_zh": "社交媒体文案生成器",
                "slug": "social-media-post-creator",
                "description": "Create engaging social media posts optimized for different platforms (WeChat, Weibo, Xiaohongshu, Twitter, LinkedIn).",
                "description_zh": "为不同社交平台(微信、微博、小红书、Twitter、LinkedIn)生成吸引人的文案。自动适配平台特点,包含话题标签、表情符号和行动号召。",
                "category": "content-generation",
                "use_case": "Social media managers, influencers, and businesses need platform-specific engaging content quickly",
                "usage_instructions_zh": """### 使用步骤

1. **选择平台**: 选择目标社交媒体平台
   - 微信公众号
   - 微博
   - 小红书
   - Twitter/X
   - LinkedIn

2. **输入内容**: 简要描述要发布的内容主题或产品
3. **设置风格**: 选择文案风格(正式/活泼/专业/情感化)
4. **目标受众**: 描述目标受众特征(可选)
5. **生成文案**: 系统将生成:
   - 3个版本的平台适配文案
   - 相关话题标签
   - 合适的表情符号
   - 行动号召(CTA)
   - 发布时间建议

### 平台适配特点
- **微信**: 长文案,层次分明,专业感
- **微博**: 140字精炼,话题标签,热点结合
- **小红书**: 种草风格,表情丰富,实用攻略
- **Twitter**: 简洁有力,话题标签,互动性强
- **LinkedIn**: 专业见解,行业深度,价值导向

### 适用场景
- 产品推广
- 活动宣传
- 品牌建设
- 个人IP打造
- 节日营销

### 输出示例
每个平台生成3个文案变体,包含完整的标签和emoji,可直接复制使用。""",
                "tags": ["social-media", "marketing", "copywriting", "engagement", "multi-platform"],
                "icon": "📱",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个社交媒体营销专家,深谙各个平台的内容特点和用户心理。你的文案能够引发共鸣、促进互动,并有效传达品牌价值。",
                "temperature": 0.8,
                "is_public": True,
                "is_template": True,
                "star_count": 0,
                "fork_count": 0,
                "run_count": 0,
                "graph_json": {
                    "nodes": [
                        {
                            "id": "input-1",
                            "type": "input",
                            "position": {"x": 100, "y": 100},
                            "data": {
                                "label": "用户输入",
                                "fields": [
                                    {"name": "content_topic", "type": "text", "label": "内容主题", "required": True},
                                    {"name": "platform", "type": "select", "label": "目标平台", "options": ["微信公众号", "微博", "小红书", "Twitter", "LinkedIn"], "required": True},
                                    {"name": "tone", "type": "select", "label": "文案风格", "options": ["正式", "活泼", "专业", "情感化"], "default": "活泼"},
                                    {"name": "target_audience", "type": "text", "label": "目标受众", "required": False}
                                ]
                            }
                        },
                        {
                            "id": "llm-1",
                            "type": "llm",
                            "position": {"x": 400, "y": 100},
                            "data": {
                                "label": "分析平台特点",
                                "prompt": "分析{{platform}}的内容特点和用户偏好,为主题「{{content_topic}}」制定内容策略。\n\n考虑因素:\n- 平台内容格式特点\n- 用户活跃时间\n- 热门话题形式\n- 互动方式\n\n目标受众: {{target_audience}}\n风格要求: {{tone}}",
                                "model": "deepseek-chat",
                                "temperature": 0.7
                            }
                        },
                        {
                            "id": "llm-2",
                            "type": "llm",
                            "position": {"x": 700, "y": 100},
                            "data": {
                                "label": "生成文案变体",
                                "prompt": "基于策略分析:\n{{llm-1.output}}\n\n为{{platform}}生成3个不同角度的文案,主题「{{content_topic}}」\n\n每个文案包含:\n1. 引人注目的开头\n2. 核心内容(符合{{tone}}风格)\n3. 适当的表情符号\n4. 行动号召(CTA)\n5. 相关话题标签\n\n字数要求:\n- 微博/Twitter: 100-140字\n- 小红书: 200-300字\n- 微信/LinkedIn: 300-500字",
                                "model": "deepseek-chat",
                                "temperature": 0.85
                            }
                        },
                        {
                            "id": "llm-3",
                            "type": "llm",
                            "position": {"x": 1000, "y": 100},
                            "data": {
                                "label": "优化与建议",
                                "prompt": "对以下文案进行优化和补充:\n{{llm-2.output}}\n\n请提供:\n1. 最佳发布时间建议\n2. 可能的话题标签(5-8个)\n3. 配图建议(风格、主题)\n4. 互动策略(如何引导评论)\n5. A/B测试建议",
                                "model": "deepseek-chat",
                                "temperature": 0.6
                            }
                        },
                        {
                            "id": "output-1",
                            "type": "output",
                            "position": {"x": 1300, "y": 100},
                            "data": {
                                "label": "文案输出",
                                "format": "structured",
                                "fields": [
                                    {"name": "strategy", "source": "llm-1.output", "label": "内容策略"},
                                    {"name": "posts", "source": "llm-2.output", "label": "文案变体"},
                                    {"name": "optimization", "source": "llm-3.output", "label": "优化建议"}
                                ]
                            }
                        }
                    ],
                    "edges": [
                        {"id": "e1", "source": "input-1", "target": "llm-1", "type": "default"},
                        {"id": "e2", "source": "llm-1", "target": "llm-2", "type": "default"},
                        {"id": "e3", "source": "llm-2", "target": "llm-3", "type": "default"},
                        {"id": "e4", "source": "llm-3", "target": "output-1", "type": "default"}
                    ],
                    "viewport": {"x": 0, "y": 0, "zoom": 0.8}
                },
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_topic": {"type": "string", "description": "内容主题"},
                        "platform": {"type": "string", "enum": ["微信公众号", "微博", "小红书", "Twitter", "LinkedIn"]},
                        "tone": {"type": "string", "enum": ["正式", "活泼", "专业", "情感化"], "default": "活泼"},
                        "target_audience": {"type": "string", "description": "目标受众(可选)"}
                    },
                    "required": ["content_topic", "platform"]
                }
            },
            {
                "name": "Email Marketing Writer",
                "name_zh": "邮件营销文案生成器",
                "slug": "email-marketing-writer",
                "description": "Create compelling email marketing campaigns with subject lines, body content, and CTAs optimized for conversion.",
                "description_zh": "生成高转化率的营销邮件,包含吸引人的主题行、正文内容和行动号召。支持多种邮件类型,自动A/B测试变体生成。",
                "category": "content-generation",
                "use_case": "Email marketers and businesses need high-converting email campaigns for newsletters, promotions, and nurturing",
                "usage_instructions_zh": """### 使用步骤

1. **选择邮件类型**:
   - 欢迎邮件(Welcome)
   - 促销邮件(Promotion)
   - 新闻通讯(Newsletter)
   - 客户关怀(Nurture)
   - 再营销(Re-engagement)

2. **输入基本信息**:
   - 产品/服务名称
   - 核心卖点或优惠
   - 目标受众描述

3. **设置参数**:
   - 邮件风格(正式/亲切/紧迫)
   - 是否包含优惠码
   - 期望行动(购买/注册/下载等)

4. **生成邮件**: 系统将生成:
   - 3个A/B测试主题行
   - 完整邮件正文(HTML友好)
   - 醒目的CTA按钮文案
   - 预览文本建议
   - 发送时间优化建议

### 邮件类型说明
- **欢迎邮件**: 建立首次连接,设定期望
- **促销邮件**: 推动即时购买,限时优惠
- **新闻通讯**: 提供价值,维护关系
- **客户关怀**: 教育用户,建立信任
- **再营销**: 唤回流失用户,重新激活

### 适用场景
- 电商促销活动
- SaaS产品推广
- 课程招生
- 活动邀请
- 用户留存

### 输出示例
生成的邮件包含完整的HTML结构提示,可直接导入Mailchimp、SendGrid等邮件营销平台。

### 优化建议
- 主题行保持在30-50字符
- 正文使用扫描友好格式
- CTA清晰且单一
- 移动端优先设计""",
                "tags": ["email-marketing", "conversion", "copywriting", "campaigns", "automation"],
                "icon": "✉️",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个邮件营销专家,深谙用户心理和转化优化。你的邮件主题行吸引人打开,正文内容促进行动,CTA设计推动转化。你了解反垃圾邮件规则,确保高送达率。",
                "temperature": 0.75,
                "is_public": True,
                "is_template": True,
                "star_count": 0,
                "fork_count": 0,
                "run_count": 0,
                "graph_json": {
                    "nodes": [
                        {
                            "id": "input-1",
                            "type": "input",
                            "position": {"x": 100, "y": 100},
                            "data": {
                                "label": "用户输入",
                                "fields": [
                                    {"name": "email_type", "type": "select", "label": "邮件类型", "options": ["欢迎邮件", "促销邮件", "新闻通讯", "客户关怀", "再营销"], "required": True},
                                    {"name": "product_name", "type": "text", "label": "产品/服务名称", "required": True},
                                    {"name": "key_benefit", "type": "text", "label": "核心卖点/优惠", "required": True},
                                    {"name": "target_audience", "type": "text", "label": "目标受众", "required": False},
                                    {"name": "tone", "type": "select", "label": "邮件风格", "options": ["正式", "亲切", "紧迫"], "default": "亲切"},
                                    {"name": "desired_action", "type": "text", "label": "期望行动", "default": "购买"}
                                ]
                            }
                        },
                        {
                            "id": "llm-1",
                            "type": "llm",
                            "position": {"x": 400, "y": 50},
                            "data": {
                                "label": "生成主题行",
                                "prompt": "为{{email_type}}生成3个A/B测试主题行变体:\n\n产品: {{product_name}}\n卖点: {{key_benefit}}\n受众: {{target_audience}}\n风格: {{tone}}\n\n要求:\n1. 长度30-50字符\n2. 包含好奇、紧迫或利益元素\n3. 避免垃圾邮件触发词\n4. 适合移动端显示\n\n为每个主题行说明预期打开率提升策略。",
                                "model": "deepseek-chat",
                                "temperature": 0.85
                            }
                        },
                        {
                            "id": "llm-2",
                            "type": "llm",
                            "position": {"x": 400, "y": 250},
                            "data": {
                                "label": "撰写邮件正文",
                                "prompt": "撰写{{email_type}}的完整邮件正文:\n\n产品: {{product_name}}\n卖点: {{key_benefit}}\n风格: {{tone}}\n目标行动: {{desired_action}}\n\n邮件结构:\n1. 个性化问候\n2. 引人入胜的开头(解决痛点或引发好奇)\n3. 核心价值阐述(2-3个要点)\n4. 社会证明或紧迫性元素\n5. 清晰的CTA(行动号召)\n6. 专业的签名\n\n格式要求:\n- 短段落,易扫描\n- 使用子标题和列表\n- 突出关键词\n- 移动端友好\n\n字数: 200-400字",
                                "model": "deepseek-chat",
                                "temperature": 0.7
                            }
                        },
                        {
                            "id": "llm-3",
                            "type": "llm",
                            "position": {"x": 700, "y": 150},
                            "data": {
                                "label": "优化CTA和补充元素",
                                "prompt": "基于邮件正文:\n{{llm-2.output}}\n\n提供以下优化:\n\n1. **CTA按钮文案**(3个变体):\n   - 针对行动: {{desired_action}}\n   - 使用行动导向语言\n   - 传达价值或紧迫性\n\n2. **预览文本**(50-100字符):\n   - 补充主题行\n   - 提供额外价值信息\n\n3. **HTML结构建议**:\n   - 关键元素位置\n   - 颜色和字体建议\n   - 图片使用建议\n\n4. **发送优化**:\n   - 最佳发送时间(基于{{email_type}})\n   - 细分受众建议\n   - A/B测试策略",
                                "model": "deepseek-chat",
                                "temperature": 0.65
                            }
                        },
                        {
                            "id": "llm-4",
                            "type": "llm",
                            "position": {"x": 1000, "y": 150},
                            "data": {
                                "label": "反垃圾检查",
                                "prompt": "对以下邮件内容进行反垃圾邮件检查:\n\n主题行: {{llm-1.output}}\n正文: {{llm-2.output}}\n\n检查项:\n1. 垃圾邮件触发词识别\n2. 大写字母使用比例\n3. 符号和标点使用\n4. 链接和图片比例\n5. 取消订阅链接提醒\n\n提供:\n- 垃圾邮件风险评分(0-10)\n- 具体问题和修改建议\n- 合规性检查(GDPR, CAN-SPAM)",
                                "model": "deepseek-chat",
                                "temperature": 0.5
                            }
                        },
                        {
                            "id": "output-1",
                            "type": "output",
                            "position": {"x": 1300, "y": 150},
                            "data": {
                                "label": "邮件输出",
                                "format": "structured",
                                "fields": [
                                    {"name": "subject_lines", "source": "llm-1.output", "label": "主题行变体"},
                                    {"name": "email_body", "source": "llm-2.output", "label": "邮件正文"},
                                    {"name": "cta_optimization", "source": "llm-3.output", "label": "CTA优化"},
                                    {"name": "spam_check", "source": "llm-4.output", "label": "反垃圾检查"}
                                ]
                            }
                        }
                    ],
                    "edges": [
                        {"id": "e1", "source": "input-1", "target": "llm-1", "type": "default"},
                        {"id": "e2", "source": "input-1", "target": "llm-2", "type": "default"},
                        {"id": "e3", "source": "llm-1", "target": "llm-3", "type": "default"},
                        {"id": "e4", "source": "llm-2", "target": "llm-3", "type": "default"},
                        {"id": "e5", "source": "llm-1", "target": "llm-4", "type": "default"},
                        {"id": "e6", "source": "llm-2", "target": "llm-4", "type": "default"},
                        {"id": "e7", "source": "llm-4", "target": "output-1", "type": "default"}
                    ],
                    "viewport": {"x": 0, "y": 0, "zoom": 0.75}
                },
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "email_type": {"type": "string", "enum": ["欢迎邮件", "促销邮件", "新闻通讯", "客户关怀", "再营销"]},
                        "product_name": {"type": "string", "description": "产品或服务名称"},
                        "key_benefit": {"type": "string", "description": "核心卖点或优惠"},
                        "target_audience": {"type": "string", "description": "目标受众描述"},
                        "tone": {"type": "string", "enum": ["正式", "亲切", "紧迫"], "default": "亲切"},
                        "desired_action": {"type": "string", "description": "期望用户采取的行动", "default": "购买"}
                    },
                    "required": ["email_type", "product_name", "key_benefit"]
                }
            }
        ]

        # Insert templates into database
        created_count = 0
        skipped_count = 0

        for template_data in templates:
            # Check if template already exists
            existing = await db.execute(
                select(AgentWorkflow).where(AgentWorkflow.slug == template_data["slug"])
            )
            if existing.scalar_one_or_none():
                print(f"⏭️  Skipped: {template_data['name_zh']} (already exists)")
                skipped_count += 1
                continue

            # Create template
            template = AgentWorkflow(
                id=uuid.uuid4(),
                user_id=user.id,
                **template_data
            )
            db.add(template)
            created_count += 1
            print(f"✅ Created: {template_data['name_zh']} ({template_data['slug']})")

        await db.commit()

        print("\n" + "="*60)
        print(f"🎉 Content Generation Templates Seeding Complete!")
        print(f"   Created: {created_count} templates")
        print(f"   Skipped: {skipped_count} templates (already exist)")
        print("="*60)


async def seed_translation_templates():
    """Create 2 translation workflow templates"""
    async with SessionLocal() as db:
        # 1. Get a user (templates need to be owned by someone)
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            print("❌ No user found. Please create a user first.")
            print("   You can run: cd ainav-backend && python seed_users.py")
            return

        print(f"✅ Using user: {user.username} ({user.email})")

        # Define translation templates
        templates = [
            {
                "name": "Multilingual Translator",
                "name_zh": "多语言翻译器",
                "slug": "multilingual-translator",
                "description": "Translate text between multiple languages with context awareness, tone preservation, and cultural adaptation.",
                "description_zh": "智能多语言翻译工具,支持上百种语言互译。具备上下文理解能力,保持原文语气和风格,自动进行文化适配。特别优化中英日韩等亚洲语言翻译质量。",
                "category": "translation",
                "use_case": "Content creators, international businesses, and travelers need accurate, context-aware translations across multiple languages",
                "usage_instructions_zh": """### 使用步骤

1. **选择语言对**:
   - 源语言(自动检测或手动选择)
   - 目标语言(支持100+语言)
   - 常用语言: 中文、英语、日语、韩语、西班牙语、法语、德语、俄语等

2. **输入待翻译文本**:
   - 支持单词、句子、段落、文章
   - 推荐长度: 10-5000字
   - 可输入专业术语表(可选)

3. **设置翻译选项**:
   - 翻译风格: 直译/意译/本地化
   - 语气保持: 正式/非正式/原文语气
   - 领域专业化: 通用/商务/技术/医疗/法律

4. **生成翻译**: 系统将输出:
   - 主要翻译结果
   - 2个替代译文(不同风格)
   - 关键术语对照表
   - 文化适配说明
   - 翻译质量评分

### 支持的语言对

**亚洲语言**: 中文(简体/繁体)、日语、韩语、泰语、越南语、印尼语、马来语等

**欧洲语言**: 英语、西班牙语、法语、德语、意大利语、葡萄牙语、俄语、波兰语等

**其他语言**: 阿拉伯语、希伯来语、土耳其语、印地语等

### 适用场景
- 网站/APP本地化
- 商务文档翻译
- 学术论文翻译
- 社交媒体内容
- 旅游沟通
- 合同协议翻译(建议人工复核)

### 翻译特色
- **上下文理解**: 根据上下文选择最合适的翻译
- **语气保持**: 保留原文的正式程度和情感色彩
- **文化适配**: 自动调整文化相关的表达方式
- **术语一致性**: 在文档中保持术语翻译的一致性

### 输出示例
每次翻译提供3个版本,让您选择最符合需求的译文,同时标注关键术语和文化差异点。""",
                "tags": ["translation", "multilingual", "localization", "i18n", "language"],
                "icon": "🌐",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个专业的多语言翻译专家,精通多种语言的细微差别和文化背景。你的翻译准确流畅,能够根据上下文选择最合适的表达方式,保持原文的语气和风格,同时进行必要的文化适配。",
                "temperature": 0.3,
                "is_public": True,
                "is_template": True,
                "star_count": 0,
                "fork_count": 0,
                "run_count": 0,
                "graph_json": {
                    "nodes": [
                        {
                            "id": "input-1",
                            "type": "input",
                            "position": {"x": 100, "y": 100},
                            "data": {
                                "label": "用户输入",
                                "fields": [
                                    {"name": "source_text", "type": "textarea", "label": "待翻译文本", "required": True},
                                    {"name": "source_lang", "type": "select", "label": "源语言", "options": ["自动检测", "中文", "英语", "日语", "韩语", "西班牙语", "法语", "德语", "俄语"], "default": "自动检测"},
                                    {"name": "target_lang", "type": "select", "label": "目标语言", "options": ["英语", "中文", "日语", "韩语", "西班牙语", "法语", "德语", "俄语"], "required": True},
                                    {"name": "style", "type": "select", "label": "翻译风格", "options": ["直译", "意译", "本地化"], "default": "意译"},
                                    {"name": "tone", "type": "select", "label": "语气", "options": ["保持原文", "正式", "非正式"], "default": "保持原文"},
                                    {"name": "domain", "type": "select", "label": "专业领域", "options": ["通用", "商务", "技术", "医疗", "法律", "文学"], "default": "通用"},
                                    {"name": "glossary", "type": "textarea", "label": "专业术语表(可选,格式: 源词=译词)", "required": False}
                                ]
                            }
                        },
                        {
                            "id": "llm-1",
                            "type": "llm",
                            "position": {"x": 400, "y": 100},
                            "data": {
                                "label": "分析源文本",
                                "prompt": "分析以下文本的特征:\n\n{{source_text}}\n\n请识别:\n1. 语言类型(如果设置为自动检测)\n2. 文本类型(正式/非正式、技术/通用等)\n3. 关键术语和专有名词\n4. 文化相关的表达\n5. 语气和情感色彩\n\n源语言设置: {{source_lang}}\n目标语言: {{target_lang}}\n专业领域: {{domain}}",
                                "model": "deepseek-chat",
                                "temperature": 0.2
                            }
                        },
                        {
                            "id": "llm-2",
                            "type": "llm",
                            "position": {"x": 700, "y": 50},
                            "data": {
                                "label": "主要翻译",
                                "prompt": "基于文本分析:\n{{llm-1.output}}\n\n将以下文本从{{source_lang}}翻译为{{target_lang}}:\n{{source_text}}\n\n翻译要求:\n- 风格: {{style}}\n- 语气: {{tone}}\n- 领域: {{domain}}\n- 术语表: {{glossary}}\n\n注意:\n1. 保持原文的段落结构\n2. 准确传达原文含义\n3. 使用目标语言的自然表达\n4. 保持专业术语的一致性\n5. 进行必要的文化适配",
                                "model": "deepseek-chat",
                                "temperature": 0.3
                            }
                        },
                        {
                            "id": "llm-3",
                            "type": "llm",
                            "position": {"x": 700, "y": 200},
                            "data": {
                                "label": "生成替代译文",
                                "prompt": "基于主要翻译:\n{{llm-2.output}}\n\n提供2个替代翻译版本:\n\n版本1: 更偏向{{style == '直译' ? '意译' : '直译'}}的风格\n版本2: 更{{tone == '正式' ? '口语化' : '正式'}}的表达\n\n每个版本都应:\n- 准确传达原文含义\n- 提供不同的表达角度\n- 标注与主译文的主要差异",
                                "model": "deepseek-chat",
                                "temperature": 0.5
                            }
                        },
                        {
                            "id": "llm-4",
                            "type": "llm",
                            "position": {"x": 1000, "y": 100},
                            "data": {
                                "label": "质量评估与补充",
                                "prompt": "对翻译结果进行质量评估:\n\n原文: {{source_text}}\n主译文: {{llm-2.output}}\n替代译文: {{llm-3.output}}\n\n请提供:\n\n1. **翻译质量评分** (0-10分):\n   - 准确性(是否忠实原文)\n   - 流畅性(目标语言是否自然)\n   - 完整性(是否遗漏信息)\n\n2. **关键术语对照表**:\n   - 列出重要术语的源语言-目标语言对照\n   - 标注术语选择的依据\n\n3. **文化适配说明**:\n   - 指出进行了文化适配的部分\n   - 解释适配的原因\n\n4. **改进建议**:\n   - 如果有更好的表达方式,请提出\n   - 标注可能存在歧义的部分",
                                "model": "deepseek-chat",
                                "temperature": 0.3
                            }
                        },
                        {
                            "id": "output-1",
                            "type": "output",
                            "position": {"x": 1300, "y": 100},
                            "data": {
                                "label": "翻译输出",
                                "format": "structured",
                                "fields": [
                                    {"name": "analysis", "source": "llm-1.output", "label": "文本分析"},
                                    {"name": "main_translation", "source": "llm-2.output", "label": "主要译文"},
                                    {"name": "alternative_translations", "source": "llm-3.output", "label": "替代译文"},
                                    {"name": "quality_assessment", "source": "llm-4.output", "label": "质量评估"}
                                ]
                            }
                        }
                    ],
                    "edges": [
                        {"id": "e1", "source": "input-1", "target": "llm-1", "type": "default"},
                        {"id": "e2", "source": "llm-1", "target": "llm-2", "type": "default"},
                        {"id": "e3", "source": "llm-2", "target": "llm-3", "type": "default"},
                        {"id": "e4", "source": "llm-2", "target": "llm-4", "type": "default"},
                        {"id": "e5", "source": "llm-3", "target": "llm-4", "type": "default"},
                        {"id": "e6", "source": "llm-4", "target": "output-1", "type": "default"}
                    ],
                    "viewport": {"x": 0, "y": 0, "zoom": 0.75}
                },
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "source_text": {"type": "string", "description": "待翻译的文本内容"},
                        "source_lang": {"type": "string", "enum": ["自动检测", "中文", "英语", "日语", "韩语", "西班牙语", "法语", "德语", "俄语"], "default": "自动检测"},
                        "target_lang": {"type": "string", "enum": ["英语", "中文", "日语", "韩语", "西班牙语", "法语", "德语", "俄语"]},
                        "style": {"type": "string", "enum": ["直译", "意译", "本地化"], "default": "意译"},
                        "tone": {"type": "string", "enum": ["保持原文", "正式", "非正式"], "default": "保持原文"},
                        "domain": {"type": "string", "enum": ["通用", "商务", "技术", "医疗", "法律", "文学"], "default": "通用"},
                        "glossary": {"type": "string", "description": "专业术语表(可选)"}
                    },
                    "required": ["source_text", "target_lang"]
                }
            },
            {
                "name": "Technical Document Translator",
                "name_zh": "技术文档翻译器",
                "slug": "technical-document-translator",
                "description": "Specialized translator for technical documentation, API docs, and developer content with terminology consistency and code preservation.",
                "description_zh": "专为技术文档设计的翻译工具,精确处理API文档、开发者指南、技术博客等内容。自动识别和保护代码块,保持技术术语一致性,支持Markdown格式。",
                "category": "translation",
                "use_case": "Developers and technical writers need accurate translation of documentation, tutorials, and technical content while preserving code and technical terms",
                "usage_instructions_zh": """### 使用步骤

1. **输入技术文档**:
   - 支持格式: Markdown, 纯文本, HTML
   - 内容类型: API文档, 教程, README, 技术博客, 发布说明
   - 可包含代码块、命令行、配置文件等

2. **选择语言方向**:
   - 常用: 英文→中文, 中文→英文
   - 支持: 日语、韩语等其他技术语言

3. **设置翻译参数**:
   - 文档类型: API文档/教程/README/技术博客
   - 术语处理: 保留原文/翻译/双语对照
   - 代码处理: 自动保护不翻译
   - 技术领域: 前端/后端/DevOps/数据科学/移动开发等

4. **生成译文**: 系统将输出:
   - 完整翻译文档(保持原格式)
   - 技术术语对照表
   - 代码示例(原样保留)
   - Markdown/HTML格式输出
   - 术语一致性检查报告

### 智能处理能力

**代码保护**:
- 自动识别代码块(```代码```)
- 保护行内代码(`代码`)
- 保护命令行指令
- 保护API端点和URL
- 保护变量名和函数名

**术语管理**:
- 内置技术术语库(10000+术语)
- 自动保持术语翻译一致性
- 支持自定义术语表
- 术语首次出现时提供双语对照

**格式保持**:
- 保持Markdown标题层级
- 保持列表和表格结构
- 保持链接和图片引用
- 保持代码注释格式

### 适用场景
- 开源项目文档本地化
- API参考文档翻译
- 技术教程翻译
- 产品技术文档
- 开发者博客
- SDK文档
- Release Notes翻译

### 技术领域覆盖
- **前端**: React, Vue, Angular, TypeScript等
- **后端**: Node.js, Python, Java, Go, Rust等
- **DevOps**: Docker, Kubernetes, CI/CD等
- **数据**: 数据库, 大数据, 机器学习等
- **移动**: iOS, Android, React Native等
- **云服务**: AWS, Azure, 阿里云等

### 输出格式
- Markdown格式(保持原文格式)
- 纯文本格式
- HTML格式(如果源文档是HTML)
- 术语对照表(JSON/Markdown)

### 质量保证
- 技术术语准确性验证
- 代码示例完整性检查
- 格式一致性检查
- 链接有效性保留

### 使用建议
- 较长文档建议分段翻译(每段2000-3000字)
- 提供术语表可显著提升翻译质量
- 翻译后建议技术人员review关键术语
- 定期更新自定义术语库以保持一致性""",
                "tags": ["technical-translation", "documentation", "api-docs", "developer-content", "markdown"],
                "icon": "📚",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个技术文档翻译专家,精通软件开发和多种编程语言。你能准确翻译技术文档,保持技术术语的一致性和准确性,保护代码块不被翻译,理解技术概念的上下文。你熟悉各种技术框架和工具,能够根据目标受众选择合适的术语翻译策略。",
                "temperature": 0.2,
                "is_public": True,
                "is_template": True,
                "star_count": 0,
                "fork_count": 0,
                "run_count": 0,
                "graph_json": {
                    "nodes": [
                        {
                            "id": "input-1",
                            "type": "input",
                            "position": {"x": 100, "y": 100},
                            "data": {
                                "label": "用户输入",
                                "fields": [
                                    {"name": "document_text", "type": "textarea", "label": "技术文档内容", "required": True, "placeholder": "支持Markdown格式,可包含代码块"},
                                    {"name": "source_lang", "type": "select", "label": "源语言", "options": ["英语", "中文", "日语"], "default": "英语"},
                                    {"name": "target_lang", "type": "select", "label": "目标语言", "options": ["中文", "英语", "日语"], "required": True},
                                    {"name": "doc_type", "type": "select", "label": "文档类型", "options": ["API文档", "教程", "README", "技术博客", "发布说明", "用户指南"], "default": "API文档"},
                                    {"name": "tech_domain", "type": "select", "label": "技术领域", "options": ["通用", "前端开发", "后端开发", "DevOps", "数据科学", "移动开发", "云计算"], "default": "通用"},
                                    {"name": "term_handling", "type": "select", "label": "术语处理", "options": ["保留原文", "翻译为目标语言", "双语对照"], "default": "双语对照"},
                                    {"name": "custom_glossary", "type": "textarea", "label": "自定义术语表(可选)", "required": False, "placeholder": "格式: API=应用程序接口\nendpoint=端点"}
                                ]
                            }
                        },
                        {
                            "id": "llm-1",
                            "type": "llm",
                            "position": {"x": 400, "y": 100},
                            "data": {
                                "label": "文档结构分析",
                                "prompt": "分析以下技术文档的结构和特征:\n\n{{document_text}}\n\n请识别:\n1. **内容结构**:\n   - 标题层级\n   - 代码块位置和语言\n   - 列表和表格\n   - 链接和图片引用\n\n2. **技术元素**:\n   - 编程语言和框架\n   - API端点和方法\n   - 配置项和参数\n   - 命令行指令\n\n3. **关键术语**:\n   - 核心技术术语列表\n   - 需要保持一致性的术语\n   - 行业标准术语\n\n4. **代码保护清单**:\n   - 需要保护的代码块\n   - 需要保护的行内代码\n   - 需要保护的命令和路径\n\n文档类型: {{doc_type}}\n技术领域: {{tech_domain}}",
                                "model": "deepseek-chat",
                                "temperature": 0.1
                            }
                        },
                        {
                            "id": "llm-2",
                            "type": "llm",
                            "position": {"x": 700, "y": 100},
                            "data": {
                                "label": "构建术语表",
                                "prompt": "基于文档分析:\n{{llm-1.output}}\n\n构建翻译术语表:\n\n1. **从内置术语库匹配**:\n   - {{tech_domain}}领域的标准术语\n   - 通用编程术语\n\n2. **处理自定义术语**:\n{{custom_glossary}}\n\n3. **术语翻译策略** ({{term_handling}}):\n   - 如果是\"保留原文\": 所有技术术语保持英文\n   - 如果是\"翻译为目标语言\": 提供准确的{{target_lang}}翻译\n   - 如果是\"双语对照\": 首次出现使用\"术语(Translation)\"格式\n\n4. **输出格式**:\n   源术语 | 目标术语 | 使用场景\n\n确保术语翻译:\n- 符合行业标准\n- 保持一致性\n- 准确传达技术概念",
                                "model": "deepseek-chat",
                                "temperature": 0.1
                            }
                        },
                        {
                            "id": "llm-3",
                            "type": "llm",
                            "position": {"x": 1000, "y": 100},
                            "data": {
                                "label": "翻译文档内容",
                                "prompt": "将以下技术文档从{{source_lang}}翻译为{{target_lang}}:\n\n{{document_text}}\n\n**翻译要求**:\n\n1. **严格遵守术语表**:\n{{llm-2.output}}\n\n2. **代码保护规则**:\n   - 代码块(```...```)内容完全保留,不翻译\n   - 行内代码(`...`)保留原文\n   - API端点、URL、路径保持不变\n   - 变量名、函数名、类名不翻译\n   - 命令行指令保持原样\n\n3. **格式保持**:\n   - 保持所有Markdown标记\n   - 保持标题层级(#, ##, ###)\n   - 保持列表格式(-, *, 1.)\n   - 保持表格结构\n   - 保持链接格式[text](url)\n\n4. **翻译风格**:\n   - 准确传达技术概念\n   - 使用{{target_lang}}技术文档的标准表达\n   - 保持清晰简洁\n   - 适合{{doc_type}}的语言风格\n\n5. **特别注意**:\n   - 代码注释可以翻译(但保持格式)\n   - 保持参数说明的准确性\n   - 错误信息通常保留原文\n   - 保持文档的逻辑结构\n\n输出完整的翻译后文档,保持原始格式。",
                                "model": "deepseek-chat",
                                "temperature": 0.2
                            }
                        },
                        {
                            "id": "llm-4",
                            "type": "llm",
                            "position": {"x": 1300, "y": 100},
                            "data": {
                                "label": "质量检查与优化",
                                "prompt": "对翻译结果进行质量检查:\n\n原文: {{document_text}}\n译文: {{llm-3.output}}\n术语表: {{llm-2.output}}\n\n**检查项目**:\n\n1. **术语一致性检查**:\n   - 验证所有术语翻译是否遵循术语表\n   - 检查同一术语在文档中的一致性\n   - 标注不一致的地方\n\n2. **代码完整性检查**:\n   - 验证所有代码块是否完整保留\n   - 检查代码块的语言标记是否保持\n   - 确认行内代码未被翻译\n\n3. **格式验证**:\n   - 检查Markdown格式是否正确\n   - 验证链接是否完整\n   - 确认标题层级是否保持\n\n4. **技术准确性**:\n   - 技术概念是否准确传达\n   - API描述是否清晰\n   - 参数说明是否准确\n\n5. **改进建议**:\n   - 标注可能存在歧义的翻译\n   - 提供更好的表达建议\n   - 指出需要人工审核的部分\n\n**输出**:\n- 质量评分(0-10)\n- 问题列表及修正建议\n- 最终优化后的译文(如有必要)",
                                "model": "deepseek-chat",
                                "temperature": 0.1
                            }
                        },
                        {
                            "id": "output-1",
                            "type": "output",
                            "position": {"x": 1600, "y": 100},
                            "data": {
                                "label": "翻译输出",
                                "format": "structured",
                                "fields": [
                                    {"name": "structure_analysis", "source": "llm-1.output", "label": "文档结构分析"},
                                    {"name": "glossary", "source": "llm-2.output", "label": "术语对照表"},
                                    {"name": "translated_document", "source": "llm-3.output", "label": "翻译后文档"},
                                    {"name": "quality_report", "source": "llm-4.output", "label": "质量检查报告"}
                                ]
                            }
                        }
                    ],
                    "edges": [
                        {"id": "e1", "source": "input-1", "target": "llm-1", "type": "default"},
                        {"id": "e2", "source": "llm-1", "target": "llm-2", "type": "default"},
                        {"id": "e3", "source": "llm-2", "target": "llm-3", "type": "default"},
                        {"id": "e4", "source": "llm-3", "target": "llm-4", "type": "default"},
                        {"id": "e5", "source": "llm-4", "target": "output-1", "type": "default"}
                    ],
                    "viewport": {"x": 0, "y": 0, "zoom": 0.7}
                },
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "document_text": {"type": "string", "description": "技术文档内容(支持Markdown)"},
                        "source_lang": {"type": "string", "enum": ["英语", "中文", "日语"], "default": "英语"},
                        "target_lang": {"type": "string", "enum": ["中文", "英语", "日语"]},
                        "doc_type": {"type": "string", "enum": ["API文档", "教程", "README", "技术博客", "发布说明", "用户指南"], "default": "API文档"},
                        "tech_domain": {"type": "string", "enum": ["通用", "前端开发", "后端开发", "DevOps", "数据科学", "移动开发", "云计算"], "default": "通用"},
                        "term_handling": {"type": "string", "enum": ["保留原文", "翻译为目标语言", "双语对照"], "default": "双语对照"},
                        "custom_glossary": {"type": "string", "description": "自定义术语表(可选)"}
                    },
                    "required": ["document_text", "target_lang"]
                }
            }
        ]

        # Insert templates into database
        created_count = 0
        skipped_count = 0

        for template_data in templates:
            # Check if template already exists
            existing = await db.execute(
                select(AgentWorkflow).where(AgentWorkflow.slug == template_data["slug"])
            )
            if existing.scalar_one_or_none():
                print(f"⏭️  Skipped: {template_data['name_zh']} (already exists)")
                skipped_count += 1
                continue

            # Create template
            template = AgentWorkflow(
                id=uuid.uuid4(),
                user_id=user.id,
                **template_data
            )
            db.add(template)
            created_count += 1
            print(f"✅ Created: {template_data['name_zh']} ({template_data['slug']})")

        await db.commit()

        print("\n" + "="*60)
        print(f"🎉 Translation Templates Seeding Complete!")
        print(f"   Created: {created_count} templates")
        print(f"   Skipped: {skipped_count} templates (already exist)")
        print("="*60)


async def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("📝 Seeding Workflow Templates")
    print("="*60 + "\n")

    await seed_content_generation_templates()
    await seed_translation_templates()

    print("\n✨ All done!\n")


if __name__ == "__main__":
    asyncio.run(main())
