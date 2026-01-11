"""
Recommendation utility functions for calculating tool recommendations,
combinations, and related scenarios based on user interactions and scenario data.
"""

from typing import List, Dict, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from pydantic import UUID4

from shared.models import Tool, Scenario, UserInteraction, tool_scenarios


async def calculate_top_tools_by_interactions(
    db: AsyncSession,
    scenario_id: UUID4,
    limit: int = 5,
    interaction_weights: Optional[Dict[str, float]] = None
) -> List[Tuple[Tool, float]]:
    """
    Calculate top tools for a scenario based on weighted user interactions.

    Args:
        db: Database session
        scenario_id: Scenario UUID to get tools for
        limit: Maximum number of tools to return (default: 5)
        interaction_weights: Custom weights for interaction types
            Default: {'view': 1.0, 'click': 2.0, 'like': 3.0, 'run': 4.0, 'fork': 5.0}

    Returns:
        List of tuples (Tool, recommendation_score) sorted by score descending

    Edge cases:
        - Returns empty list if scenario has no tools
        - Falls back to static ranking (github_stars, review_count) when no interaction data
        - Handles missing or invalid scenario_id gracefully
    """
    # Default interaction weights
    if interaction_weights is None:
        interaction_weights = {
            'view': 1.0,
            'click': 2.0,
            'like': 3.0,
            'run': 4.0,
            'fork': 5.0,
        }

    # Get all tools for this scenario
    tools_query = (
        select(Tool)
        .join(tool_scenarios, Tool.id == tool_scenarios.c.tool_id)
        .where(tool_scenarios.c.scenario_id == scenario_id)
        .options(selectinload(Tool.category), selectinload(Tool.scenarios))
    )
    result = await db.execute(tools_query)
    tools = result.scalars().all()

    if not tools:
        return []

    tool_ids = [tool.id for tool in tools]

    # Calculate interaction scores for each tool
    interaction_query = (
        select(
            UserInteraction.item_id,
            UserInteraction.action,
            func.count(UserInteraction.id).label('count')
        )
        .where(
            and_(
                UserInteraction.item_type == 'tool',
                UserInteraction.item_id.in_(tool_ids)
            )
        )
        .group_by(UserInteraction.item_id, UserInteraction.action)
    )
    interaction_result = await db.execute(interaction_query)
    interactions = interaction_result.all()

    # Build interaction score map
    tool_scores = {}
    for item_id, action, count in interactions:
        weight = interaction_weights.get(action, 1.0)
        score = count * weight
        if item_id not in tool_scores:
            tool_scores[item_id] = 0.0
        tool_scores[item_id] += score

    # Score each tool - use interactions if available, otherwise fall back to static metrics
    scored_tools = []
    for tool in tools:
        if tool.id in tool_scores:
            score = tool_scores[tool.id]
        else:
            # Fallback to static ranking when no interaction data
            score = (
                (tool.github_stars or 0) * 0.1 +
                (tool.review_count or 0) * 2.0 +
                (tool.avg_rating or 0) * 10.0
            )
        scored_tools.append((tool, score))

    # Sort by score descending and return top N
    scored_tools.sort(key=lambda x: x[1], reverse=True)
    return scored_tools[:limit]


async def find_tool_combinations(
    db: AsyncSession,
    scenario_id: UUID4,
    min_co_occurrence: int = 2,
    limit: int = 10
) -> List[Dict]:
    """
    Find tool combinations (pairs) that commonly appear together in scenarios.

    Args:
        db: Database session
        scenario_id: Scenario UUID to find combinations for
        min_co_occurrence: Minimum number of shared scenarios to be considered a combination
        limit: Maximum number of combinations to return

    Returns:
        List of dicts with structure:
        [
            {
                'tools': [Tool, Tool],  # Pair of tools
                'co_occurrence_count': int,  # Number of scenarios they share
                'shared_scenario_ids': [UUID, ...]  # List of scenario IDs they share
            },
            ...
        ]
        Sorted by co_occurrence_count descending

    Edge cases:
        - Returns empty list if scenario has fewer than 2 tools
        - Only considers tools within the same scenario
        - Excludes combinations with co_occurrence below min_co_occurrence
    """
    # Get all tools for this scenario
    tools_query = (
        select(Tool)
        .join(tool_scenarios, Tool.id == tool_scenarios.c.tool_id)
        .where(tool_scenarios.c.scenario_id == scenario_id)
        .options(selectinload(Tool.category), selectinload(Tool.scenarios))
    )
    result = await db.execute(tools_query)
    tools = result.scalars().all()

    if len(tools) < 2:
        return []

    # For each pair of tools, count how many scenarios they share
    combinations = []
    tools_list = list(tools)

    for i in range(len(tools_list)):
        for j in range(i + 1, len(tools_list)):
            tool_a = tools_list[i]
            tool_b = tools_list[j]

            # Find shared scenarios between tool_a and tool_b
            shared_scenarios_query = (
                select(tool_scenarios.c.scenario_id)
                .where(tool_scenarios.c.tool_id == tool_a.id)
                .intersect(
                    select(tool_scenarios.c.scenario_id)
                    .where(tool_scenarios.c.tool_id == tool_b.id)
                )
            )
            shared_result = await db.execute(shared_scenarios_query)
            shared_scenario_ids = [row[0] for row in shared_result.all()]
            co_occurrence = len(shared_scenario_ids)

            if co_occurrence >= min_co_occurrence:
                combinations.append({
                    'tools': [tool_a, tool_b],
                    'co_occurrence_count': co_occurrence,
                    'shared_scenario_ids': shared_scenario_ids
                })

    # Sort by co_occurrence_count descending
    combinations.sort(key=lambda x: x['co_occurrence_count'], reverse=True)
    return combinations[:limit]


async def find_related_scenarios(
    db: AsyncSession,
    scenario_id: UUID4,
    limit: int = 5,
    min_similarity: float = 0.1
) -> List[Tuple[Scenario, float]]:
    """
    Find related scenarios based on Jaccard similarity of shared tools.

    Jaccard similarity = |intersection| / |union|

    Args:
        db: Database session
        scenario_id: Scenario UUID to find related scenarios for
        limit: Maximum number of related scenarios to return
        min_similarity: Minimum Jaccard similarity score (0.0 to 1.0)

    Returns:
        List of tuples (Scenario, similarity_score) sorted by similarity descending
        Excludes the input scenario itself

    Edge cases:
        - Returns empty list if scenario has no tools
        - Returns empty list if no other scenarios exist
        - Excludes scenarios with similarity below min_similarity
        - Only considers scenarios that share at least one tool
    """
    # Get tools for the target scenario
    target_tools_query = (
        select(Tool.id)
        .join(tool_scenarios, Tool.id == tool_scenarios.c.tool_id)
        .where(tool_scenarios.c.scenario_id == scenario_id)
    )
    target_result = await db.execute(target_tools_query)
    target_tool_ids = set(row[0] for row in target_result.all())

    if not target_tool_ids:
        return []

    # Get all other scenarios with their tools
    all_scenarios_query = (
        select(Scenario)
        .where(Scenario.id != scenario_id)
    )
    scenarios_result = await db.execute(all_scenarios_query)
    other_scenarios = scenarios_result.scalars().all()

    if not other_scenarios:
        return []

    # Calculate Jaccard similarity for each scenario
    similarities = []

    for scenario in other_scenarios:
        # Get tools for this scenario
        scenario_tools_query = (
            select(Tool.id)
            .join(tool_scenarios, Tool.id == tool_scenarios.c.tool_id)
            .where(tool_scenarios.c.scenario_id == scenario.id)
        )
        scenario_result = await db.execute(scenario_tools_query)
        scenario_tool_ids = set(row[0] for row in scenario_result.all())

        if not scenario_tool_ids:
            continue

        # Calculate Jaccard similarity
        intersection = len(target_tool_ids & scenario_tool_ids)
        union = len(target_tool_ids | scenario_tool_ids)

        if union > 0:
            similarity = intersection / union

            if similarity >= min_similarity:
                similarities.append((scenario, similarity))

    # Sort by similarity descending
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:limit]
