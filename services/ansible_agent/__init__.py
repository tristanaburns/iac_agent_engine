from typing import Any, Callable, TypeVar

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])
"""Ansible Executor Service Package."""
