"""Routers package initialization."""

from .simulation import router as simulation_router
from .optimization import router as optimization_router
from .portfolio import router as portfolio_router
from .instruments import router as instruments_router
from .rebalancing import router as rebalancing_router

__all__ = [
    'simulation_router',
    'optimization_router',
    'portfolio_router',
    'instruments_router',
    'rebalancing_router',
]
