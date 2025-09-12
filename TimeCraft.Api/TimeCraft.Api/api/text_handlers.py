"""
Text processing endpoints for TimeCraft API.
"""

from fastapi.responses import JSONResponse
from .models import TextRefinementRequest
from .helpers import create_demo_response, handle_api_error


def handle_refine_text(request: TextRefinementRequest, timecraft_available: bool) -> JSONResponse:
    """Refine textual descriptions using multi-agent approach."""
    try:
        if not timecraft_available:
            return create_demo_response(
                "demo_mode",
                "TimeCraft components not available. This is a demo response.",
                original_text=request.text,
                refined_text=f"[DEMO] Refined version of: {request.text[:100]}...",
                refinement_type=request.refinement_type,
                note="In production, this would use actual multi-agent refinement"
            )
        
        # Import TimeCraft modules for text refinement
        from TimeCraft.refine_text import refine_with_multi_agent
        
        # Process text refinement
        refined_result = refine_with_multi_agent(
            request.text,
            refinement_type=request.refinement_type,
            num_iterations=getattr(request, 'num_iterations', 3)
        )
        
        return JSONResponse({
            "status": "success",
            "original_text": request.text,
            "refined_text": refined_result.get("refined_text", request.text),
            "refinement_type": request.refinement_type,
            "details": refined_result
        })
        
    except Exception as e:
        return handle_api_error("refine_text", e)