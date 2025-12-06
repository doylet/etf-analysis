"""
Instruments CRUD API router.

Endpoints for managing tracked financial instruments.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional

from api.schemas.portfolio import (
    InstrumentResponse,
    InstrumentListResponse,
    InstrumentCreateRequest,
    InstrumentUpdateRequest,
    InstrumentTypeEnum,
)
from services.storage_adapter import DataStorageAdapter
from repositories.instrument_repository import InstrumentRepository
from domain.portfolio import InstrumentDomainModel, InstrumentType
from api.auth import get_current_user, User
from api.exceptions import ResourceNotFoundError, BusinessLogicError


router = APIRouter(prefix="/instruments", tags=["Instruments"])


def get_instrument_repository() -> InstrumentRepository:
    """Get instrument repository instance."""
    storage = DataStorageAdapter()
    return InstrumentRepository(storage)


@router.get("", response_model=InstrumentListResponse)
async def list_instruments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    active_only: bool = Query(True, description="Only return active instruments"),
    search: Optional[str] = Query(None, description="Search by symbol or name"),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of tracked instruments.
    
    Supports filtering by active status and searching by symbol/name.
    """
    try:
        repo = get_instrument_repository()
        
        # Get instruments
        if search:
            instruments = repo.search(search)
        elif active_only:
            instruments = repo.find_all_active()
        else:
            # Get all instruments (active and inactive)
            instruments = repo.find_all_active()  # TODO: Add find_all method
        
        # Apply pagination
        total = len(instruments)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated = instruments[start_idx:end_idx]
        
        # Convert to response format
        instrument_responses = [
            InstrumentResponse(
                symbol=inst.symbol,
                name=inst.name,
                type=InstrumentTypeEnum[inst.type.value],
                sector=inst.sector,
                currency=inst.currency,
                quantity=inst.quantity,
                current_value=inst.current_value,
                average_cost=inst.average_cost
            )
            for inst in paginated
        ]
        
        return InstrumentListResponse(
            instruments=instrument_responses,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list instruments: {str(e)}")


@router.get("/{symbol}", response_model=InstrumentResponse)
async def get_instrument(symbol: str):
    """
    Get details for a specific instrument.
    
    Returns instrument information including current holdings.
    """
    try:
        repo = get_instrument_repository()
        instrument = repo.find_by_symbol(symbol.upper())
        
        if not instrument:
            raise ResourceNotFoundError("Instrument", symbol)
        
        return InstrumentResponse(
            symbol=instrument.symbol,
            name=instrument.name,
            type=InstrumentTypeEnum[instrument.type.value],
            sector=instrument.sector,
            currency=instrument.currency,
            quantity=instrument.quantity,
            current_value=instrument.current_value,
            average_cost=instrument.average_cost
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get instrument: {str(e)}")


@router.post("", response_model=InstrumentResponse, status_code=201)
async def create_instrument(request: InstrumentCreateRequest):
    """
    Add a new instrument to track.
    
    The instrument will be available for portfolio operations.
    """
    try:
        repo = get_instrument_repository()
        
        # Check if instrument already exists
        existing = repo.find_by_symbol(request.symbol)
        if existing:
            raise BusinessLogicError(f"Instrument '{request.symbol}' already exists", 409)
        
        # Create domain model
        instrument = InstrumentDomainModel(
            symbol=request.symbol,
            name=request.name,
            type=InstrumentType[request.type.value],
            sector=request.sector,
            currency=request.currency,
            quantity=0,
            current_value=0,
            average_cost=0
        )
        
        # Add to repository
        created = repo.add(instrument)
        
        return InstrumentResponse(
            symbol=created.symbol,
            name=created.name,
            type=InstrumentTypeEnum[created.type.value],
            sector=created.sector,
            currency=created.currency,
            quantity=created.quantity,
            current_value=created.current_value,
            average_cost=created.average_cost
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create instrument: {str(e)}")


@router.patch("/{symbol}", response_model=InstrumentResponse)
async def update_instrument(symbol: str, request: InstrumentUpdateRequest):
    """
    Update instrument details.
    
    Allows updating name and sector. Symbol cannot be changed.
    """
    try:
        repo = get_instrument_repository()
        
        # Check if instrument exists
        existing = repo.find_by_symbol(symbol.upper())
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Instrument '{symbol}' not found"
            )
        
        # Prepare updates
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.sector is not None:
            updates['sector'] = request.sector
        
        if not updates:
            # No changes requested
            return InstrumentResponse(
                symbol=existing.symbol,
                name=existing.name,
                type=InstrumentTypeEnum[existing.type.value],
                sector=existing.sector,
                currency=existing.currency,
                quantity=existing.quantity,
                current_value=existing.current_value,
                average_cost=existing.average_cost
            )
        
        # Update instrument
        updated = repo.update(symbol.upper(), updates)
        
        return InstrumentResponse(
            symbol=updated.symbol,
            name=updated.name,
            type=InstrumentTypeEnum[updated.type.value],
            sector=updated.sector,
            currency=updated.currency,
            quantity=updated.quantity,
            current_value=updated.current_value,
            average_cost=updated.average_cost
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update instrument: {str(e)}")


@router.delete("/{symbol}", status_code=204)
async def delete_instrument(symbol: str):
    """
    Remove (deactivate) an instrument.
    
    The instrument will be marked inactive but not deleted from the database.
    Historical data and orders are preserved.
    """
    try:
        repo = get_instrument_repository()
        
        # Check if instrument exists
        existing = repo.find_by_symbol(symbol.upper())
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Instrument '{symbol}' not found"
            )
        
        # Remove instrument (marks as inactive)
        success = repo.remove(symbol.upper())
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to remove instrument '{symbol}'"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete instrument: {str(e)}")
