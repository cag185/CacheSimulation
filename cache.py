class Cache:
    def __init__(self, num_layers, cache_sizes, access_latencies, block_size, set_associativities, write_policy, allocation_policy):
        self.num_layers = num_layers
        self.cache_sizes = cache_sizes
        self.access_latencies = access_latencies
        self.block_size = block_size
        self.set_associativities = set_associativities
        self.write_policy = write_policy
        self.allocation_policy = allocation_policy
        self.cache_hierarchy = self.initialize_cache_hierarchy()
        self.hit_counters = [0] * num_layers
        self.miss_counters = [0] * num_layers
        self.read_finish_times = []
        self.block_size = block_size

        # Calculate the number of bits needed for the block offset
        self.block_offset_bits = int(log2(block_size))

        self.cache_hierarchy = self.initialize_cache_hierarchy()

    def initialize_cache_hierarchy(self):
        # Initialize the cache hierarchy based on configuration parameters
        # and create data structures for cache layers
        cache_hierarchy = []

        for i in range(self.num_layers):
            layer = {
                "size": self.cache_sizes[i],
                "access_latency": self.access_latencies[i],
                "associativity": self.set_associativities[i],
                "num_sets": self.cache_sizes[i] // (self.block_size * self.set_associativities[i]),
                "sets": {}
            }

            for set_index in range(layer["num_sets"]):
                layer["sets"][set_index] = [self.create_cache_block() for _ in range(layer["associativity"])]

            cache_hierarchy.append(layer)

        return cache_hierarchy

    
    def create_cache_block(self):
        return {
            "tag": None,
            "valid": False,
            "dirty": False,
            "lru_counter": 0,
            "data": bytearray(self.block_size)  # Initialize the data field as a bytearray of the specified block size
    }
        
    def read(self, address):
        # Implement read operation
        
        # Calculate the tag, index, and offset from the address
        tag, cache_set_index, block_offset = self.parse_address(address)

        # Perform cache operations to find the cache block with the given tag and index
        cache_block = self.find_cache_block(tag, cache_set_index)

        # If the cache block is found and valid, return the requested byte
        if cache_block and cache_block["valid"]:
            return cache_block["data"][block_offset]


    def write(self, address, arriving_time):
        pass
        # Implement write operation

    def update_lru(self, ...):
        pass
        # Update the LRU information

    def parse_input(self, input_stream):
        pass
        # Parse the input stream of memory accesses

    def output_cache_status(self):
        # Output cache status image, hit/miss rates, and finish time of read accesses
