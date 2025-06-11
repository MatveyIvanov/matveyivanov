import pickle

import aiofiles
from redis.asyncio import Redis
from redis.commands.core import AsyncScript

from services.interfaces import IRingBuffer, ISerializer


class RedisRingBuffer[T](IRingBuffer[T]):
    __write: AsyncScript
    __size: AsyncScript
    __clear: AsyncScript
    __latest: AsyncScript
    __all_ordered: AsyncScript

    def __init__(
        self,
        redis: Redis,
        name: str,
        max_size: int,
        serializer: ISerializer[T] = pickle,  # type:ignore[assignment]
    ):
        """
        :param redis: Redis client
        :type redis: Redis
        :param name: Unique name for the buffer
        :type name: str
        :param max_size: Maximum number of elements
        :type max_size: int
        :param serializer: Serializer for redis
        :type serializer: ISerializer[T]
        """
        self.__redis = redis
        self.__name = name
        self.__max_size = max_size
        self.__serializer = serializer
        self.__head_key = f"{name}:head"
        self.__data_key = f"{name}:data"
        self.__lock_key = f"{name}:lock"
        self.__initialized = False

    async def _initialize(self) -> None:
        if self.__initialized:
            return

        if not await self.__redis.exists(self.__head_key):
            await self.__redis.set(self.__head_key, 0)

        async def load(path: str) -> str:
            async with aiofiles.open(path, "r") as file:
                content = await file.read()
            return content

        self.__write = self.__redis.register_script(
            await load("lua/hset/write_one.lua")
        )
        self.__size = self.__redis.register_script(await load("lua/hset/size.lua"))
        self.__clear = self.__redis.register_script(await load("lua/hset/clear.lua"))
        self.__latest = self.__redis.register_script(await load("lua/hset/latest.lua"))
        self.__all_ordered = self.__redis.register_script(
            await load("lua/hset/all.lua")
        )

        self.__initialized = True

    async def _head(self) -> int:
        head = await self.__redis.get(self.__head_key)
        return int(head) if head else 0

    async def put(self, value: T) -> bool:
        await self._initialize()

        serialized = self.__serializer.dumps(value)

        await self.__write(
            keys=[self.__head_key, self.__data_key],
            args=[self.__max_size, serialized],
        )
        return True

    async def all(self) -> list[T]:
        await self._initialize()

        head = await self._head()
        if head == 0:
            return []

        if head > self.__max_size:
            # buffer has wrapped around, so
            # we need to get items in the correct order
            pairs = await self.__all_ordered(
                keys=[self.__head_key, self.__data_key],
                args=[self.__max_size],
            )
            return list(self.__serializer.loads(value) for _, value in pairs)
        else:
            # buffer has not wrapped around,
            # so we can simply get all values and
            # sort them
            values = await self.__redis.hgetall(self.__data_key)  # type:ignore[misc]
            positions: list[int] = [
                int(key.decode()) if isinstance(key, bytes) else int(key)
                for key in values.keys()
            ]
            positions = sorted(positions)
            return list(
                self.__serializer.loads(values[str(position).encode()])
                for position in positions
            )

    async def latest(self, n: int = 1) -> list[T]:
        await self._initialize()

        values = await self.__latest(
            keys=[self.__head_key, self.__data_key],
            args=[self.__max_size, n],
        )
        return list(self.__serializer.loads(value) for value in values)

    async def clear(self) -> bool:
        await self._initialize()

        await self.__clear(
            keys=[self.__head_key, self.__data_key],
            args=[],
        )
        return True

    async def size(self) -> int:
        await self._initialize()

        size = await self.__size(
            keys=[self.__head_key],
            args=[self.__max_size],
        )
        return int(size) if size else 0
