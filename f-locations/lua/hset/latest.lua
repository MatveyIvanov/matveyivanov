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
