# Template Seed Scripts

This directory contains scripts to seed workflow templates into the database.

## Content Generation Templates

### Usage

```bash
cd ainav-backend
python scripts/seed_templates.py
```

### Prerequisites

1. Database must be running and migrations applied
2. At least one user must exist in the database
3. Environment variables configured in `.env`

### Templates Included

The `seed_templates.py` script creates the following content generation templates:

1. **Blog Article Generator (博客文章生成器)**
   - Category: content-generation
   - Generates SEO-optimized blog articles with outlines and metadata
   - Supports multiple writing styles and word count customization

2. **Social Media Post Creator (社交媒体文案生成器)**
   - Category: content-generation
   - Creates platform-specific posts for WeChat, Weibo, Xiaohongshu, Twitter, LinkedIn
   - Includes hashtags, emojis, and CTAs optimized for each platform

3. **Email Marketing Writer (邮件营销文案生成器)**
   - Category: content-generation
   - Generates complete email campaigns with subject lines, body, and CTAs
   - Includes spam check and A/B testing variants

### Features

Each template includes:
- ✅ Bilingual naming (English + Chinese)
- ✅ Detailed usage instructions in Chinese
- ✅ Realistic workflow graph with LLM nodes
- ✅ Input schema validation
- ✅ Tags for discovery
- ✅ Template categorization

### Output

The script will:
- Check for existing templates (by slug) to avoid duplicates
- Create new templates and assign them to the first user in the database
- Print progress and summary of created/skipped templates

### Troubleshooting

**Error: "No user found"**
- Create a user first by running the user service or using a seed user script

**Error: Database connection failed**
- Ensure PostgreSQL is running on the configured port
- Check DATABASE_URL in your .env file
- Verify alembic migrations have been applied

### Next Steps

After seeding templates:
1. Run the migration if not already done: `alembic upgrade head`
2. Start the agent service: `uvicorn services.agent_service.app.main:app --reload --port 8005`
3. Access templates via API: `GET /v1/workflows?is_template=true&category=content-generation`
4. View templates in the web UI at `/agents/gallery`
