from unittest.mock import (
    Mock,
    call,
    patch,
)

import pytest

from homebrew_releaser import app
from homebrew_releaser.app import App


def configure_github_responses(mock_request, include_matrix_assets=False):
    assets = []
    if include_matrix_assets:
        targets = ('darwin-amd64', 'darwin-arm64', 'linux-amd64', 'linux-arm64')
        for asset_id, target in enumerate(targets, start=1):
            assets.append(
                {
                    'id': asset_id,
                    'url': (
                        f'https://api.github.com/repos/{app.GITHUB_OWNER}/{app.GITHUB_REPO}/releases/assets/{asset_id}'
                    ),
                    'browser_download_url': (
                        f'https://github.com/{app.GITHUB_OWNER}/{app.GITHUB_REPO}/releases/download/v1.0.0/'
                        f'{app.GITHUB_REPO}-1.0.0-{target}.tar.gz'
                    ),
                }
            )

    mock_request.return_value.json.side_effect = [
        {'private': False, 'name': app.GITHUB_REPO},
        {'id': 1, 'tag_name': 'v1.0.0', 'assets': assets},
    ]


@patch('homebrew_releaser.app.SKIP_COMMIT', True)
@patch('homebrew_releaser.app.HOMEBREW_TAP', '123')
@patch('woodchips.get')
@patch('homebrew_releaser.git.Git.setup')
@patch('homebrew_releaser.git.Git.add')
@patch('homebrew_releaser.git.Git.commit')
@patch('homebrew_releaser.git.Git.push')
@patch('homebrew_releaser.utils.Utils.write_file')
@patch('homebrew_releaser.formula.Formula.generate_formula_data')
@patch('homebrew_releaser.checksum.Checksum.get_checksum', return_value=('123', 'mock-repo'))
@patch('homebrew_releaser.app.App.download_archive')
@patch('homebrew_releaser.utils.Utils.make_github_get_request')
@patch('homebrew_releaser.app.App.check_required_env_variables')
def test_run_github_action_skip_commit(
    mock_check_env_variables,
    mock_make_github_get_request,
    mock_download_archive,
    mock_get_checksum,
    mock_generate_formula,
    mock_write_file,
    mock_push_formula,
    mock_commit_formula,
    mock_add_formula,
    mock_setup_git,
    mock_logger,
):
    configure_github_responses(mock_make_github_get_request)
    App.run_github_action()

    # TODO: Assert these `called_with` eventually
    mock_logger.assert_called()
    mock_check_env_variables.assert_called_once()
    assert mock_make_github_get_request.call_count == 2
    mock_download_archive.call_count == 2
    mock_get_checksum.call_count == 2
    mock_generate_formula.assert_called_once()
    mock_write_file.call_count == 2
    mock_setup_git.assert_called_once()
    mock_add_formula.assert_called_once()
    mock_commit_formula.assert_called_once()
    mock_push_formula.assert_not_called()


@patch('homebrew_releaser.app.HOMEBREW_TAP', '123')
@patch('homebrew_releaser.checksum.Checksum.upload_checksum_file')
@patch('woodchips.get')
@patch('homebrew_releaser.git.Git.setup')
@patch('homebrew_releaser.git.Git.add')
@patch('homebrew_releaser.git.Git.commit')
@patch('homebrew_releaser.git.Git.push')
@patch('homebrew_releaser.utils.Utils.write_file')
@patch('homebrew_releaser.formula.Formula.generate_formula_data')
@patch('homebrew_releaser.checksum.Checksum.get_checksum', return_value=('123', 'mock-repo'))
@patch('homebrew_releaser.app.App.download_archive')
@patch('homebrew_releaser.utils.Utils.make_github_get_request')
@patch('homebrew_releaser.app.App.check_required_env_variables')
def test_run_github_action(
    mock_check_env_variables,
    mock_make_github_get_request,
    mock_download_archive,
    mock_get_checksum,
    mock_generate_formula,
    mock_write_file,
    mock_push_formula,
    mock_commit_formula,
    mock_add_formula,
    mock_setup_git,
    mock_logger,
    mock_upload_checksum_file,
):
    configure_github_responses(mock_make_github_get_request)
    App.run_github_action()

    # TODO: Assert these `called_with` eventually
    mock_logger.assert_called()
    mock_check_env_variables.assert_called_once()
    assert mock_make_github_get_request.call_count == 2
    mock_download_archive.call_count == 2
    mock_get_checksum.call_count == 2
    mock_generate_formula.assert_called_once()
    mock_write_file.call_count == 2
    mock_setup_git.assert_called_once()
    mock_add_formula.assert_called_once()
    mock_commit_formula.assert_called_once()
    mock_push_formula.assert_called_once()


@patch('homebrew_releaser.app.SKIP_COMMIT', False)
@patch('homebrew_releaser.app.VERSION', 'v1.2.3')
@patch('homebrew_releaser.app.GITHUB_OWNER', 'example-owner')
@patch('homebrew_releaser.app.GITHUB_REPO', 'example-project')
@patch('homebrew_releaser.app.HOMEBREW_OWNER', 'example-owner')
@patch('homebrew_releaser.app.HOMEBREW_TAP', 'example-tap')
@patch('homebrew_releaser.app.TARGET_DARWIN_AMD64', True)
@patch('homebrew_releaser.checksum.Checksum.upload_checksum_file')
@patch('woodchips.get')
@patch('homebrew_releaser.git.Git.setup')
@patch('homebrew_releaser.git.Git.add')
@patch('homebrew_releaser.git.Git.commit')
@patch('homebrew_releaser.git.Git.push')
@patch('homebrew_releaser.utils.Utils.write_file')
@patch('homebrew_releaser.formula.Formula.generate_formula_data')
@patch('homebrew_releaser.checksum.Checksum.get_checksum', return_value='selected-checksum')
@patch('homebrew_releaser.app.App.download_archive')
@patch('homebrew_releaser.utils.Utils.make_github_get_request')
@patch('homebrew_releaser.app.App.check_required_env_variables')
def test_run_github_action_selects_requested_release_for_private_assets(
    mock_check_env_variables,
    mock_make_github_get_request,
    mock_download_archive,
    mock_get_checksum,
    mock_generate_formula,
    mock_write_file,
    mock_push_formula,
    mock_commit_formula,
    mock_add_formula,
    mock_setup_git,
    mock_logger,
    mock_upload_checksum_file,
):
    repository_url = 'https://api.github.com/repos/example-owner/example-project'
    selected_release_url = f'{repository_url}/releases/tags/v1.2.3'
    latest_release_url = f'{repository_url}/releases/latest'
    selected_asset_api_url = f'{repository_url}/releases/assets/1231'
    selected_asset_url = (
        'https://github.com/example-owner/example-project/releases/download/'
        'v1.2.3/example-project-1.2.3-darwin-amd64.tar.gz'
    )
    latest_asset_url = (
        'https://github.com/example-owner/example-project/releases/download/'
        'v2.0.0/example-project-2.0.0-darwin-amd64.tar.gz'
    )

    repository = {'private': True, 'name': 'example-project'}
    selected_release = {
        'id': 123,
        'tag_name': 'v1.2.3',
        'assets': [{'id': 1231, 'url': selected_asset_api_url, 'browser_download_url': selected_asset_url}],
    }
    latest_release = {
        'id': 200,
        'tag_name': 'v2.0.0',
        'assets': [
            {'id': 2001, 'url': f'{repository_url}/releases/assets/2001', 'browser_download_url': latest_asset_url}
        ],
    }

    repository_response = Mock()
    repository_response.json.return_value = repository
    selected_release_response = Mock()
    selected_release_response.json.return_value = selected_release
    latest_release_response = Mock()
    latest_release_response.json.return_value = latest_release
    responses = {
        repository_url: repository_response,
        selected_release_url: selected_release_response,
        latest_release_url: latest_release_response,
    }
    mock_make_github_get_request.side_effect = lambda url, **kwargs: responses[url]

    App.run_github_action()

    assert mock_make_github_get_request.call_args_list == [
        call(url=repository_url),
        call(url=selected_release_url),
    ]
    mock_download_archive.assert_any_call(f'{repository_url}/tarball/v1.2.3', False)
    mock_download_archive.assert_any_call(f'{repository_url}/zipball/v1.2.3', False)
    mock_download_archive.assert_any_call(selected_asset_api_url, True)

    formula_args = mock_generate_formula.call_args.args
    assert formula_args[5] == f'{repository_url}/tarball/v1.2.3'
    assert formula_args[11] == '1.2.3'
    assert {
        'example-project-1.2.3-darwin-amd64.tar.gz': {
            'checksum': 'selected-checksum',
            'url': selected_asset_url,
        }
    } in formula_args[3]
    mock_upload_checksum_file.assert_called_once_with(selected_release)
    mock_push_formula.assert_called_once_with('example-tap', 'example-owner')


@pytest.mark.parametrize('version', [None, ''])
def test_run_github_action_uses_latest_release_when_version_is_empty(version, monkeypatch):
    repository_url = 'https://api.github.com/repos/example-owner/example-project'
    repository_response = Mock()
    repository_response.json.return_value = {'private': False, 'name': 'example-project'}
    release_response = Mock()
    release = {'id': 200, 'tag_name': 'v2.0.0', 'assets': []}
    release_response.json.return_value = release
    mock_make_github_get_request = Mock(side_effect=[repository_response, release_response])
    mock_download_archive = Mock(return_value='mock-archive.tar.gz')
    mock_generate_formula = Mock()
    mock_upload_checksum_file = Mock()

    monkeypatch.setattr(app, 'VERSION', version)
    monkeypatch.setattr(app, 'GITHUB_OWNER', 'example-owner')
    monkeypatch.setattr(app, 'GITHUB_REPO', 'example-project')
    monkeypatch.setattr(app, 'HOMEBREW_OWNER', 'example-owner')
    monkeypatch.setattr(app, 'HOMEBREW_TAP', 'example-tap')
    monkeypatch.setattr(app, 'SKIP_COMMIT', False)
    monkeypatch.setattr(app, 'TARGET_DARWIN_AMD64', False)
    monkeypatch.setattr(app, 'TARGET_DARWIN_ARM64', False)
    monkeypatch.setattr(app, 'TARGET_LINUX_AMD64', False)
    monkeypatch.setattr(app, 'TARGET_LINUX_ARM64', False)
    monkeypatch.setattr(app.App, 'setup_logger', Mock())
    monkeypatch.setattr(app.App, 'check_required_env_variables', Mock())
    monkeypatch.setattr(app.App, 'download_archive', mock_download_archive)
    monkeypatch.setattr(app.Utils, 'make_github_get_request', mock_make_github_get_request)
    monkeypatch.setattr(app.Utils, 'write_file', Mock())
    monkeypatch.setattr(app.Checksum, 'get_checksum', Mock(return_value='checksum'))
    monkeypatch.setattr(app.Checksum, 'upload_checksum_file', mock_upload_checksum_file)
    monkeypatch.setattr(app.Formula, 'generate_formula_data', mock_generate_formula)
    monkeypatch.setattr(app.Git, 'setup', Mock())
    monkeypatch.setattr(app.Git, 'add', Mock())
    monkeypatch.setattr(app.Git, 'commit', Mock())
    monkeypatch.setattr(app.Git, 'push', Mock())
    monkeypatch.setattr(app.woodchips, 'get', Mock(return_value=Mock()))

    App.run_github_action()

    assert mock_make_github_get_request.call_args_list == [
        call(url=repository_url),
        call(url=f'{repository_url}/releases/latest'),
    ]
    formula_args = mock_generate_formula.call_args.args
    assert formula_args[5] == 'https://github.com/example-owner/example-project/archive/refs/tags/v2.0.0.tar.gz'
    assert formula_args[11] is None
    mock_upload_checksum_file.assert_called_once_with(release)


def test_run_github_action_does_not_fallback_when_requested_release_is_missing(monkeypatch):
    repository_url = 'https://api.github.com/repos/example-owner/example-project'
    selected_release_url = f'{repository_url}/releases/tags/v9.9.9'
    latest_release_url = f'{repository_url}/releases/latest'
    repository_response = Mock()
    repository_response.json.return_value = {'private': False, 'name': 'example-project'}
    latest_release_response = Mock()
    latest_release_response.json.return_value = {'id': 200, 'tag_name': 'v2.0.0', 'assets': []}

    def make_github_get_request(url, **kwargs):
        if url == repository_url:
            return repository_response
        if url == selected_release_url:
            raise SystemExit('release not found')
        if url == latest_release_url:
            return latest_release_response
        raise AssertionError(f'Unexpected GitHub request: {url}')

    mock_make_github_get_request = Mock(side_effect=make_github_get_request)
    mock_download_archive = Mock()
    mock_get_checksum = Mock()
    mock_generate_formula = Mock()
    mock_write_file = Mock()
    mock_upload_checksum_file = Mock()
    mock_git_setup = Mock()
    mock_git_add = Mock()
    mock_git_commit = Mock()
    mock_git_push = Mock()

    monkeypatch.setattr(app, 'VERSION', 'v9.9.9')
    monkeypatch.setattr(app, 'GITHUB_OWNER', 'example-owner')
    monkeypatch.setattr(app, 'GITHUB_REPO', 'example-project')
    monkeypatch.setattr(app, 'HOMEBREW_OWNER', 'example-owner')
    monkeypatch.setattr(app, 'HOMEBREW_TAP', 'example-tap')
    monkeypatch.setattr(app, 'SKIP_COMMIT', False)
    monkeypatch.setattr(app.App, 'setup_logger', Mock())
    monkeypatch.setattr(app.App, 'check_required_env_variables', Mock())
    monkeypatch.setattr(app.App, 'download_archive', mock_download_archive)
    monkeypatch.setattr(app.Utils, 'make_github_get_request', mock_make_github_get_request)
    monkeypatch.setattr(app.Utils, 'write_file', mock_write_file)
    monkeypatch.setattr(app.Checksum, 'get_checksum', mock_get_checksum)
    monkeypatch.setattr(app.Checksum, 'upload_checksum_file', mock_upload_checksum_file)
    monkeypatch.setattr(app.Formula, 'generate_formula_data', mock_generate_formula)
    monkeypatch.setattr(app.Git, 'setup', mock_git_setup)
    monkeypatch.setattr(app.Git, 'add', mock_git_add)
    monkeypatch.setattr(app.Git, 'commit', mock_git_commit)
    monkeypatch.setattr(app.Git, 'push', mock_git_push)
    monkeypatch.setattr(app.woodchips, 'get', Mock(return_value=Mock()))

    with pytest.raises(SystemExit, match='release not found'):
        App.run_github_action()

    assert mock_make_github_get_request.call_args_list == [
        call(url=repository_url),
        call(url=selected_release_url),
    ]
    mock_git_setup.assert_called_once()
    mock_download_archive.assert_not_called()
    mock_get_checksum.assert_not_called()
    mock_generate_formula.assert_not_called()
    mock_write_file.assert_not_called()
    mock_upload_checksum_file.assert_not_called()
    mock_git_add.assert_not_called()
    mock_git_commit.assert_not_called()
    mock_git_push.assert_not_called()


@patch('homebrew_releaser.app.HOMEBREW_TAP', '123')
@patch('homebrew_releaser.app.UPDATE_README_TABLE', True)
@patch('homebrew_releaser.readme_updater.ReadmeUpdater.update_readme')
@patch('homebrew_releaser.checksum.Checksum.upload_checksum_file')
@patch('woodchips.get')
@patch('homebrew_releaser.git.Git.setup')
@patch('homebrew_releaser.git.Git.add')
@patch('homebrew_releaser.git.Git.commit')
@patch('homebrew_releaser.git.Git.push')
@patch('homebrew_releaser.utils.Utils.write_file')
@patch('homebrew_releaser.formula.Formula.generate_formula_data')
@patch('homebrew_releaser.checksum.Checksum.get_checksum', return_value=('123', 'mock-repo'))
@patch('homebrew_releaser.app.App.download_archive')
@patch('homebrew_releaser.utils.Utils.make_github_get_request')
@patch('homebrew_releaser.app.App.check_required_env_variables')
def test_run_github_action_update_readme(
    mock_check_env_variables,
    mock_make_github_get_request,
    mock_download_archive,
    mock_get_checksum,
    mock_generate_formula,
    mock_write_file,
    mock_push_formula,
    mock_commit_formula,
    mock_add_formula,
    mock_setup_git,
    mock_logger,
    mock_upload_checksum_file,
    mock_update_readme,
):
    configure_github_responses(mock_make_github_get_request)
    App.run_github_action()

    # TODO: Assert these `called_with` eventually
    mock_logger.assert_called()
    mock_check_env_variables.assert_called_once()
    assert mock_make_github_get_request.call_count == 2
    mock_download_archive.call_count == 2
    mock_get_checksum.call_count == 2
    mock_generate_formula.assert_called_once()
    mock_write_file.call_count == 2
    mock_setup_git.assert_called_once()
    mock_add_formula.assert_called_once()
    mock_commit_formula.assert_called_once()
    mock_push_formula.assert_called_once()
    mock_update_readme.assert_called_once()


@patch('homebrew_releaser.app.HOMEBREW_TAP', '123')
@patch('homebrew_releaser.app.TARGET_DARWIN_AMD64', True)
@patch('homebrew_releaser.app.TARGET_DARWIN_ARM64', True)
@patch('homebrew_releaser.app.TARGET_LINUX_AMD64', True)
@patch('homebrew_releaser.app.TARGET_LINUX_ARM64', True)
@patch('homebrew_releaser.checksum.Checksum.upload_checksum_file')
@patch('woodchips.get')
@patch('homebrew_releaser.git.Git.setup')
@patch('homebrew_releaser.git.Git.add')
@patch('homebrew_releaser.git.Git.commit')
@patch('homebrew_releaser.git.Git.push')
@patch('homebrew_releaser.utils.Utils.write_file')
@patch('homebrew_releaser.formula.Formula.generate_formula_data')
@patch('homebrew_releaser.checksum.Checksum.get_checksum', return_value=('123', 'mock-repo'))
@patch('homebrew_releaser.app.App.download_archive')
@patch('homebrew_releaser.utils.Utils.make_github_get_request')
@patch('homebrew_releaser.app.App.check_required_env_variables')
def test_run_github_action_target_matrix(
    mock_check_env_variables,
    mock_make_github_get_request,
    mock_download_archive,
    mock_get_checksum,
    mock_generate_formula,
    mock_write_file,
    mock_push_formula,
    mock_commit_formula,
    mock_add_formula,
    mock_setup_git,
    mock_logger,
    mock_upload_checksum_file,
):
    """Tests that we append checksum URLs to the list when the user passes matrix targets."""
    configure_github_responses(mock_make_github_get_request, include_matrix_assets=True)
    App.run_github_action()

    # TODO: Assert these `called_with` eventually
    mock_logger.assert_called()
    mock_check_env_variables.assert_called_once()
    assert mock_make_github_get_request.call_count == 2
    mock_download_archive.call_count == 2
    mock_get_checksum.call_count == 2
    mock_generate_formula.assert_called_once()
    mock_write_file.call_count == 2
    mock_setup_git.assert_called_once()
    mock_add_formula.assert_called_once()
    mock_commit_formula.assert_called_once()
    mock_push_formula.assert_called_once()


@patch('woodchips.Logger')
def test_setup_logger(mock_logger):
    App.setup_logger()

    mock_logger.assert_called_once()


@patch('homebrew_releaser.app.GITHUB_TOKEN', '123')
@patch('homebrew_releaser.app.HOMEBREW_OWNER', 'Justintime50')
@patch('homebrew_releaser.app.HOMEBREW_TAP', 'homebrew-formulas')
@patch('homebrew_releaser.app.INSTALL', 'bin.install "src/my-script.sh" => "my-script"')
@patch('sys.exit')
def test_check_required_env_variables(mock_system_exit):
    App.check_required_env_variables()

    mock_system_exit.assert_not_called()


@patch('sys.exit')
def test_check_required_env_variables_missing_env_variable(mock_system_exit):
    with pytest.raises(SystemExit) as error:
        App.check_required_env_variables()
        mock_system_exit.assert_called_once()

    assert (
        str(error.value)
        == 'You must provide all necessary environment variables. Please reference the Homebrew Releaser documentation.'
    )


@patch('homebrew_releaser.utils.Utils.write_file')
@patch('homebrew_releaser.utils.Utils.make_github_get_request')
def test_download_public_archive(mock_make_github_get_request, mock_write_file):
    url = 'https://github.com/repos/Justintime50/homebrew-releaser/archive/refs/tags/v0.1.0.tar.gz'
    App.download_archive(url, True)

    mock_make_github_get_request.assert_called_once_with(url=url, stream=True)
    mock_write_file.assert_called_once()  # TODO: Assert `called_with` here instead


@patch('homebrew_releaser.utils.Utils.write_file')
@patch('homebrew_releaser.utils.Utils.make_github_get_request')
def test_download_private_archive(mock_make_github_get_request, mock_write_file):
    url = 'https://api.github.com/repos/Justintime50/homebrew-releaser/tarball/v0.1.0'
    App.download_archive(url, False)

    mock_make_github_get_request.assert_called_once_with(url=url, stream=False)
    mock_write_file.assert_called_once()  # TODO: Assert `called_with` here instead
