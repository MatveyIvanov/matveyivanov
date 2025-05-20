from typing import Protocol, TypeVar

T = TypeVar("T")


class IRingBuffer(Protocol[T]):
    async def put(self, value: T) -> bool:
        """
        Put a value to the ring buffer.

        :param value: Value to put
        :type value: T
        :return: True if successfull, False otherwise
        :rtype: bool
        """
        ...

    async def all(self) -> list[T]:
        """
        Read all items from the buffer.
        Returns items in the order they were written.

        :return: Values in the buffer
        :rtype: list[T]
        """
        ...

    async def latest(self, n: int = 1) -> list[T]:
        """
        Read the n most recent items from the buffer.

        :param n: Number items to return
        :type n: int

        :return: List containing at most n most recent items
        :rtype: list[T]
        """
        ...

    async def clear(self) -> bool:
        """
        Clear the buffer.

        :return: True if successful, False otherwise
        :rtype: bool
        """
        ...

    async def size(self) -> int:
        """
        Get the current number of elements in the buffer.

        :return: Current number of elements
        :rtype: int
        """
        ...


class ISerializer(Protocol[T]):
    def dumps(self, obj: T) -> bytes | str:
        """
        Dump object to bytes or str.

        :param obj: Object to dump
        :type obj: T
        :return: Dumped object
        :rtype: bytes | str
        """
        ...

    def loads(self, obj: bytes | str) -> T:
        """
        Load object from bytes or str.

        :param obj: Object to load
        :type obj: bytes | str
        :return: Loaded object
        :rtype: T
        """
        ...


class IHashAndCompare(Protocol):
    def __call__(self, value: bytes | str, expected: str, key: str = ...) -> str:
        """
        Hash value and compare to provided hash.

        :param value: Value to hash
        :type value: T
        :param expected: Hashed value to compare to
        :type expected: str
        :param key: Key to compute hash with
        :type key: str
        :return: Hashed value
        :rtype: str
        """
        ...
