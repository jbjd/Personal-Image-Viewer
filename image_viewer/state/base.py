"""Base classes for states."""

from abc import abstractmethod


class StateBase:
    """Base class for states."""

    __slots__ = ()

    @abstractmethod
    def reset(self) -> None:
        """Reset state to default values."""
