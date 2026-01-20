# Agent Change Log

This file tracks changes made to the repository by automated agents.

## 2025-09-27
- Initialized repository structure for vectorless RAG service.
- Added initial FastAPI service, indexing, retrieval, storage, observability, and configuration modules.
- Added tests, CI, Docker, compose stack, and documentation.
- Added scripts and build tooling (Makefile, pyproject, workflows).
- Fixed ruff lint issues (dependency injection, import ordering, line lengths, unused imports).
- Adjusted FastAPI dependency wiring and file upload annotations for lint compliance.
- Sorted imports in storage database module per ruff.
- Relaxed mypy configuration to ignore missing imports and updated interface typing.
- Fixed filename typing in document upload handler to satisfy mypy.
- Declared filename type upfront for document upload handler typing.
- Ensured text payload defaulting avoids Optional assignment in upload handler.
