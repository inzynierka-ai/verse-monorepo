import logging
from .workflow_loader import WorkflowLoader
from .character_workflow import CharacterWorkflowLoader
from .location_workflow import LocationWorkflowLoader


class WorkflowLoaderFactory:
    """Factory for creating workflow loaders based on context"""
    
    @staticmethod
    def create_loader(context_type: str) -> WorkflowLoader:
        """
        Create a workflow loader based on the context type
        
        Args:
            context_type: Type of context ('character' or 'location')
            
        Returns:
            Appropriate workflow loader for the context
        """
        if context_type.lower() == "character":
            return CharacterWorkflowLoader()
        elif context_type.lower() == "location":
            return LocationWorkflowLoader()
        else:
            # Default to character if unknown
            logging.warning(f"Unknown context type: {context_type}, using character workflow")
            return CharacterWorkflowLoader() 