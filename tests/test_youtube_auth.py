import pytest
from unittest.mock import patch, MagicMock, ANY
from processes.youtube_utils import get_authenticated_service, _read_token_data, _write_token_data
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request # Needed for credentials.refresh() in actual code
import json
import os

# Mock the googleapiclient.discovery.build function
@pytest.fixture
def mock_google_build():
    with patch("processes.youtube_utils.googleapiclient.discovery.build") as mock_build:
        yield mock_build

# Mock the google_auth_oauthlib.flow.InstalledAppFlow class
@pytest.fixture
def mock_installed_app_flow():
    with patch("processes.youtube_utils.InstalledAppFlow") as mock_flow_cls:
        # Configure mock flow instance
        mock_flow_instance = MagicMock()
        mock_flow_cls.from_client_secrets_file.return_value = mock_flow_instance
        
        # Configure mock credentials returned by run_local_server
        mock_credentials = MagicMock()
        mock_credentials.valid = True
        mock_credentials.expired = False
        mock_credentials.to_dict.return_value = {
            "token": "new_token_data",
            "refresh_token": "mock_refresh_token",
            "client_id": "mock_client_id",
            "client_secret": "mock_client_secret",
            "scopes": ["https://www.googleapis.com/auth/youtube.force-ssl"]
        }
        mock_credentials.to_json.return_value = json.dumps(mock_credentials.to_dict.return_value)
        mock_flow_instance.run_local_server.return_value = mock_credentials
        
        yield mock_flow_cls

@pytest.fixture
def mock_token_file_ops():
    with patch("processes.youtube_utils._read_token_data") as mock_read, \
         patch("processes.youtube_utils._write_token_data") as mock_write:
        yield mock_read, mock_write

def test_get_authenticated_service_new_channel(mock_token_file_ops, mock_google_build, mock_installed_app_flow):
    mock_read, mock_write = mock_token_file_ops
    mock_read.return_value = {} # Simulate no existing tokens
    
    channel_id = "NEW_CHANNEL_ID"
    service = get_authenticated_service(target_channel_id=channel_id)
    
    mock_installed_app_flow.from_client_secrets_file.assert_called_once_with(
        "client_secret.json", ANY
    )
    mock_installed_app_flow.from_client_secrets_file.return_value.run_local_server.assert_called_once_with(port=8080)
    
    mock_write.assert_called_once()
    args, kwargs = mock_write.call_args
    # Check that the dictionary passed to _write_token_data contains the new token
    assert channel_id in args[0]
    expected_token_data = mock_installed_app_flow.from_client_secrets_file.return_value.run_local_server.return_value.to_dict.return_value
    assert json.loads(args[0][channel_id]) == expected_token_data
    
    mock_google_build.assert_called_once()
    _, build_kwargs = mock_google_build.call_args
    assert isinstance(build_kwargs["credentials"], MagicMock) # Can only check for MagicMock now

def test_get_authenticated_service_existing_valid_channel(mock_token_file_ops, mock_google_build, mock_installed_app_flow):
    mock_read, mock_write = mock_token_file_ops
    channel_id = "EXISTING_CHANNEL_ID"
    existing_token_data = {
        "token": "existing_valid_token",
        "refresh_token": "mock_refresh_token",
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
        "scopes": ["https://www.googleapis.com/auth/youtube.force-ssl"]
    }
    mock_read.return_value = {channel_id: existing_token_data}
    
    mock_credentials = MagicMock()
    mock_credentials.valid = True
    mock_credentials.expired = False
    mock_credentials.to_json.return_value = json.dumps(existing_token_data)
    mock_credentials.to_dict.return_value = existing_token_data # Set explicit dict for to_dict()

    with patch("processes.youtube_utils.Credentials.from_authorized_user_info", return_value=mock_credentials):
        service = get_authenticated_service(target_channel_id=channel_id)
        
        mock_installed_app_flow.from_client_secrets_file.assert_not_called()
        mock_write.assert_not_called()
        
        mock_google_build.assert_called_once()
        _, build_kwargs = mock_google_build.call_args
        assert isinstance(build_kwargs["credentials"], MagicMock) # Can only check for MagicMock now
        assert build_kwargs["credentials"].to_dict.return_value == existing_token_data


def test_get_authenticated_service_existing_expired_channel(mock_token_file_ops, mock_google_build, mock_installed_app_flow):
    mock_read, mock_write = mock_token_file_ops
    channel_id = "EXPIRED_CHANNEL_ID"
    expired_token_data = {
        "token": "expired_token",
        "refresh_token": "a_refresh_token",
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
        "scopes": ["https://www.googleapis.com/auth/youtube.force-ssl"]
    }
    mock_read.return_value = {channel_id: expired_token_data}
    
    mock_expired_credentials = MagicMock()
    mock_expired_credentials.valid = False
    mock_expired_credentials.expired = True
    mock_expired_credentials.refresh_token = "a_refresh_token"
    refreshed_token_dict = {
        "token": "refreshed_token",
        "refresh_token": "a_refresh_token",
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
        "scopes": ["https://www.googleapis.com/auth/youtube.force-ssl"]
    }
    mock_expired_credentials.to_json.return_value = json.dumps(refreshed_token_dict)
    mock_expired_credentials.to_dict.return_value = refreshed_token_dict
    
    with patch("processes.youtube_utils.Credentials.from_authorized_user_info", return_value=mock_expired_credentials), \
         patch("processes.youtube_utils.Request") as mock_request:
        mock_expired_credentials.refresh = MagicMock()
        mock_expired_credentials.refresh.return_value = None

        service = get_authenticated_service(target_channel_id=channel_id)
        
        mock_expired_credentials.refresh.assert_called_once_with(mock_request.return_value)
        mock_write.assert_called_once()
        args, kwargs = mock_write.call_args
        assert channel_id in args[0]
        assert json.loads(args[0][channel_id]) == refreshed_token_dict
        
        mock_google_build.assert_called_once()
        _, build_kwargs = mock_google_build.call_args
        assert isinstance(build_kwargs["credentials"], MagicMock) # Can only check for MagicMock now
