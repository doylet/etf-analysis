"""
Celery Task Queue Configuration

Handles async task execution for long-running operations like Monte Carlo simulations.
Uses Redis as the message broker and result backend.
"""

from celery import Celery
from celery.result import AsyncResult
import os
import logging
from typing import Dict, Any

from domain.simulation import SimulationParameters
from services.monte_carlo_service import MonteCarloService
from services.storage_adapter import DataStorageAdapter
from repositories.price_data_repository import PriceDataRepository


logger = logging.getLogger(__name__)


# Get Redis configuration from environment or use defaults
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


# Create Celery application
celery_app = Celery(
    'etf_analysis',
    broker=REDIS_URL,
    backend=REDIS_URL
)


# Configure Celery
celery_app.conf.update(
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=270,  # Soft limit at 4.5 minutes
    
    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={'master_name': 'mymaster'},
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


# Task placeholder - actual tasks will be defined here
@celery_app.task(name='monte_carlo_simulation', bind=True)
def monte_carlo_simulation_task(self, simulation_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Background task for Monte Carlo portfolio simulation.
    
    Args:
        self: Celery task instance (for progress tracking)
        simulation_params: Dictionary containing simulation parameters
        
    Returns:
        Dictionary containing simulation results
        
    Raises:
        Exception: If simulation fails
    """
    try:
        # Update task status to started
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Initializing simulation...'}
        )
        
        # Parse simulation parameters
        try:
            # Convert dict back to SimulationParameters domain object
            params = SimulationParameters(
                symbols=simulation_params['symbols'],
                start_date=simulation_params['start_date'],
                end_date=simulation_params['end_date'],
                num_simulations=simulation_params['num_simulations'],
                time_horizon=simulation_params['time_horizon'],
                initial_investment=simulation_params['initial_investment'],
                risk_free_rate=simulation_params.get('risk_free_rate', 0.02),
                confidence_level=simulation_params.get('confidence_level', 0.95),
                rebalancing_frequency=simulation_params.get('rebalancing_frequency', 'monthly')
            )
        except Exception as e:
            logger.error(f"Failed to parse simulation parameters: {e}")
            raise Exception(f"Invalid simulation parameters: {str(e)}")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Setting up data repositories...'}
        )
        
        # Initialize services
        storage = DataStorageAdapter()
        price_repo = PriceDataRepository(storage)
        monte_carlo_service = MonteCarloService(price_data_repository=price_repo)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': 'Loading historical data...'}
        )
        
        # Run simulation with progress tracking
        logger.info(f"Starting Monte Carlo simulation with {params.num_simulations} paths")
        
        # Update progress during simulation
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Running Monte Carlo simulation...'}
        )
        
        # Execute the simulation
        result = monte_carlo_service.run_simulation(params)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': 'Processing results...'}
        )
        
        # Convert result to serializable format
        serializable_result = {
            'simulation_id': result.simulation_id,
            'parameters': {
                'symbols': result.parameters.symbols,
                'start_date': result.parameters.start_date,
                'end_date': result.parameters.end_date,
                'num_simulations': result.parameters.num_simulations,
                'time_horizon': result.parameters.time_horizon,
                'initial_investment': result.parameters.initial_investment,
                'risk_free_rate': result.parameters.risk_free_rate,
                'confidence_level': result.parameters.confidence_level,
                'rebalancing_frequency': result.parameters.rebalancing_frequency
            },
            'results': {
                'final_values': result.results.final_values.tolist() if hasattr(result.results.final_values, 'tolist') else result.results.final_values,
                'returns': result.results.returns.tolist() if hasattr(result.results.returns, 'tolist') else result.results.returns,
                'expected_return': float(result.results.expected_return),
                'volatility': float(result.results.volatility),
                'sharpe_ratio': float(result.results.sharpe_ratio),
                'max_drawdown': float(result.results.max_drawdown),
                'var_95': float(result.results.var_95),
                'cvar_95': float(result.results.cvar_95),
                'probability_of_loss': float(result.results.probability_of_loss)
            },
            'metadata': {
                'created_at': result.metadata.created_at.isoformat(),
                'execution_time_seconds': result.metadata.execution_time_seconds,
                'data_points_used': result.metadata.data_points_used,
                'simulation_method': result.metadata.simulation_method
            }
        }
        
        # Final progress update
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Simulation completed successfully'}
        )
        
        logger.info(f"Monte Carlo simulation completed successfully: {result.simulation_id}")
        return serializable_result
        
    except Exception as e:
        logger.error(f"Monte Carlo simulation failed: {e}", exc_info=True)
        self.update_state(
            state='FAILURE',
            meta={'current': 0, 'total': 100, 'status': f'Simulation failed: {str(e)}', 'error': str(e)}
        )
        raise Exception(f"Simulation failed: {str(e)}")


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get status of a Celery task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Dictionary with task status information
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state == 'PENDING':
            return {
                'task_id': task_id,
                'state': 'PENDING',
                'current': 0,
                'total': 100,
                'status': 'Task is waiting to be processed'
            }
        elif task_result.state == 'PROGRESS':
            return {
                'task_id': task_id,
                'state': 'PROGRESS',
                'current': task_result.info.get('current', 0),
                'total': task_result.info.get('total', 100),
                'status': task_result.info.get('status', 'Processing...')
            }
        elif task_result.state == 'SUCCESS':
            return {
                'task_id': task_id,
                'state': 'SUCCESS',
                'current': 100,
                'total': 100,
                'status': 'Task completed successfully',
                'result': task_result.result
            }
        elif task_result.state == 'FAILURE':
            return {
                'task_id': task_id,
                'state': 'FAILURE',
                'current': 0,
                'total': 100,
                'status': task_result.info.get('status', 'Task failed'),
                'error': str(task_result.info)
            }
        else:
            return {
                'task_id': task_id,
                'state': task_result.state,
                'current': 0,
                'total': 100,
                'status': f'Task state: {task_result.state}'
            }
            
    except Exception as e:
        logger.error(f"Failed to get task status for {task_id}: {e}")
        return {
            'task_id': task_id,
            'state': 'ERROR',
            'current': 0,
            'total': 100,
            'status': f'Failed to retrieve task status: {str(e)}',
            'error': str(e)
        }


def get_task_result(task_id: str) -> Any:
    """
    Get result of completed Celery task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task result or None if not completed
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.ready():
            return task_result.result
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get task result for {task_id}: {e}")
        return None


def cancel_task(task_id: str) -> Dict[str, Any]:
    """
    Cancel a running Celery task.
    
    Args:
        task_id: Celery task ID to cancel
        
    Returns:
        Cancellation status
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        logger.info(f"Task {task_id} cancellation requested")
        
        return {
            'task_id': task_id,
            'status': 'cancellation_requested',
            'message': 'Task cancellation has been requested'
        }
        
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {e}")
        return {
            'task_id': task_id,
            'status': 'cancellation_failed',
            'error': str(e)
        }


__all__ = ['celery_app', 'monte_carlo_simulation_task', 'get_task_status', 'get_task_result', 'cancel_task']
