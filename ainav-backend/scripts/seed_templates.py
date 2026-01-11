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


async def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("📝 Seeding Content Generation Templates")
    print("="*60 + "\n")

    await seed_content_generation_templates()

    print("\n✨ All done!\n")


if __name__ == "__main__":
    asyncio.run(main())
