"""
Task status and result endpoints for async operations.

Provides endpoints to check Celery task status and retrieve results.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Any, Dict, Optional

from api.auth import get_current_user
from api.schemas.common import TaskStatusResponse
from api.tasks import get_task_status as get_celery_task_status, get_task_result, cancel_task as cancel_celery_task
from api.dependencies import get_celery_app

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str
) -> TaskStatusResponse:
    """
    Get the status of a background task.
    
    Args:
        task_id: The Celery task ID
        current_user: Authenticated user information
        
    Returns:
        TaskStatusResponse with current status
        
    Raises:
        HTTPException: If task not found or access denied
    """
    try:
        # Get task status from Celery using our task module function
        status_info = get_celery_task_status(task_id)
        
        # Map Celery states to our API states
        status_mapping = {
            'PENDING': 'pending',
            'STARTED': 'running',
            'RETRY': 'running',
            'PROGRESS': 'running',
            'SUCCESS': 'completed',
            'FAILURE': 'failed',
            'REVOKED': 'cancelled'
        }
        
        state = status_info.get("state", "PENDING")
        status = status_mapping.get(state, 'unknown')
        info = status_info.get("info", {})
        
        # Extract progress information
        progress = None
        if isinstance(info, dict):
            progress = info.get('progress', 0)
        elif state == 'SUCCESS':
            progress = 100
        
        # Handle different states
        if state == 'SUCCESS':
            return TaskStatusResponse(
                task_id=task_id,
                status=status,
                progress=100,
                result=info,
                error=None,
                created_at=None,  # Celery doesn't provide creation time easily
                completed_at=None  # Would need custom tracking
            )
        elif state == 'FAILURE':
            error_message = str(info) if info else "Task failed"
            return TaskStatusResponse(
                task_id=task_id,
                status=status,
                progress=None,
                result=None,
                error=error_message,
                created_at=None,
                completed_at=None
            )
        else:
            # PENDING, STARTED, RETRY, PROGRESS
            return TaskStatusResponse(
                task_id=task_id,
                status=status,
                progress=progress,
                result=None,
                error=None,
                created_at=None,
                completed_at=None
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving task status: {str(e)}"
        )


@router.get("/{task_id}/result")
async def get_task_result(
    task_id: str,
    celery_app = Depends(get_celery_app)
) -> Dict[str, Any]:
    """
    Get the result of a completed task.
    
    Args:
        task_id: The Celery task ID
        current_user: Authenticated user information
        celery_app: Celery application instance
        
    Returns:
        Task result data
        
    Raises:
        HTTPException: If task not found, not completed, or failed
    """
    try:
        task_result = celery_app.AsyncResult(task_id)
        
        if not task_result:
            raise HTTPException(status_code=404, detail="Task not found")
        
        state = task_result.state
        
        if state == 'PENDING':
            raise HTTPException(
                status_code=202,
                detail="Task is still pending"
            )
        elif state in ['STARTED', 'RETRY', 'PROGRESS']:
            raise HTTPException(
                status_code=202, 
                detail="Task is still running"
            )
        elif state == 'FAILURE':
            error_info = task_result.info or {}
            raise HTTPException(
                status_code=400,
                detail=f"Task failed: {error_info}"
            )
        elif state == 'SUCCESS':
            return {
                "task_id": task_id,
                "status": "completed",
                "result": task_result.result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Task in unexpected state: {state}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving task result: {str(e)}"
        )


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    celery_app = Depends(get_celery_app)
) -> Dict[str, str]:
    """
    Cancel a running task.
    
    Args:
        task_id: The Celery task ID to cancel
        current_user: Authenticated user information 
        celery_app: Celery application instance
        
    Returns:
        Cancellation confirmation
        
    Raises:
        HTTPException: If task not found or cannot be cancelled
    """
    try:
        task_result = celery_app.AsyncResult(task_id)
        
        if not task_result:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Attempt to revoke the task
        celery_app.control.revoke(task_id, terminate=True)
        
        return {
            "task_id": task_id,
            "message": "Task cancellation requested"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error cancelling task: {str(e)}"
        )


@router.get("/")
async def list_active_tasks(
    celery_app = Depends(get_celery_app)
) -> Dict[str, Any]:
    """
    List all active tasks for monitoring.
    
    Args:
        current_user: Authenticated user information
        celery_app: Celery application instance
        
    Returns:
        List of active tasks
        
    Note:
        This requires Celery to be configured with result backend
        and proper monitoring capabilities.
    """
    try:
        # Get active tasks from Celery
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if not active_tasks:
            return {"active_tasks": []}
        
        # Format the response
        formatted_tasks = []
        for worker, tasks in active_tasks.items():
            for task in tasks:
                formatted_tasks.append({
                    "task_id": task.get("id"),
                    "name": task.get("name"),
                    "worker": worker,
                    "args": task.get("args", []),
                    "kwargs": task.get("kwargs", {}),
                    "time_start": task.get("time_start")
                })
        
        return {"active_tasks": formatted_tasks}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving active tasks: {str(e)}"
        )