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
