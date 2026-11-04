import subprocess
from unittest.mock import (
    mock_open,
    patch,
)

import pytest
import requests

from homebrew_releaser.checksum import Checksum
from homebrew_releaser.constants import TIMEOUT


@patch('subprocess.check_output')
def test_get_checksum(mock_subprocess, mock_tar_filename):
    # TODO: Mock the subprocess better to ensure it does what it's supposed to
    Checksum.get_checksum(mock_tar_filename)

    mock_subprocess.assert_called_once_with(
        ['shasum', '-a', '256', mock_tar_filename],
        stdin=None,
        stderr=None,
        timeout=TIMEOUT,
    )


@patch('subprocess.check_output', side_effect=subprocess.TimeoutExpired(cmd='subprocess.check_output', timeout=0.1))
def test_get_checksum_subprocess_timeout(mock_subprocess, mock_tar_filename):
    with pytest.raises(SystemExit):
        Checksum.get_checksum(mock_tar_filename)


@patch(
    'subprocess.check_output', side_effect=subprocess.CalledProcessError(returncode=1, cmd='subprocess.check_output')
)
def test_get_checksum_process_error(mock_subprocess, mock_tar_filename):
    with pytest.raises(SystemExit):
        Checksum.get_checksum(mock_tar_filename)


@patch('homebrew_releaser.checksum.GITHUB_OWNER', 'example-owner')
@patch('homebrew_releaser.checksum.GITHUB_REPO', 'example-project')
@patch('requests.post')
@patch('homebrew_releaser.utils.Utils.make_github_get_request')
def test_upload_checksum_file(mock_make_github_get_request, mock_post_request):
    """Tests that we upload the checksum file to the provided release."""
    with patch('builtins.open', mock_open()):
        Checksum.upload_checksum_file({'id': 1, 'tag_name': 'v1.0.0'})

        mock_post_request.assert_called_once()
        assert mock_post_request.call_args.args[0] == (
            'https://uploads.github.com/repos/example-owner/example-project/releases/1/assets?name=checksum.txt'
        )
        mock_make_github_get_request.assert_not_called()


@patch('requests.post', side_effect=requests.exceptions.RequestException('mock-error'))
@patch('homebrew_releaser.utils.Utils.make_github_get_request')
def test_upload_checksum_file_error_on_upload(mock_make_github_get_request, mock_post_request):
    """Tests that we exit on error to upload checksum.txt file."""
    with patch('builtins.open', mock_open()):
        with pytest.raises(SystemExit) as error:
            Checksum.upload_checksum_file({'id': 1, 'tag_name': 'v1.0.0'})

            mock_post_request.assert_called_once()

    assert 'mock-error' == str(error.value)
