"""Base adapter class for converting widgets to API endpoints."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
import logging
from datetime import datetime

from ..schemas.widgets import WidgetResponse, WidgetError
from ..exceptions import WidgetError as WidgetException

logger = logging.getLogger(__name__)


class BaseWidgetAdapter(ABC):
    """Base class for all widget API adapters.
    
    Converts existing Streamlit widgets into JSON-serializable API responses
    while preserving calculation accuracy and error handling.
    """
    
    def __init__(self, storage, widget_class: Type):
        """Initialize adapter with database storage and widget class.
        
        Args:
            storage: Database storage instance
            widget_class: The Streamlit widget class to adapt
        """
        self.storage = storage
        self.widget_class = widget_class
        self._widget_instance = None
        
    @abstractmethod
    def get_widget_name(self) -> str:
        """Return the API-friendly widget name."""
        pass
        
    @abstractmethod
    def get_widget_description(self) -> str:
        """Return widget description for API documentation."""
        pass
        
    @abstractmethod 
    def extract_calculation_data(self, widget_instance) -> Dict[str, Any]:
        """Extract pure calculation data from widget instance.
        
        This method should extract only the mathematical/analytical results
        without any Streamlit UI components like st.divider(), st.columns(), etc.
        
        Args:
            widget_instance: Instance of the Streamlit widget
            
        Returns:
            Dict containing JSON-serializable calculation results
        """
        pass
        
    @abstractmethod
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate and normalize input parameters.
        
        Returns:
            Dict of validated parameters
            
        Raises:
            WidgetException: If validation fails
        """
        pass
        
    async def execute(self, **kwargs) -> WidgetResponse:
        """Execute widget calculation and return API response.
        
        Args:
            **kwargs: Widget-specific parameters
            
        Returns:
            WidgetResponse with calculation results or error
        """
        try:
            # Validate input parameters
            validated_params = self.validate_input_parameters(**kwargs)
            
            # Create widget instance with validated parameters
            widget_instance = self._create_widget_instance(validated_params)
            
            # Extract calculation data (avoiding UI components)
            calculation_data = self.extract_calculation_data(widget_instance)
            
            # Build response
            return WidgetResponse(
                widget_name=self.get_widget_name(),
                success=True,
                data=calculation_data,
                metadata={
                    "execution_time": datetime.utcnow().isoformat(),
                    "parameters": validated_params,
                    "widget_description": self.get_widget_description()
                },
                error=None
            )
            
        except WidgetException as e:
            logger.warning(f"Widget validation error in {self.get_widget_name()}: {e}")
            return WidgetResponse(
                widget_name=self.get_widget_name(),
                success=False,
                data=None,
                metadata={
                    "execution_time": datetime.utcnow().isoformat(),
                    "parameters": kwargs,
                    "widget_description": self.get_widget_description()
                },
                error=WidgetError(
                    code="VALIDATION_ERROR", 
                    message=str(e),
                    details={"parameter_errors": e.details if hasattr(e, 'details') else {}}
                )
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.get_widget_name()}: {e}", exc_info=True)
            return WidgetResponse(
                widget_name=self.get_widget_name(),
                success=False,
                data=None,
                metadata={
                    "execution_time": datetime.utcnow().isoformat(),
                    "parameters": kwargs,
                    "widget_description": self.get_widget_description()
                },
                error=WidgetError(
                    code="INTERNAL_ERROR",
                    message="An unexpected error occurred during calculation",
                    details={"error_type": type(e).__name__}
                )
            )
    
    def _create_widget_instance(self, validated_params: Dict[str, Any]):
        """Create widget instance with validated parameters.
        
        Args:
            validated_params: Validated input parameters
            
        Returns:
            Widget instance ready for calculation
        """
        # Create a unique widget ID for this API call
        widget_id = f"{self.get_widget_name()}_{hash(str(validated_params))}"
        
        # Instantiate the widget with storage and ID
        return self.widget_class(self.storage, widget_id)