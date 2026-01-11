from typing import List, Dict, Any, Optional
import json
import logging
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from shared.config import settings

logger = logging.getLogger(__name__)

class GraphNode(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None

class GeneratedGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class PlannerAgent:
    """
    Agent responsible for translating natural language into executable graph structures.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_URL.replace("/chat/completions", ""),
            model="deepseek-chat",
            temperature=0.2,
        ).with_structured_output(GeneratedGraph)

    async def plan_workflow(self, prompt: str, current_graph: Optional[Dict[str, Any]] = None) -> GeneratedGraph:
        """
        Plans or refines a workflow graph based on the user prompt and optional current state.
        """
        context_str = ""
        if current_graph:
            context_str = f"\nCURRENT GRAPH STRUCTURE:\n{json.dumps(current_graph, indent=2)}\n"

        system_prompt = f"""
        You are an expert AI Workflow Architect (Visual Programming Specialist).
        Your mission is to translate high-level user intent into a precise, executable visual graph structure (DAG or cyclic graph).
        {context_str}
        
        AVAILABLE NODE TYPES & CAPABILITIES:
        1. 'input': Entry point for data. Fields: label, inputType (text|number|json|file).
        2. 'llm': Reasoning core. Fields: label, model (deepseek-chat|deepseek-reasoner), temperature (0.0-1.0), prompt (use {{{{input}}}} or {{{{context}}}} as placeholders).
        3. 'skill': External tool execution. Fields: label, tool_id (e.g., 'search', 'weather', 'calculator').
        4. 'transform': Data manipulation. Fields: transform_type (extract|template|json_parse|array_join), template (for template type), field (for extract type).
        5. 'output': Final destination. Fields: format (markdown|json|text).
        
        TOPOLOGICAL & ARCHITECTURAL RULES:
        - MANDATORY: Every graph must have exactly one 'input' node and at least one 'output' node.
        - FLOW: Data flows from ports. Ensure source/target connections are logical.
        - PERSISTENCE: If CURRENT GRAPH STRUCTURE exists, preserve existing node IDs (e.g., 'node-123') unless intentionally deleting them.
        - SPATIAL ARRANGEMENT: 
            * Scale: 300px horizontal spacing, 200px vertical spacing.
            * Horizontal layers (Input -> LLM/Skill -> Output).
            * If branching, use vertical offsets (e.g., y=150, y=350).
        - COMPLEX LOGIC:
            * For multi-step reasoning, chain multiple 'llm' nodes.
            * Use 'transform' to clean LLM output before tool calls if needed.
        
        OUTPUT FORMAT:
        Return a valid JSON object matching the GeneratedGraph schema.
        """

        try:
            result = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ])
            
            # Post-generation validation and repair
            return self._ensure_graph_integrity(result)
        except Exception as e:
            logger.error(f"Error during workflow planning: {str(e)}")
            raise

    def _ensure_graph_integrity(self, graph: GeneratedGraph) -> GeneratedGraph:
        """
        Ensures the generated graph meets minimum structural requirements.
        Repairs minor issues like missing required nodes or invalid positions.
        """
        node_types = [n.type for n in graph.nodes]
        
        # Ensure 'input' exists
        if 'input' not in node_types:
            graph.nodes.insert(0, GraphNode(
                id=f"input-{int(datetime.now().timestamp())}",
                type="input",
                position={"x": 0, "y": 150},
                data={"label": "Input", "inputType": "text"}
            ))
            
        # Ensure 'output' exists
        if 'output' not in node_types:
            last_x = max([n.position["x"] for n in graph.nodes]) if graph.nodes else 0
            graph.nodes.append(GraphNode(
                id=f"output-{int(datetime.now().timestamp())}",
                type="output",
                position={"x": last_x + 300, "y": 150},
                data={"label": "Output", "format": "markdown"}
            ))
            
        # Basic edge validation could be added here
        return graph

