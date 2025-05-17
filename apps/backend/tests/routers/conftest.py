"""
Shared fixtures for router tests
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.main import app
from fastapi import WebSocket


@pytest.fixture
def test_client():
    """Create a test client for FastAPI app testing"""
    return TestClient(app)


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket for testing"""
    return AsyncMock(spec=WebSocket) 