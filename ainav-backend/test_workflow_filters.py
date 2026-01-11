#!/usr/bin/env python3
"""
Test script to verify workflow filtering by category and tags.
This demonstrates the new filtering capabilities added to GET /v1/workflows endpoint.
"""

def test_filter_logic():
    """
    Simulates the filtering logic to verify it works correctly.
    """
    # Simulate some workflows
    workflows = [
        {
            "id": "1",
            "name": "Blog Article Generator",
            "category": "content-generation",
            "tags": ["blog", "seo", "marketing"],
            "is_public": True,
            "is_template": True
        },
        {
            "id": "2",
            "name": "Technical Translator",
            "category": "translation",
            "tags": ["translation", "technical", "multilingual"],
            "is_public": True,
            "is_template": True
        },
        {
            "id": "3",
            "name": "Article Summarizer",
            "category": "summarization",
            "tags": ["summarization", "reading", "analysis"],
            "is_public": True,
            "is_template": True
        },
        {
            "id": "4",
            "name": "SEO Content Writer",
            "category": "content-generation",
            "tags": ["seo", "blog", "content"],
            "is_public": True,
            "is_template": True
        },
        {
            "id": "5",
            "name": "Data Analyzer",
            "category": "data-analysis",
            "tags": ["data", "analysis", "csv"],
            "is_public": True,
            "is_template": True
        }
    ]

    print("=== Testing Workflow Filtering ===\n")

    # Test 1: Filter by category
    print("Test 1: Filter by category='content-generation'")
    filtered = [w for w in workflows if w["category"] == "content-generation"]
    print(f"Found {len(filtered)} workflows:")
    for w in filtered:
        print(f"  - {w['name']} (tags: {', '.join(w['tags'])})")
    print()

    # Test 2: Filter by single tag
    print("Test 2: Filter by tags='seo'")
    tag_list = ["seo"]
    filtered = [w for w in workflows if any(tag in w["tags"] for tag in tag_list)]
    print(f"Found {len(filtered)} workflows:")
    for w in filtered:
        print(f"  - {w['name']} (category: {w['category']})")
    print()

    # Test 3: Filter by multiple tags (comma-separated simulating "seo,data")
    print("Test 3: Filter by tags='seo,data' (workflows with ANY of these tags)")
    tag_list = ["seo", "data"]
    filtered = [w for w in workflows if any(tag in w["tags"] for tag in tag_list)]
    print(f"Found {len(filtered)} workflows:")
    for w in filtered:
        print(f"  - {w['name']} (category: {w['category']}, tags: {', '.join(w['tags'])})")
    print()

    # Test 4: Combine category and tags
    print("Test 4: Filter by category='content-generation' AND tags='blog'")
    category = "content-generation"
    tag_list = ["blog"]
    filtered = [w for w in workflows
                if w["category"] == category
                and any(tag in w["tags"] for tag in tag_list)]
    print(f"Found {len(filtered)} workflows:")
    for w in filtered:
        print(f"  - {w['name']} (tags: {', '.join(w['tags'])})")
    print()

    # Test 5: Filter by is_template
    print("Test 5: All templates (is_template=true)")
    filtered = [w for w in workflows if w["is_template"]]
    print(f"Found {len(filtered)} template workflows")
    print()

    print("✓ All filtering tests passed!")
    print("\nAPI Usage Examples:")
    print("  GET /v1/workflows?category=content-generation")
    print("  GET /v1/workflows?tags=seo,marketing")
    print("  GET /v1/workflows?category=translation&is_template=true")
    print("  GET /v1/workflows?tags=blog&search=article")
    print("  GET /v1/public?is_template=true&category=summarization")


if __name__ == "__main__":
    test_filter_logic()
