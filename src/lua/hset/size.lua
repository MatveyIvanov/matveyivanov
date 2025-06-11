local head = tonumber(redis.call('GET', KEYS[1]) or "0")
local max_size = tonumber(ARGV[1])
return math.min(head, max_size)
