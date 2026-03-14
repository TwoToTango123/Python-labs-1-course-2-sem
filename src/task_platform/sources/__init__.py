"""Реализации источников задач."""

from .api_stub_source import ApiStubTaskSource
from .file_source import FileTaskSource
from .generator_source import GeneratorTaskSource

__all__ = ["FileTaskSource", "GeneratorTaskSource", "ApiStubTaskSource"]
