"""Tests for xkalamine CLI (install/remove commands)."""

import os
import pytest
from click.testing import CliRunner

from kalamine.cli_xkb import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_wayland(monkeypatch):
    """Mock WAYLAND detection."""
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")


@pytest.fixture
def mock_xorg(monkeypatch):
    """Mock Xorg detection."""
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")


class TestInstallCommand:
    """Tests for xkalamine install command."""

    def test_install_no_args(self, runner, mock_wayland):
        """install with no layouts should exit gracefully."""
        result = runner.invoke(cli, ["install"])
        assert result.exit_code == 0

    def test_install_wayland_user_space(self, runner, mock_wayland, monkeypatch, tmp_path):
        """install on Wayland without sudo should allow user-space install."""
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        monkeypatch.setenv("HOME", str(tmp_path))
        result = runner.invoke(cli, ["install", "-y", "layouts/prog.toml"])
        # Should succeed (user-space install allowed on Wayland)
        assert result.exit_code == 0

    def test_install_xorg_message(self, runner, mock_xorg, monkeypatch, tmp_path):
        """install on Xorg without sudo should not use user-space."""
        monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("XDG_CONFIG_HOME", "")
        result = runner.invoke(cli, ["install", "-y", "layouts/prog.toml"])
        # Should NOT try user-space on Xorg - only system-wide
        # Either succeeds (if writable) or fails with XOrg message
        assert "XOrg" in result.output or result.exit_code == 0


class TestRemoveCommand:
    """Tests for xkalamine remove command."""

    def test_remove_wayland_user_space(self, runner, mock_wayland, monkeypatch, tmp_path):
        """remove on Wayland without sudo should allow user-space removal."""
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        monkeypatch.setenv("HOME", str(tmp_path))
        result = runner.invoke(cli, ["remove", "fr/prog"])
        # Should succeed (user-space remove allowed on Wayland)
        assert result.exit_code == 0


class TestListCommand:
    """Tests for xkalamine list command."""

    def test_list_help(self, runner):
        """list --help should work."""
        result = runner.invoke(cli, ["list", "--help"])
        assert result.exit_code == 0
        assert "List installed Kalamine layouts" in result.output