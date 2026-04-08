"""Test cases for Todo Integration module.

Tests the future extensibility for Todo list integration:
- Todo item selection
- Todo session association
- Todo provider interface (for multiple backends)
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime


# ==================== Test: Todo Provider Interface ====================

class TestTodoProviderInterface:
    """Test the abstract interface for Todo providers."""

    def test_todo_provider_has_required_methods(self, todo_provider):
        """TodoProvider must implement required methods."""
        assert hasattr(todo_provider, 'get_todos')
        assert hasattr(todo_provider, 'get_todo_by_id')
        assert hasattr(todo_provider, 'mark_completed')

    def test_get_todos_returns_list(self, todo_provider, sample_todos):
        """get_todos should return a list of todo items."""
        result = todo_provider.get_todos()
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)

    def test_get_todo_by_id(self, todo_provider, sample_todos):
        """get_todo_by_id should return specific todo item."""
        todo = todo_provider.get_todo_by_id(1)
        assert todo['id'] == 1
        assert todo['title'] == "Write documentation"

    def test_get_todo_by_id_not_found_raises_error(self, todo_provider):
        """get_todo_by_id should raise error for non-existent ID."""
        with pytest.raises(KeyError, match="Todo not found"):
            todo_provider.get_todo_by_id(999)

    def test_mark_completed_updates_todo(self, todo_provider, sample_todos):
        """mark_completed should update todo's completed status."""
        todo_provider.mark_completed(1)
        updated_todo = todo_provider.get_todo_by_id(1)
        assert updated_todo['completed'] is True


# ==================== Test: Todo-Timer Association ====================

class TestTodoTimerAssociation:
    """Test associating timer sessions with Todo items."""

    def test_attach_todo_to_timer_session(self, timer_engine, todo_integration):
        """Should be able to attach a Todo item to a timer session."""
        todo = {"id": 1, "title": "Write tests"}
        timer_engine.attach_todo(todo)
        assert timer_engine.active_todo == todo

    def test_timer_completion_updates_todo_progress(self, timer_engine, todo_integration):
        """Completing a timer session should update associated Todo progress."""
        todo = {"id": 1, "title": "Write tests", "completed": False}
        timer_engine.attach_todo(todo)
        timer_engine._complete_session()
        # Should track session completion

    def test_detach_todo_from_timer(self, timer_engine):
        """Should be able to detach Todo from timer."""
        todo = {"id": 1, "title": "Write tests"}
        timer_engine.attach_todo(todo)
        timer_engine.detach_todo()
        assert timer_engine.active_todo is None

    def test_session_history_with_todo(self, timer_engine, todo_integration):
        """Should track session history with associated Todo."""
        todo = {"id": 1, "title": "Write tests"}
        timer_engine.attach_todo(todo)
        timer_engine._complete_session()
        history = timer_engine.get_session_history()
        assert len(history) > 0
        assert history[0]['todo_id'] == 1


# ==================== Test: Multiple Todo Providers ====================

class TestMultipleTodoProviders:
    """Test switching between different Todo providers."""

    def test_register_todo_provider(self, todo_integration, mock_provider):
        """Should be able to register a new Todo provider."""
        todo_integration.register_provider("custom", mock_provider)
        assert "custom" in todo_integration.available_providers()

    def test_switch_active_provider(self, todo_integration, mock_provider):
        """Should be able to switch active Todo provider."""
        todo_integration.register_provider("custom", mock_provider)
        todo_integration.set_active_provider("custom")
        assert todo_integration.active_provider_name == "custom"

    def test_invalid_provider_raises_error(self, todo_integration):
        """Switching to invalid provider should raise error."""
        with pytest.raises(ValueError, match="Provider not found"):
            todo_integration.set_active_provider("nonexistent")


# ==================== Test: Todo Selection UI ====================

class TestTodoSelectionUI:
    """Test Todo selection in UI."""

    def test_display_todo_list(self, todo_integration, sample_todos):
        """UI should display list of available Todos."""
        todos = todo_integration.get_todos()
        assert len(todos) == 3
        assert todos[0]['title'] == "Write documentation"

    def test_select_todo_from_ui(self, todo_integration, timer_engine):
        """Should be able to select Todo from UI dropdown."""
        todos = todo_integration.get_todos()
        selected = todos[0]
        timer_engine.attach_todo(selected)
        assert timer_engine.active_todo == selected

    def test_filter_completed_todos(self, todo_integration):
        """Should be able to filter out completed Todos."""
        todos = todo_integration.get_todos(include_completed=False)
        assert all(not todo['completed'] for todo in todos)

    def test_search_todos_by_title(self, todo_integration):
        """Should be able to search Todos by title."""
        results = todo_integration.search_todos("documentation")
        assert "documentation" in results[0]['title'].lower()


# ==================== Fixtures ====================

@pytest.fixture
def mock_provider():
    """Create a mock Todo provider."""
    provider = Mock()
    provider.get_todos.return_value = [
        {"id": 1, "title": "Mock todo 1", "completed": False},
        {"id": 2, "title": "Mock todo 2", "completed": False},
    ]
    provider.get_todo_by_id = lambda id: {"id": id, "title": f"Mock todo {id}", "completed": False}
    provider.mark_completed = lambda id: None
    return provider


@pytest.fixture
def todo_provider(sample_todos):
    """Create a TodoProvider instance with sample data."""
    from src.todo.providers import InMemoryTodoProvider
    provider = InMemoryTodoProvider()
    for todo in sample_todos:
        provider.add_todo(todo)
    return provider


@pytest.fixture
def todo_integration(todo_provider):
    """Create a TodoIntegration instance."""
    from src.todo.integration import TodoIntegration
    return TodoIntegration(todo_provider)


@pytest.fixture
def timer_engine(timer_config):
    """Create a TimerEngine with Todo integration support."""
    from src.timer.engine import TimerEngine
    return TimerEngine(timer_config)
