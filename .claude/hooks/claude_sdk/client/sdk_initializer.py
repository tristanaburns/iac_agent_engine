"""Claude SDK client initialization following SOLID principles.

Single Responsibility: Only handles Claude SDK client initialization.
"""

import os
from pathlib import Path
from typing import Any, Optional


class SDKInitializer:
    """Initializes and configures Claude SDK client."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize with optional configuration path."""
        self.config_path = config_path
        self.client: Optional[Any] = None
        self.options: Optional[Any] = None
        self.is_available = self._check_sdk_availability()

    def _check_sdk_availability(self) -> bool:
        """Check if Claude SDK is available."""
        try:
            import claude_code_sdk  # noqa: F401

            return True
        except ImportError:
            return False

    def initialize(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-opus-20240229",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs,
    ) -> Optional[Any]:
        """Initialize Claude SDK client with configuration.

        Args:
            api_key: API key for Claude (defaults to env var)
            model: Model to use
            max_tokens: Maximum tokens for responses
            temperature: Temperature for generation
            **kwargs: Additional options

        Returns:
            Initialized Claude SDK client or None if not available
        """
        if not self.is_available:
            try:
                from operations.logging.logger import logger
            except (ImportError, ValueError):
                # Fallback if relative import fails
                import sys
                from pathlib import Path

                hooks_dir = Path(__file__).parent.parent.parent
                sys.path.insert(0, str(hooks_dir))
                from operations.logging.logger import logger

            logger.warning("Claude SDK not available - skipping initialization")
            return None

        try:
            from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient

            # Get API key from environment if not provided
            if api_key is None:
                api_key = os.environ.get("CLAUDE_API_KEY", "")

            if not api_key:
                try:
                    from operations.logging.logger import logger
                except (ImportError, ValueError):
                    import sys
                    from pathlib import Path

                    hooks_dir = Path(__file__).parent.parent.parent
                    sys.path.insert(0, str(hooks_dir))
                    from operations.logging.logger import logger

                logger.error("No Claude API key provided")
                return None

            # Create options
            self.options = ClaudeCodeOptions(  # type: ignore[call-arg]
                api_key=api_key,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            # Initialize client
            self.client = ClaudeSDKClient(self.options)  # type: ignore[assignment]

            try:
                from operations.logging.logger import logger
            except (ImportError, ValueError):
                import sys
                from pathlib import Path

                hooks_dir = Path(__file__).parent.parent.parent
                sys.path.insert(0, str(hooks_dir))
                from operations.logging.logger import logger

            logger.success(f"Claude SDK client initialized with model: {model}")

            return self.client

        except Exception as e:
            try:
                from operations.logging.logger import logger
            except (ImportError, ValueError):
                import sys
                from pathlib import Path

                hooks_dir = Path(__file__).parent.parent.parent
                sys.path.insert(0, str(hooks_dir))
                from operations.logging.logger import logger

            logger.exception(f"Failed to initialize Claude SDK: {e}")
            return None

    def get_client(self) -> Optional[Any]:
        """Get the initialized client.

        Returns:
            Claude SDK client or None if not initialized
        """
        return self.client

    def get_options(self) -> Optional[Any]:
        """Get the client options.

        Returns:
            Claude Code options or None if not initialized
        """
        return self.options

    def is_initialized(self) -> bool:
        """Check if client is initialized.

        Returns:
            True if client is initialized
        """
        return self.client is not None

    def shutdown(self) -> None:
        """Shutdown the client and cleanup resources."""
        if self.client:
            try:
                # Attempt to close client if method exists
                if hasattr(self.client, "close"):
                    self.client.close()
                elif hasattr(self.client, "shutdown"):
                    self.client.shutdown()
            except Exception as e:
                from operations.logging.logger import logger

                logger.warning(f"Error during client shutdown: {e}")
            finally:
                self.client = None
                self.options = None

    def configure_from_file(self, config_file: Path) -> bool:
        """Configure client from a JSON configuration file.

        Args:
            config_file: Path to configuration file

        Returns:
            True if configuration successful
        """
        if not config_file.exists():
            from operations.logging.logger import logger

            logger.error(f"Configuration file not found: {config_file}")
            return False

        try:
            import json

            with open(config_file, "r") as f:
                config = json.load(f)

            # Initialize with config
            self.initialize(**config)
            return True

        except Exception as e:
            from operations.logging.logger import logger

            logger.exception(f"Failed to load configuration: {e}")
            return False
