"""Queue primitives for music playback."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(slots=True)
class Track:
    """A playable track and its metadata."""

    title: str
    url: str
    webpage_url: str
    duration: int
    thumbnail: str | None
    requested_by: str
    source: str


class Queue:
    """Simple FIFO queue for guild music playback."""

    def __init__(self) -> None:
        self._queue: deque[Track] = deque()
        self.current: Track | None = None

    def add(self, track: Track) -> int:
        """Add a track to the queue and return its 1-based queued position."""
        self._queue.append(track)
        return len(self._queue)

    def next(self) -> Track | None:
        """Pop the next track and set it as the current track."""
        if self._queue:
            self.current = self._queue.popleft()
            return self.current
        self.current = None
        return None

    def clear(self) -> None:
        """Clear queued and current tracks."""
        self._queue.clear()
        self.current = None

    def list(self) -> list[Track]:
        """Return queued tracks as a list."""
        return list(self._queue)

    def is_empty(self) -> bool:
        """Return whether the queue is empty."""
        return len(self._queue) == 0

    def __len__(self) -> int:
        return len(self._queue)
