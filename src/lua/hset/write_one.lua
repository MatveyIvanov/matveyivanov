local head = tonumber(redis.call('GET', KEYS[1]) or "0")
local position = head % tonumber(ARGV[1])

-- Store the value at the calculated position
redis.call('HSET', KEYS[2], position, ARGV[2])

-- Increment head and store it
head = head + 1
redis.call('SET', KEYS[1], head)

return head
