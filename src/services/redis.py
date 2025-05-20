import json
import pickle
from typing import cast

from redis.asyncio import Redis
from redis.commands.core import AsyncScript

from services.interfaces import IRingBuffer, ISerializer, T


class RedisRingBuffer(IRingBuffer[T]):
    """
    An asynchronous ring buffer implementation using Redis as a storage backend.

    Features:
    - Atomic write operations using transactions
    - Non-atomic read operations
    - Configurable ring size
    """

    def __init__(
        self,
        redis: Redis,
        name: str,
        max_size: int,
        serializer: ISerializer[T] = pickle,
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
        self.__write: AsyncScript = None  # type:ignore
        self.__size: AsyncScript = None  # type:ignore
        self.__clear: AsyncScript = None  # type:ignore
        self.__latest: AsyncScript = None  # type:ignore
        self.__all_ordered: AsyncScript = None  # type:ignore

    async def _initialize(self) -> None:
        if self.__initialized:
            return
        if not await self.redis.exists(self.head_key):
            await self.redis.set(self.head_key, 0)

        self.__write = self.__redis.register_script(
            """
            local head = tonumber(redis.call('GET', KEYS[1]) or "0")
            local position = head % tonumber(ARGV[1])

            -- Store the value at the calculated position
            redis.call('HSET', KEYS[2], position, ARGV[2])

            -- Increment head and store it
            head = head + 1
            redis.call('SET', KEYS[1], head)

            return head
            """
        )
        self.__size = self.__redis.register_script(
            """
            local head = tonumber(redis.call('GET', KEYS[1]) or "0")
            local max_size = tonumber(ARGV[1])
            return math.min(head, max_size)
            """
        )
        self.__clear = self.__redis.register_script(
            """
            redis.call('DEL', KEYS[2])
            redis.call('SET', KEYS[1], 0)
            return 1
            """
        )
        self.__latest = self.__redis.register_script(
            """
            local head = tonumber(redis.call('GET', KEYS[1]) or "0")
            local max_size = tonumber(ARGV[1])
            local count = tonumber(ARGV[2])
            local result = {}

            -- If empty buffer
            if head == 0 then
                return result
            end

            -- Calculate how many items to fetch (min of requested count, actual items)
            local items_to_fetch = math.min(count, math.min(head, max_size))

            -- Get the latest items in reverse order (newest first)
            for i = 0, items_to_fetch - 1 do
                local pos = (head - i - 1) % max_size
                local value = redis.call('HGET', KEYS[2], tostring(pos))
                if value then
                    table.insert(result, value)
                end
            end

            return result
            """
        )
        self.__all_ordered = self.__redis.register_script(
            """
            local head = tonumber(redis.call('GET', KEYS[1]) or "0")
            local max_size = tonumber(ARGV[1])
            local result = {}
            
            -- Get actual size (min of head or max_size)
            local size = math.min(head, max_size)
            
            -- If buffer has wrapped, get items in correct order (oldest to newest)
            if head > max_size then
                local start_pos = head % max_size
                
                -- First collect from start_pos to max_size - 1
                for i = start_pos, max_size - 1 do
                    local value = redis.call('HGET', KEYS[2], tostring(i))
                    if value then
                        table.insert(result, {tostring(i), value})
                    end
                end
                
                -- Then collect from 0 to start_pos - 1
                for i = 0, start_pos - 1 do
                    local value = redis.call('HGET', KEYS[2], tostring(i))
                    if value then
                        table.insert(result, {tostring(i), value})
                    end
                end
            else
                -- If buffer hasn't wrapped, get items in index order
                for i = 0, size - 1 do
                    local value = redis.call('HGET', KEYS[2], tostring(i))
                    if value then
                        table.insert(result, {tostring(i), value})
                    end
                end
            end
            
            return result
            """
        )

        self.__initialized = True

    async def _head(self) -> int:
        head = await self.redis.get(self.head_key)
        return int(head) if head else 0

    async def put(self, value: T) -> bool:
        await self._initialize()

        serialized = self.__serializer.dumps(value)

        await self.__write(
            keys=[self.head_key, self.data_key],
            args=[self.max_size, serialized],
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
                keys=[self.head_key, self.data_key],
                args=[self.max_size],
            )
            return list(self.__serializer.loads(value) for _, value in pairs)
        else:
            # buffer has not wrapped around,
            # so we can simply get all values and
            # sort them
            values = await self.__redis.hgetall(self.data_key)
            positions = [
                (key.decode()) if isinstance(key, bytes) else int(key)
                for key in values.keys()
            ]
            positions = sorted(positions)
            return list(
                self.__serializer.loads(values[position]) for position in positions
            )

    async def latest(self, n: int) -> list[T]:
        await self._initialize()

        values = await self.__latest(
            keys=[self.head_key, self.data_key],
            args=[self.max_size, n],
        )
        return list(self.__serializer.loads(value) for value in values)

    async def clear(self) -> bool:
        await self._initialize()

        await self.__clear(
            keys=[self.head_key, self.data_key],
            args=[],
        )
        return True

    async def size(self) -> int:
        await self._initialize()

        size = await self.__size(
            keys=[self.head_key],
            args=[self.max_size],
        )
        return int(size) if size else 0
