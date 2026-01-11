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


async def seed_summarization_templates():
    """Create 3 summarization workflow templates"""
    async with SessionLocal() as db:
        # 1. Get a user (templates need to be owned by someone)
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            print("❌ No user found. Please create a user first.")
            print("   You can run: cd ainav-backend && python seed_users.py")
            return

        print(f"✅ Using user: {user.username} ({user.email})")

        # Define summarization templates
        templates = [
            {
                "name": "Article Summarizer",
                "name_zh": "文章摘要生成器",
                "slug": "article-summarizer",
                "description": "Generate concise, accurate summaries of long-form articles, blog posts, and news pieces with key points extraction.",
                "description_zh": "智能提取长文章的核心要点,生成简洁准确的摘要。支持多种摘要长度,自动提取关键信息、主要观点和重要数据,适合快速阅读和信息获取。",
                "category": "summarization",
                "use_case": "Professionals, researchers, and content curators need to quickly grasp the essence of long articles without reading the entire text",
                "usage_instructions_zh": """### 使用步骤

1. **输入文章内容**:
   - 复制粘贴完整文章文本
   - 支持新闻报道、博客文章、专栏评论等
   - 推荐长度: 500-10000字

2. **选择摘要类型**:
   - 极简摘要(1-2句话,50-100字)
   - 标准摘要(1段,150-300字)
   - 详细摘要(多段,300-500字)

3. **设置摘要重点**:
   - 全面概括(平衡覆盖所有要点)
   - 观点提取(聚焦作者观点和论据)
   - 事实总结(聚焦事件、数据、事实)
   - 行动建议(提取实用建议和方法)

4. **生成摘要**: 系统将输出:
   - 核心摘要(按选定长度)
   - 3-5个关键要点(bullet points)
   - 重要数据和引用
   - 文章主题标签
   - 相关问题建议(延伸阅读)

### 适用场景
- 新闻快速浏览
- 行业资讯跟踪
- 竞品分析报告
- 学习资料整理
- 内容策划研究
- 会议前准备阅读

### 摘要特点
- **准确性**: 忠实原文,不添加原文没有的信息
- **完整性**: 覆盖文章的主要观点和论据
- **简洁性**: 去除冗余,保留核心信息
- **可读性**: 流畅连贯,独立成文

### 输出示例
每次生成包含三个部分:核心摘要、关键要点列表、延伸阅读建议。可直接用于分享、笔记或二次创作。

### 使用建议
- 新闻类文章建议使用"事实总结"模式
- 观点评论类使用"观点提取"模式
- 教程指南类使用"行动建议"模式
- 研究报告类使用"全面概括"模式""",
                "tags": ["summarization", "reading", "content-analysis", "key-points", "productivity"],
                "icon": "📄",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个专业的文章摘要专家,擅长快速抓住文章核心要点,用简洁清晰的语言概括长篇内容。你的摘要准确、全面、易读,能够帮助读者快速理解文章精髓。",
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
                                    {"name": "article_text", "type": "textarea", "label": "文章内容", "required": True, "placeholder": "粘贴完整文章文本..."},
                                    {"name": "summary_length", "type": "select", "label": "摘要长度", "options": ["极简摘要(50-100字)", "标准摘要(150-300字)", "详细摘要(300-500字)"], "default": "标准摘要(150-300字)"},
                                    {"name": "focus_type", "type": "select", "label": "摘要重点", "options": ["全面概括", "观点提取", "事实总结", "行动建议"], "default": "全面概括"},
                                    {"name": "target_audience", "type": "select", "label": "目标读者", "options": ["通用读者", "专业人士", "决策者", "学生"], "default": "通用读者"}
                                ]
                            }
                        },
                        {
                            "id": "llm-1",
                            "type": "llm",
                            "position": {"x": 400, "y": 100},
                            "data": {
                                "label": "分析文章结构",
                                "prompt": "分析以下文章的结构和核心内容:\n\n{{article_text}}\n\n请识别:\n1. 文章类型(新闻/评论/教程/研究等)\n2. 主题和中心思想\n3. 主要观点和论据(3-5个)\n4. 重要数据、引用、案例\n5. 文章的逻辑结构\n\n摘要重点: {{focus_type}}\n目标读者: {{target_audience}}",
                                "model": "deepseek-chat",
                                "temperature": 0.2
                            }
                        },
                        {
                            "id": "llm-2",
                            "type": "llm",
                            "position": {"x": 700, "y": 100},
                            "data": {
                                "label": "生成核心摘要",
                                "prompt": "基于文章分析:\n{{llm-1.output}}\n\n为以下文章生成{{summary_length}}:\n{{article_text}}\n\n要求:\n1. **摘要重点**: {{focus_type}}\n   - 全面概括: 平衡覆盖所有主要观点\n   - 观点提取: 重点提炼作者的核心观点和论据\n   - 事实总结: 聚焦事件经过、数据、客观事实\n   - 行动建议: 提取实用方法、步骤、建议\n\n2. **摘要原则**:\n   - 忠实原文,不添加原文没有的信息\n   - 使用简洁清晰的语言\n   - 保持逻辑连贯\n   - 适合{{target_audience}}\n\n3. **字数控制**:\n   - 极简摘要: 1-2句话,50-100字\n   - 标准摘要: 1段,150-300字\n   - 详细摘要: 2-3段,300-500字\n\n直接输出摘要内容,不要添加标题或说明。",
                                "model": "deepseek-chat",
                                "temperature": 0.3
                            }
                        },
                        {
                            "id": "llm-3",
                            "type": "llm",
                            "position": {"x": 1000, "y": 100},
                            "data": {
                                "label": "提取关键要点",
                                "prompt": "基于文章:\n{{article_text}}\n\n和摘要:\n{{llm-2.output}}\n\n提取并输出:\n\n**关键要点** (3-5个bullet points):\n- 每个要点一句话\n- 覆盖文章的主要观点\n- 按重要性排序\n\n**重要信息**:\n- 关键数据和统计\n- 重要引用或观点\n- 核心案例或例子\n\n**主题标签** (3-5个):\n- 文章涉及的主要话题\n- 便于分类和检索\n\n使用清晰的格式输出,便于阅读。",
                                "model": "deepseek-chat",
                                "temperature": 0.3
                            }
                        },
                        {
                            "id": "llm-4",
                            "type": "llm",
                            "position": {"x": 1300, "y": 100},
                            "data": {
                                "label": "生成延伸建议",
                                "prompt": "基于文章主题和内容:\n{{llm-1.output}}\n\n提供延伸阅读建议:\n\n1. **相关问题**(3-4个):\n   - 这篇文章引发的深入思考问题\n   - 帮助读者进一步理解主题\n\n2. **进一步探索方向**:\n   - 可以深入研究的相关主题\n   - 推荐的延伸阅读方向\n\n3. **实践应用**(如适用):\n   - 如何将文章内容应用到实际工作/生活\n   - 具体的行动建议\n\n针对{{target_audience}}提供建议。",
                                "model": "deepseek-chat",
                                "temperature": 0.5
                            }
                        },
                        {
                            "id": "output-1",
                            "type": "output",
                            "position": {"x": 1600, "y": 100},
                            "data": {
                                "label": "摘要输出",
                                "format": "structured",
                                "fields": [
                                    {"name": "summary", "source": "llm-2.output", "label": "核心摘要"},
                                    {"name": "key_points", "source": "llm-3.output", "label": "关键要点"},
                                    {"name": "suggestions", "source": "llm-4.output", "label": "延伸建议"}
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
                    "viewport": {"x": 0, "y": 0, "zoom": 0.75}
                },
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "article_text": {"type": "string", "description": "文章完整内容"},
                        "summary_length": {"type": "string", "enum": ["极简摘要(50-100字)", "标准摘要(150-300字)", "详细摘要(300-500字)"], "default": "标准摘要(150-300字)"},
                        "focus_type": {"type": "string", "enum": ["全面概括", "观点提取", "事实总结", "行动建议"], "default": "全面概括"},
                        "target_audience": {"type": "string", "enum": ["通用读者", "专业人士", "决策者", "学生"], "default": "通用读者"}
                    },
                    "required": ["article_text"]
                }
            },
            {
                "name": "Meeting Notes Summarizer",
                "name_zh": "会议纪要生成器",
                "slug": "meeting-notes-summarizer",
                "description": "Transform meeting transcripts and notes into structured summaries with action items, decisions, and key discussion points.",
                "description_zh": "将会议记录或录音转写文本整理成结构化的会议纪要。自动提取讨论要点、决策事项、行动计划和待办任务,支持多种会议类型和输出格式。",
                "category": "summarization",
                "use_case": "Teams and professionals need to convert lengthy meeting discussions into clear, actionable summaries with tasks and decisions",
                "usage_instructions_zh": """### 使用步骤

1. **输入会议内容**:
   - 粘贴会议记录/转写文本
   - 或输入会议核心内容
   - 支持中英文混合
   - 可包含时间戳和发言人标记

2. **会议信息** (可选):
   - 会议主题
   - 会议类型(项目会、周会、决策会、头脑风暴等)
   - 参会人员
   - 会议日期

3. **选择输出格式**:
   - 标准纪要(适合内部分享)
   - 简洁版(适合快速回顾)
   - 详细版(含完整讨论过程)
   - 执行清单(聚焦行动项)

4. **生成纪要**: 系统将输出:
   - 会议概要(1段总结)
   - 讨论要点(分主题整理)
   - 决策事项(明确的决定)
   - 行动计划(任务、责任人、截止日期)
   - 待解决问题
   - 下次会议议程建议

### 会议类型支持

**项目会议**:
- 项目进度更新
- 问题和风险讨论
- 资源需求
- 下一步计划

**决策会议**:
- 背景和问题陈述
- 讨论的选项
- 最终决策和理由
- 执行计划

**头脑风暴**:
- 问题定义
- 提出的想法(分类整理)
- 有价值的方向
- 后续行动

**周例会/站会**:
- 上周完成
- 本周计划
- 阻碍和需要帮助
- 团队公告

### 适用场景
- 项目管理会议
- 团队周会/站会
- 客户沟通会议
- 战略规划会议
- 问题解决会议
- 培训分享会

### 输出特点
- **结构化**: 清晰的章节和层次
- **可执行**: 明确的行动项和责任人
- **易检索**: 关键信息突出标记
- **可追踪**: 便于后续跟进

### 行动计划格式
每个行动项包含:
- [ ] 任务描述
- 负责人: @姓名
- 截止日期: YYYY-MM-DD
- 优先级: 高/中/低

### 使用建议
- 会议录音可先用语音转文字工具转写
- 输入时保留发言人标记可获得更好效果
- 会议结束后及时整理,记忆更清晰
- 生成的纪要建议发送给参会人员确认""",
                "tags": ["meeting", "notes", "productivity", "collaboration", "action-items"],
                "icon": "📋",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个专业的会议纪要整理专家,擅长从会议记录中提取关键信息,整理成结构化的会议纪要。你能准确识别决策、行动项和重要讨论点,帮助团队高效跟进会议成果。",
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
                                    {"name": "meeting_content", "type": "textarea", "label": "会议记录/转写文本", "required": True, "placeholder": "粘贴会议内容,可包含发言人和时间戳..."},
                                    {"name": "meeting_title", "type": "text", "label": "会议主题", "required": False, "placeholder": "例: 产品规划会议"},
                                    {"name": "meeting_type", "type": "select", "label": "会议类型", "options": ["项目会议", "周例会/站会", "决策会议", "头脑风暴", "客户沟通", "其他"], "default": "项目会议"},
                                    {"name": "participants", "type": "text", "label": "参会人员", "required": False, "placeholder": "张三、李四、王五"},
                                    {"name": "output_format", "type": "select", "label": "输出格式", "options": ["标准纪要", "简洁版", "详细版", "执行清单"], "default": "标准纪要"}
                                ]
                            }
                        },
                        {
                            "id": "llm-1",
                            "type": "llm",
                            "position": {"x": 400, "y": 100},
                            "data": {
                                "label": "分析会议内容",
                                "prompt": "分析以下会议记录:\n\n{{meeting_content}}\n\n会议信息:\n- 主题: {{meeting_title}}\n- 类型: {{meeting_type}}\n- 参会人: {{participants}}\n\n请识别和提取:\n\n1. **会议目标和背景**:\n   - 会议召开的目的\n   - 讨论的背景和上下文\n\n2. **主要讨论主题**:\n   - 列出会议涉及的主要话题\n   - 按重要性和讨论时长排序\n\n3. **关键信息类型**:\n   - 信息分享(汇报、更新)\n   - 讨论观点(不同意见、建议)\n   - 明确决策(已确定的事项)\n   - 行动任务(需要执行的工作)\n   - 问题和风险(待解决的问题)\n\n4. **发言人和角色**(如果有标记):\n   - 主持人\n   - 主要发言人\n   - 决策者\n\n为后续结构化整理做准备。",
                                "model": "deepseek-chat",
                                "temperature": 0.2
                            }
                        },
                        {
                            "id": "llm-2",
                            "type": "llm",
                            "position": {"x": 700, "y": 50},
                            "data": {
                                "label": "提取决策和行动项",
                                "prompt": "基于会议分析:\n{{llm-1.output}}\n\n从会议内容中提取:\n{{meeting_content}}\n\n**1. 明确决策事项**:\n列出会议中达成的所有决策,格式:\n- 决策内容\n- 决策理由(如果有讨论)\n- 决策者(如果明确)\n\n**2. 行动计划**:\n提取所有行动项,每项包含:\n- [ ] 任务描述(清晰、可执行)\n- 负责人: @姓名 (如果会议中提到)\n- 截止日期: YYYY-MM-DD (如果会议中提到,否则标记\"待定\")\n- 优先级: 高/中/低 (根据讨论紧迫程度判断)\n- 依赖关系: (如果有前置任务)\n\n**3. 待解决问题**:\n列出提出但未解决的问题:\n- 问题描述\n- 为什么未解决\n- 建议的解决路径\n\n确保每个行动项都清晰、可执行、可追踪。",
                                "model": "deepseek-chat",
                                "temperature": 0.2
                            }
                        },
                        {
                            "id": "llm-3",
                            "type": "llm",
                            "position": {"x": 700, "y": 250},
                            "data": {
                                "label": "整理讨论要点",
                                "prompt": "基于会议分析:\n{{llm-1.output}}\n\n整理会议讨论要点:\n{{meeting_content}}\n\n按主题组织讨论内容:\n\n**主题1: [主题名称]**\n- 讨论要点1\n- 讨论要点2\n- 关键观点和建议\n- 数据和事实支持\n\n**主题2: [主题名称]**\n...\n\n要求:\n1. 按{{meeting_type}}的特点组织内容\n2. 保留重要的讨论细节\n3. 突出不同观点和建议\n4. 简洁清晰,去除冗余\n5. 保持逻辑连贯\n\n如果是头脑风暴类会议,按想法类别整理;\n如果是项目会议,按项目模块或议题整理;\n如果是决策会议,按讨论的选项整理。",
                                "model": "deepseek-chat",
                                "temperature": 0.3
                            }
                        },
                        {
                            "id": "llm-4",
                            "type": "llm",
                            "position": {"x": 1000, "y": 150},
                            "data": {
                                "label": "生成会议纪要",
                                "prompt": "整合以下信息,生成{{output_format}}的会议纪要:\n\n**会议信息**:\n- 主题: {{meeting_title}}\n- 类型: {{meeting_type}}\n- 参会人: {{participants}}\n\n**会议分析**:\n{{llm-1.output}}\n\n**决策和行动项**:\n{{llm-2.output}}\n\n**讨论要点**:\n{{llm-3.output}}\n\n根据{{output_format}}生成相应格式:\n\n**标准纪要**包含:\n```\n# 会议纪要: [主题]\n\n## 基本信息\n- 时间: [日期]\n- 参会人: [人员]\n- 会议类型: [类型]\n\n## 会议概要\n[1-2段总结会议目的和主要成果]\n\n## 讨论要点\n[按主题整理的讨论内容]\n\n## 决策事项\n[明确的决策列表]\n\n## 行动计划\n[任务清单,含责任人和截止日期]\n\n## 待解决问题\n[未解决的问题]\n\n## 下次会议\n[建议的议程或跟进事项]\n```\n\n**简洁版**包含:\n- 会议概要(1段)\n- 关键决策(3-5条)\n- 行动计划(清单)\n\n**详细版**包含:\n- 完整的讨论过程\n- 不同观点和建议\n- 详细的决策理由\n- 完整行动计划\n\n**执行清单**聚焦:\n- 行动任务清单\n- 责任人分配\n- 时间节点\n- 优先级排序\n\n使用清晰的Markdown格式,便于阅读和分享。",
                                "model": "deepseek-chat",
                                "temperature": 0.2
                            }
                        },
                        {
                            "id": "output-1",
                            "type": "output",
                            "position": {"x": 1300, "y": 150},
                            "data": {
                                "label": "纪要输出",
                                "format": "markdown",
                                "fields": [
                                    {"name": "meeting_minutes", "source": "llm-4.output", "label": "会议纪要"}
                                ]
                            }
                        }
                    ],
                    "edges": [
                        {"id": "e1", "source": "input-1", "target": "llm-1", "type": "default"},
                        {"id": "e2", "source": "llm-1", "target": "llm-2", "type": "default"},
                        {"id": "e3", "source": "llm-1", "target": "llm-3", "type": "default"},
                        {"id": "e4", "source": "llm-2", "target": "llm-4", "type": "default"},
                        {"id": "e5", "source": "llm-3", "target": "llm-4", "type": "default"},
                        {"id": "e6", "source": "llm-4", "target": "output-1", "type": "default"}
                    ],
                    "viewport": {"x": 0, "y": 0, "zoom": 0.75}
                },
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "meeting_content": {"type": "string", "description": "会议记录或转写文本"},
                        "meeting_title": {"type": "string", "description": "会议主题"},
                        "meeting_type": {"type": "string", "enum": ["项目会议", "周例会/站会", "决策会议", "头脑风暴", "客户沟通", "其他"], "default": "项目会议"},
                        "participants": {"type": "string", "description": "参会人员"},
                        "output_format": {"type": "string", "enum": ["标准纪要", "简洁版", "详细版", "执行清单"], "default": "标准纪要"}
                    },
                    "required": ["meeting_content"]
                }
            },
            {
                "name": "Research Paper Digest",
                "name_zh": "学术论文摘要器",
                "slug": "research-paper-digest",
                "description": "Create structured summaries of academic papers with methodology, findings, and significance analysis for researchers and students.",
                "description_zh": "为学术论文生成结构化摘要,提取研究问题、方法、发现和意义。适合科研人员快速了解论文核心内容,支持中英文论文,自动识别论文结构。",
                "category": "summarization",
                "use_case": "Researchers, students, and academics need to quickly understand academic papers without reading the entire text",
                "usage_instructions_zh": """### 使用步骤

1. **输入论文内容**:
   - 复制粘贴论文全文或主要部分
   - 至少包含: 摘要、方法、结果、讨论
   - 支持中文和英文论文
   - 建议长度: 2000-20000字

2. **选择学科领域**:
   - 计算机科学
   - 生物医学
   - 物理学
   - 化学
   - 经济学
   - 社会科学
   - 工程技术
   - 其他

3. **设置摘要深度**:
   - 快速浏览(5分钟阅读)
   - 标准摘要(10分钟阅读)
   - 深度分析(20分钟阅读)

4. **生成摘要**: 系统将输出:
   - 一句话总结
   - 研究背景和动机
   - 研究问题/假设
   - 研究方法
   - 主要发现
   - 研究意义和贡献
   - 局限性和未来工作
   - 关键引用和相关工作

### 适用场景
- 文献综述准备
- 科研选题调研
- 论文快速筛选
- 学术报告准备
- 跨学科学习
- 论文阅读笔记
- 研究方向探索

### 论文结构识别

自动识别论文标准章节:
- **Abstract**: 论文摘要
- **Introduction**: 研究背景和问题
- **Related Work**: 相关研究
- **Methodology**: 研究方法
- **Results**: 实验结果
- **Discussion**: 结果讨论
- **Conclusion**: 结论和展望
- **References**: 参考文献

### 输出特点

**结构化**:
- 按学术论文逻辑组织
- 清晰的章节划分
- 便于快速定位信息

**准确性**:
- 保留关键数据和指标
- 准确传达研究方法
- 忠实原文结论

**批判性**:
- 分析研究的优势
- 指出可能的局限性
- 评估研究贡献

**可读性**:
- 简化专业术语(适度)
- 清晰的逻辑表达
- 适合{{摘要深度}}

### 摘要模板

**快速浏览版**:
- 研究问题(1句话)
- 方法(1-2句)
- 主要发现(2-3句)
- 意义(1句)

**标准摘要版**:
- 背景和动机(1段)
- 研究问题(明确陈述)
- 方法概述(1段)
- 主要结果(带关键数据)
- 贡献和意义(1段)

**深度分析版**:
- 详细背景(2-3段)
- 研究问题和假设
- 方法详解(包括实验设计)
- 详细结果(含图表说明)
- 深入讨论
- 批判性分析
- 应用价值

### 使用建议
- 输入论文越完整,摘要质量越高
- PDF需先转换为文本格式
- 数学公式密集的论文建议保留公式图片
- 可以只输入核心章节(方法+结果+讨论)
- 生成摘要后建议结合原文关键部分阅读

### 学科特定优化

不同学科关注重点不同:
- **理工科**: 实验设计、数据分析、性能指标
- **医学**: 临床意义、样本量、统计显著性
- **社科**: 理论框架、研究方法、实证证据
- **计算机**: 算法创新、实验对比、开源代码""",
                "tags": ["research", "academic", "papers", "literature-review", "education"],
                "icon": "🔬",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个学术研究专家,擅长阅读和分析学术论文。你能快速抓住论文的核心贡献,准确提取研究方法和发现,批判性地评估研究意义和局限性。你的摘要帮助研究者和学生高效理解学术文献。",
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
                            "position": {"x": 100, "y": 150},
                            "data": {
                                "label": "用户输入",
                                "fields": [
                                    {"name": "paper_text", "type": "textarea", "label": "论文内容", "required": True, "placeholder": "粘贴论文全文或主要章节(摘要、方法、结果、讨论)..."},
                                    {"name": "paper_title", "type": "text", "label": "论文标题", "required": False},
                                    {"name": "research_field", "type": "select", "label": "学科领域", "options": ["计算机科学", "生物医学", "物理学", "化学", "经济学", "社会科学", "工程技术", "其他"], "default": "计算机科学"},
                                    {"name": "summary_depth", "type": "select", "label": "摘要深度", "options": ["快速浏览(5分钟)", "标准摘要(10分钟)", "深度分析(20分钟)"], "default": "标准摘要(10分钟)"},
                                    {"name": "language", "type": "select", "label": "论文语言", "options": ["中文", "英文", "其他"], "default": "英文"}
                                ]
                            }
                        },
                        {
                            "id": "llm-1",
                            "type": "llm",
                            "position": {"x": 400, "y": 150},
                            "data": {
                                "label": "论文结构分析",
                                "prompt": "分析以下学术论文的结构和内容:\n\n{{paper_text}}\n\n论文信息:\n- 标题: {{paper_title}}\n- 学科: {{research_field}}\n- 语言: {{language}}\n\n请识别和提取:\n\n1. **论文基本信息**:\n   - 论文类型(实证研究/理论分析/综述/方法论等)\n   - 研究范式(定量/定性/混合)\n   - 如果有,提取作者、机构、发表时间\n\n2. **论文结构识别**:\n   - 哪些标准章节存在(Abstract, Introduction, Method, Results, Discussion, Conclusion)\n   - 章节的主要内容概览\n\n3. **核心学术元素**:\n   - 研究背景和动机\n   - 研究问题或假设\n   - 理论框架(如果有)\n   - 研究方法概述\n   - 主要发现和结论\n   - 研究贡献\n\n4. **关键细节**:\n   - 重要数据、统计结果、性能指标\n   - 实验设置、样本量、数据集\n   - 关键图表的说明\n   - 重要的相关研究引用\n\n基于{{research_field}}的特点进行分析。",
                                "model": "deepseek-chat",
                                "temperature": 0.1
                            }
                        },
                        {
                            "id": "llm-2",
                            "type": "llm",
                            "position": {"x": 700, "y": 50},
                            "data": {
                                "label": "提取研究问题和方法",
                                "prompt": "基于论文分析:\n{{llm-1.output}}\n\n从论文中提取:\n{{paper_text}}\n\n**一、研究背景和动机**:\n- 研究领域的现状和问题\n- 为什么这个研究重要\n- 前人工作的不足(Research Gap)\n\n**二、研究问题/假设**:\n- 明确陈述研究要解决的问题\n- 或提出的研究假设\n- 研究目标\n\n**三、研究方法**:\n根据{{research_field}}的特点,详细描述:\n- 研究设计(实验/调查/分析等)\n- 数据来源(数据集/样本/实验对象)\n- 方法和技术(算法/模型/分析工具)\n- 实验设置和参数\n- 评估指标和基准\n\n**四、理论框架**(如果有):\n- 采用的理论基础\n- 概念模型\n\n使用清晰的结构化格式,保留关键技术细节。",
                                "model": "deepseek-chat",
                                "temperature": 0.2
                            }
                        },
                        {
                            "id": "llm-3",
                            "type": "llm",
                            "position": {"x": 700, "y": 250},
                            "data": {
                                "label": "提取研究发现和意义",
                                "prompt": "基于论文分析:\n{{llm-1.output}}\n\n从论文中提取:\n{{paper_text}}\n\n**一、主要研究发现**:\n列出论文的核心发现:\n- 发现1: [描述] (包含关键数据/指标)\n- 发现2: [描述]\n- ...\n\n重点提取:\n- 定量结果(数值、百分比、p值等)\n- 定性发现(观察、模式、关系)\n- 与基准或前人工作的对比\n- 统计显著性(如果有)\n\n**二、结果解释和讨论**:\n- 结果的含义和解释\n- 结果支持或反驳了什么\n- 意外发现(如果有)\n\n**三、研究贡献和意义**:\n- 理论贡献(对学术领域的贡献)\n- 实践意义(应用价值)\n- 方法论贡献(如果有新方法)\n\n**四、局限性和未来工作**:\n- 研究的局限性\n- 未来研究方向\n- 尚未解决的问题\n\n基于{{research_field}}的评估标准,客观全面地总结。",
                                "model": "deepseek-chat",
                                "temperature": 0.2
                            }
                        },
                        {
                            "id": "llm-4",
                            "type": "llm",
                            "position": {"x": 1000, "y": 150},
                            "data": {
                                "label": "生成结构化摘要",
                                "prompt": "整合以下信息,生成{{summary_depth}}的学术论文摘要:\n\n**论文信息**:\n- 标题: {{paper_title}}\n- 学科: {{research_field}}\n\n**结构分析**:\n{{llm-1.output}}\n\n**研究问题和方法**:\n{{llm-2.output}}\n\n**研究发现和意义**:\n{{llm-3.output}}\n\n根据{{summary_depth}}生成相应深度的摘要:\n\n**快速浏览(5分钟)** 包含:\n```\n# 论文快速摘要: [标题]\n\n## 一句话总结\n[用一句话概括这篇论文]\n\n## 研究问题\n[1-2句]\n\n## 方法\n[1-2句]\n\n## 主要发现\n- [发现1]\n- [发现2]\n- [发现3]\n\n## 研究意义\n[1-2句]\n```\n\n**标准摘要(10分钟)** 包含:\n```\n# 论文摘要: [标题]\n\n## 研究背景\n[1-2段]\n\n## 研究问题\n[明确陈述]\n\n## 研究方法\n[方法概述,1段]\n\n## 主要发现\n[详细列出,包含关键数据]\n\n## 研究贡献\n[理论+实践意义,1-2段]\n\n## 局限性\n[简要说明]\n```\n\n**深度分析(20分钟)** 包含:\n```\n# 论文深度分析: [标题]\n\n## 研究背景和动机\n[详细背景,2-3段]\n\n## 研究问题和假设\n[明确陈述,包含理论框架]\n\n## 文献综述要点\n[相关研究,Research Gap]\n\n## 研究方法详解\n[详细方法描述,包括实验设计、数据、技术]\n\n## 研究发现详述\n[详细结果,含图表说明,数据分析]\n\n## 结果讨论\n[深入讨论,与前人研究对比]\n\n## 研究贡献和意义\n[理论+方法+实践,多维度分析]\n\n## 批判性分析\n[优势、局限性、可改进之处]\n\n## 未来研究方向\n[建议的后续研究]\n\n## 关键引用\n[重要的相关研究]\n```\n\n使用清晰的Markdown格式,学术性强但易于理解。\n根据{{research_field}}调整专业术语的使用程度。",
                                "model": "deepseek-chat",
                                "temperature": 0.2
                            }
                        },
                        {
                            "id": "llm-5",
                            "type": "llm",
                            "position": {"x": 1300, "y": 150},
                            "data": {
                                "label": "生成阅读建议",
                                "prompt": "基于论文摘要和分析,提供阅读建议:\n\n**论文**: {{paper_title}}\n**学科**: {{research_field}}\n\n**摘要**:\n{{llm-4.output}}\n\n请提供:\n\n**1. 阅读价值评估**:\n- 这篇论文适合谁读?\n- 阅读优先级建议(高/中/低)\n- 为什么值得/不值得深入阅读?\n\n**2. 关键章节推荐**:\n- 如果时间有限,应重点阅读哪些章节?\n- 哪些图表最关键?\n\n**3. 延伸阅读**:\n- 基于这篇论文,建议阅读的相关主题\n- 推荐的前置阅读(基础知识)\n- 推荐的后续阅读(深入研究)\n\n**4. 应用思考**:\n- 这个研究可以应用到哪些场景?\n- 如何借鉴这个研究的方法?\n- 有哪些可以进一步探索的研究问题?\n\n**5. 批判性思考问题** (3-4个):\n- 引导深入思考论文的问题\n- 帮助评估研究质量的问题\n\n针对{{摘要深度}}和{{research_field}}提供建议。",
                                "model": "deepseek-chat",
                                "temperature": 0.4
                            }
                        },
                        {
                            "id": "output-1",
                            "type": "output",
                            "position": {"x": 1600, "y": 150},
                            "data": {
                                "label": "摘要输出",
                                "format": "structured",
                                "fields": [
                                    {"name": "paper_summary", "source": "llm-4.output", "label": "论文摘要"},
                                    {"name": "reading_guide", "source": "llm-5.output", "label": "阅读建议"}
                                ]
                            }
                        }
                    ],
                    "edges": [
                        {"id": "e1", "source": "input-1", "target": "llm-1", "type": "default"},
                        {"id": "e2", "source": "llm-1", "target": "llm-2", "type": "default"},
                        {"id": "e3", "source": "llm-1", "target": "llm-3", "type": "default"},
                        {"id": "e4", "source": "llm-2", "target": "llm-4", "type": "default"},
                        {"id": "e5", "source": "llm-3", "target": "llm-4", "type": "default"},
                        {"id": "e6", "source": "llm-4", "target": "llm-5", "type": "default"},
                        {"id": "e7", "source": "llm-5", "target": "output-1", "type": "default"}
                    ],
                    "viewport": {"x": 0, "y": 0, "zoom": 0.7}
                },
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "paper_text": {"type": "string", "description": "论文全文或主要章节内容"},
                        "paper_title": {"type": "string", "description": "论文标题"},
                        "research_field": {"type": "string", "enum": ["计算机科学", "生物医学", "物理学", "化学", "经济学", "社会科学", "工程技术", "其他"], "default": "计算机科学"},
                        "summary_depth": {"type": "string", "enum": ["快速浏览(5分钟)", "标准摘要(10分钟)", "深度分析(20分钟)"], "default": "标准摘要(10分钟)"},
                        "language": {"type": "string", "enum": ["中文", "英文", "其他"], "default": "英文"}
                    },
                    "required": ["paper_text"]
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
        print(f"🎉 Summarization Templates Seeding Complete!")
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
    await seed_summarization_templates()

    print("\n✨ All done!\n")


if __name__ == "__main__":
    asyncio.run(main())
