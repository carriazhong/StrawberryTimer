"""Strawberry Timer - Todo integration module for future extensibility."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


class TodoProvider(ABC):
    """Abstract interface for Todo providers.

    Implement this interface to connect Strawberry Timer with different
    Todo backends (local files, web services, etc.).
    """

    @abstractmethod
    def get_todos(self, include_completed: bool = True) -> List[Dict[str, Any]]:
        """Get list of Todo items.

        Args:
            include_completed: Whether to include completed Todos.

        Returns:
            List of Todo dictionaries.
        """
        pass

    @abstractmethod
    def get_todo_by_id(self, todo_id: int) -> Dict[str, Any]:
        """Get a specific Todo item by ID.

        Args:
            todo_id: Todo item ID.

        Returns:
            Todo dictionary.

        Raises:
            KeyError: If Todo not found.
        """
        pass

    @abstractmethod
    def mark_completed(self, todo_id: int) -> None:
        """Mark a Todo item as completed.

        Args:
            todo_id: Todo item ID.
        """
        pass

    @abstractmethod
    def add_todo(self, todo: Dict[str, Any]) -> int:
        """Add a new Todo item.

        Args:
            todo: Todo dictionary with at least 'title'.

        Returns:
            ID of created Todo.
        """
        pass


@dataclass
class TodoItem:
    """Todo item data structure."""
    id: int
    title: str
    completed: bool = False
    description: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "description": self.description,
            "tags": self.tags,
        }


class InMemoryTodoProvider(TodoProvider):
    """In-memory Todo provider for testing and standalone use.

    This is the default provider when no external Todo service is configured.
    """

    def __init__(self):
        """Initialize in-memory Todo storage."""
        self._todos: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def get_todos(self, include_completed: bool = True) -> List[Dict[str, Any]]:
        """Get list of Todo items.

        Args:
            include_completed: Whether to include completed Todos.

        Returns:
            List of Todo dictionaries.
        """
        todos = list(self._todos.values())
        if not include_completed:
            todos = [t for t in todos if not t["completed"]]
        return todos

    def get_todo_by_id(self, todo_id: int) -> Dict[str, Any]:
        """Get a specific Todo item by ID.

        Args:
            todo_id: Todo item ID.

        Returns:
            Todo dictionary.

        Raises:
            KeyError: If Todo not found.
        """
        if todo_id not in self._todos:
            raise KeyError(f"Todo not found: {todo_id}")
        return self._todos[todo_id].copy()

    def mark_completed(self, todo_id: int) -> None:
        """Mark a Todo item as completed.

        Args:
            todo_id: Todo item ID.

        Raises:
            KeyError: If Todo not found.
        """
        if todo_id not in self._todos:
            raise KeyError(f"Todo not found: {todo_id}")
        self._todos[todo_id]["completed"] = True

    def add_todo(self, todo: Dict[str, Any]) -> int:
        """Add a new Todo item.

        Args:
            todo: Todo dictionary with at least 'title'.

        Returns:
            ID of created Todo.
        """
        todo_id = self._next_id
        self._next_id += 1

        self._todos[todo_id] = {
            "id": todo_id,
            "title": todo.get("title", "Untitled"),
            "completed": todo.get("completed", False),
            "description": todo.get("description"),
            "tags": todo.get("tags", []),
        }
        return todo_id


class TodoIntegration:
    """Manages Todo provider integration for the timer.

    Allows switching between different Todo backends and provides
    a unified interface for the timer to interact with Todos.
    """

    def __init__(self, provider: Optional[TodoProvider] = None):
        """Initialize Todo integration.

        Args:
            provider: Todo provider to use. If None, uses InMemoryTodoProvider.
        """
        self._provider = provider or InMemoryTodoProvider()
        self._providers: Dict[str, TodoProvider] = {
            "default": self._provider,
        }

    # ==================== Provider Management ====================

    def register_provider(self, name: str, provider: TodoProvider) -> None:
        """Register a new Todo provider.

        Args:
            name: Unique name for this provider.
            provider: TodoProvider instance.
        """
        self._providers[name] = provider

    def set_active_provider(self, name: str) -> None:
        """Switch the active Todo provider.

        Args:
            name: Name of registered provider.

        Raises:
            ValueError: If provider not found.
        """
        if name not in self._providers:
            raise ValueError(f"Provider not found: {name}")
        self._provider = self._providers[name]

    @property
    def active_provider_name(self) -> str:
        """Get the name of the active provider."""
        for name, provider in self._providers.items():
            if provider is self._provider:
                return name
        return "unknown"

    def available_providers(self) -> List[str]:
        """Get list of registered provider names."""
        return list(self._providers.keys())

    # ==================== Todo Operations ====================

    def get_todos(self, include_completed: bool = True) -> List[Dict[str, Any]]:
        """Get Todos from active provider.

        Args:
            include_completed: Whether to include completed Todos.

        Returns:
            List of Todo dictionaries.
        """
        return self._provider.get_todos(include_completed)

    def get_todo_by_id(self, todo_id: int) -> Dict[str, Any]:
        """Get a specific Todo by ID.

        Args:
            todo_id: Todo item ID.

        Returns:
            Todo dictionary.
        """
        return self._provider.get_todo_by_id(todo_id)

    def mark_completed(self, todo_id: int) -> None:
        """Mark a Todo as completed.

        Args:
            todo_id: Todo item ID.
        """
        self._provider.mark_completed(todo_id)

    def search_todos(self, query: str) -> List[Dict[str, Any]]:
        """Search Todos by title.

        Args:
            query: Search query (case-insensitive).

        Returns:
            List of matching Todos.
        """
        todos = self._provider.get_todos()
        query_lower = query.lower()
        return [
            todo for todo in todos
            if query_lower in todo.get("title", "").lower()
        ]
