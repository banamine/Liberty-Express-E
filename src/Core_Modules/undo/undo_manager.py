"""
Undo/Redo Manager - State management for reversible operations
"""

import copy
import logging
from typing import Any, List, Optional, Dict, Callable
from datetime import datetime
import json


class UndoManager:
    """
    Manages undo/redo functionality with state snapshots.
    Implements a command pattern for reversible operations.
    """
    
    def __init__(self, max_history: int = 50):
        """
        Initialize the undo manager.
        
        Args:
            max_history: Maximum number of states to keep in history
        """
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        self.max_history = max_history
        self.logger = logging.getLogger(__name__)
        self.enabled = True
        self.current_state: Optional[Dict[str, Any]] = None
    
    def save_state(self, state: Any, description: str = "") -> None:
        """
        Save a state snapshot for undo functionality.
        
        Args:
            state: The state to save (will be deep copied)
            description: Description of the operation
        """
        if not self.enabled:
            return
        
        try:
            # Create state snapshot
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'description': description,
                'state': copy.deepcopy(state)
            }
            
            # Add to undo stack
            self.undo_stack.append(snapshot)
            
            # Clear redo stack when new action is performed
            self.redo_stack.clear()
            
            # Limit undo history
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
            
            self.logger.debug(f"State saved: {description}")
            
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def can_undo(self) -> bool:
        """
        Check if undo operation is available.
        
        Returns:
            True if undo is possible
        """
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """
        Check if redo operation is available.
        
        Returns:
            True if redo is possible
        """
        return len(self.redo_stack) > 0
    
    def undo(self) -> Optional[Any]:
        """
        Perform undo operation.
        
        Returns:
            The previous state, or None if undo is not possible
        """
        if not self.can_undo():
            self.logger.debug("No undo history available")
            return None
        
        try:
            # Get the last state
            snapshot = self.undo_stack.pop()
            
            # Save current state to redo stack if we have it
            if self.current_state is not None:
                self.redo_stack.append({
                    'timestamp': datetime.now().isoformat(),
                    'description': f"Redo: {snapshot['description']}",
                    'state': copy.deepcopy(self.current_state)
                })
            
            # Return the previous state
            self.current_state = snapshot['state']
            self.logger.debug(f"Undo performed: {snapshot['description']}")
            
            return copy.deepcopy(snapshot['state'])
            
        except Exception as e:
            self.logger.error(f"Failed to perform undo: {e}")
            return None
    
    def redo(self) -> Optional[Any]:
        """
        Perform redo operation.
        
        Returns:
            The redone state, or None if redo is not possible
        """
        if not self.can_redo():
            self.logger.debug("No redo history available")
            return None
        
        try:
            # Get the state to redo
            snapshot = self.redo_stack.pop()
            
            # Save current state to undo stack if we have it
            if self.current_state is not None:
                self.undo_stack.append({
                    'timestamp': datetime.now().isoformat(),
                    'description': f"Before redo: {snapshot['description']}",
                    'state': copy.deepcopy(self.current_state)
                })
            
            # Return the redone state
            self.current_state = snapshot['state']
            self.logger.debug(f"Redo performed: {snapshot['description']}")
            
            return copy.deepcopy(snapshot['state'])
            
        except Exception as e:
            self.logger.error(f"Failed to perform redo: {e}")
            return None
    
    def clear_history(self) -> None:
        """Clear all undo/redo history"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.current_state = None
        self.logger.debug("Undo/redo history cleared")
    
    def get_undo_description(self) -> str:
        """
        Get description of the last undoable operation.
        
        Returns:
            Description string or empty string
        """
        if self.can_undo():
            return self.undo_stack[-1].get('description', 'Undo')
        return ""
    
    def get_redo_description(self) -> str:
        """
        Get description of the last redoable operation.
        
        Returns:
            Description string or empty string
        """
        if self.can_redo():
            return self.redo_stack[-1].get('description', 'Redo')
        return ""
    
    def set_current_state(self, state: Any) -> None:
        """
        Set the current state for tracking.
        
        Args:
            state: The current state
        """
        self.current_state = copy.deepcopy(state)
    
    def enable(self) -> None:
        """Enable undo/redo functionality"""
        self.enabled = True
        self.logger.debug("Undo/redo enabled")
    
    def disable(self) -> None:
        """Disable undo/redo functionality"""
        self.enabled = False
        self.logger.debug("Undo/redo disabled")
    
    def get_history_info(self) -> Dict[str, Any]:
        """
        Get information about the undo/redo history.
        
        Returns:
            Dictionary with history information
        """
        return {
            'undo_count': len(self.undo_stack),
            'redo_count': len(self.redo_stack),
            'max_history': self.max_history,
            'enabled': self.enabled,
            'can_undo': self.can_undo(),
            'can_redo': self.can_redo(),
            'last_undo': self.get_undo_description(),
            'last_redo': self.get_redo_description()
        }
    
    def export_history(self, filepath: str) -> bool:
        """
        Export undo/redo history to a file for debugging.
        
        Args:
            filepath: Path to export file
            
        Returns:
            True if successful
        """
        try:
            history = {
                'undo_stack': [
                    {
                        'timestamp': s['timestamp'],
                        'description': s['description']
                    }
                    for s in self.undo_stack
                ],
                'redo_stack': [
                    {
                        'timestamp': s['timestamp'],
                        'description': s['description']
                    }
                    for s in self.redo_stack
                ],
                'info': self.get_history_info()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)
            
            self.logger.info(f"History exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export history: {e}")
            return False


class Command:
    """
    Base class for implementing command pattern operations.
    Subclass this for specific reversible operations.
    """
    
    def __init__(self, description: str = ""):
        """
        Initialize a command.
        
        Args:
            description: Description of the command
        """
        self.description = description
        self.executed = False
    
    def execute(self) -> bool:
        """
        Execute the command.
        
        Returns:
            True if successful
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def undo(self) -> bool:
        """
        Undo the command.
        
        Returns:
            True if successful
        """
        raise NotImplementedError("Subclasses must implement undo()")
    
    def redo(self) -> bool:
        """
        Redo the command.
        
        Returns:
            True if successful
        """
        return self.execute()


class CommandManager:
    """
    Manages command-based undo/redo operations.
    Alternative to state-based undo/redo.
    """
    
    def __init__(self, max_history: int = 50):
        """
        Initialize the command manager.
        
        Args:
            max_history: Maximum number of commands to keep
        """
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self.max_history = max_history
        self.logger = logging.getLogger(__name__)
    
    def execute_command(self, command: Command) -> bool:
        """
        Execute a command and add it to history.
        
        Args:
            command: Command to execute
            
        Returns:
            True if successful
        """
        try:
            if command.execute():
                self.undo_stack.append(command)
                self.redo_stack.clear()
                
                # Limit history
                if len(self.undo_stack) > self.max_history:
                    self.undo_stack.pop(0)
                
                self.logger.debug(f"Command executed: {command.description}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to execute command: {e}")
            return False
    
    def undo(self) -> bool:
        """
        Undo the last command.
        
        Returns:
            True if successful
        """
        if not self.undo_stack:
            return False
        
        try:
            command = self.undo_stack.pop()
            if command.undo():
                self.redo_stack.append(command)
                self.logger.debug(f"Command undone: {command.description}")
                return True
            
            # If undo failed, put it back
            self.undo_stack.append(command)
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to undo command: {e}")
            return False
    
    def redo(self) -> bool:
        """
        Redo the last undone command.
        
        Returns:
            True if successful
        """
        if not self.redo_stack:
            return False
        
        try:
            command = self.redo_stack.pop()
            if command.redo():
                self.undo_stack.append(command)
                self.logger.debug(f"Command redone: {command.description}")
                return True
            
            # If redo failed, put it back
            self.redo_stack.append(command)
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to redo command: {e}")
            return False