redis.call('DEL', KEYS[2])
redis.call('SET', KEYS[1], 0)
return 1
