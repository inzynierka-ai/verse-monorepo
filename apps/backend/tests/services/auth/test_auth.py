import pytest
from unittest.mock import Mock, patch
from app.services.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user
)


class TestAuthFunctions:
    """Test cases for auth functions"""
    
    def test_get_password_hash(self):
        """Test password hashing functionality"""
        password = "test_password"
        hashed = get_password_hash(password)
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "test_user"}
        token = create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    @patch('app.services.auth.auth.get_user_by_username')
    @patch('app.services.auth.auth.verify_password')
    def test_authenticate_user_success(self, mock_verify_password, mock_get_user):
        """Test successful user authentication"""
        # Mock user object
        mock_user = Mock()
        mock_user.hashed_password = "hashed_password"
        
        mock_get_user.return_value = mock_user
        mock_verify_password.return_value = True
        
        mock_db = Mock()
        result = authenticate_user(mock_db, "test_user", "test_password")
        
        assert result == mock_user
        mock_get_user.assert_called_once_with(mock_db, "test_user")
        mock_verify_password.assert_called_once_with("test_password", "hashed_password")
    
    @patch('app.services.auth.auth.get_user_by_username')
    def test_authenticate_user_not_found(self, mock_get_user):
        """Test authentication with non-existent user"""
        mock_get_user.return_value = None
        
        mock_db = Mock()
        result = authenticate_user(mock_db, "nonexistent_user", "test_password")
        
        assert result is False
        mock_get_user.assert_called_once_with(mock_db, "nonexistent_user") 