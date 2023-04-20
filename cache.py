import math
import os # module to load in data from the system
class Cache:
    def __init__(self, num_layers, cache_sizes, access_latencies, block_size, set_associativities, write_policy, allocation_policy, input_stream):
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
        self.read_finish_latencies = []
        self.block_size = block_size
        self.input_stream = input_stream # given to the class from the main function where we instantiate the class
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
    
    def load_data_into_cache(self, layer, tag, cache_set_index, data):
        cache_set = layer["sets"][cache_set_index]

        # Try to find an available (not valid) cache block
        available_block = None
        for block in cache_set:
            if not block["valid"]:
                available_block = block
                break

        # If no available block is found, evict the LRU block
        if available_block is None:
            lru_block_index = min(enumerate(cache_set), key=lambda x: x[1]["last_used"])[0]
            available_block = cache_set[lru_block_index]

        # Update the available block with the new data and tag
        available_block["tag"] = tag
        available_block["valid"] = True
        available_block["dirty"] = False
        available_block["data"] = data
        available_block["last_used"] = self.current_time

    
    def read(self, address, main_memory):
    # Calculate the tag, index, and offset from the address
        tag, cache_set_index, block_offset = self.parse_address(address)
        access_latency = 0
        data = None

        for layer in reversed(self.cache_hierarchy):  # Traverse from highest to lowest level
            access_latency += layer["latency"]
            cache_block = self.find_cache_block(tag, cache_set_index, layer)

            if cache_block and cache_block["valid"]:
                # Cache hit: store the data and exit the loop
                data = cache_block["data"][block_offset]
                break

        # If data is found in a higher-level cache, load it into all lower-level caches
        if data is not None:
            for layer in self.cache_hierarchy:
                if not self.find_cache_block(tag, cache_set_index, layer):
                    self.load_data_into_cache(layer, tag, cache_set_index, data)
                else:
                    break
        else:
            # If not found in any cache, read the data from memory
            access_latency += self.memory_access_latency
            data = main_memory.get(address)

            # Load data into all cache levels
            for layer in self.cache_hierarchy:
                self.load_data_into_cache(layer, tag, cache_set_index, data)

        return data, access_latency


    def write(self, address, data, main_memory):
    # Implement write operation
        tag, cache_set_index, block_offset = self.parse_address(address)

        write_hit = False
        for layer_idx, layer in enumerate(self.cache_hierarchy):
            cache_block = self.find_cache_block(tag, cache_set_index, layer)

            if cache_block and cache_block["valid"]:
                write_hit = True

                # Check if the block is present in the lower-level cache
                if layer_idx > 0:
                    prev_layer = self.cache_hierarchy[layer_idx - 1]
                    prev_cache_block = self.find_cache_block(tag, cache_set_index, prev_layer)
                    if prev_cache_block and prev_cache_block["valid"]:
                        cache_block = prev_cache_block

                if self.write_policy == "write-back":
                    cache_block["data"][block_offset] = data
                    cache_block["dirty"] = True
                elif self.write_policy == "write-through":
                    cache_block["data"][block_offset] = data
                    main_memory[address] = data

        if not write_hit:
            if self.write_policy == "write-back" and self.allocation_policy == "write-allocate":
                for layer in self.cache_hierarchy:
                    self.load_data_into_cache(layer, tag, cache_set_index, data)

            elif self.write_policy == "write-through" and self.allocation_policy == "non-write-allocate":
                main_memory[address] = data

    def update_lru(self, ...):
        pass
        # Update the LRU information

    # input data is instruction (r/w), address, and the arrival time
    def parse_input(self, input_stream):
        # Parse the input stream of memory accesses
        for line in input_stream:
            instructionChar, address, arr_time = line

            # based on the operation call a different function
            if(instructionChar == 'r'):
                print('read instruction')
                read_results = self.read(address, main_memory)
                read_finish_times.append (arr_time + read_results.access_latency) # append the time taken to get a hit
                read_finish_latencies.append(read_results.access_latency) # append the time taken to get a hit without the initial time
                # output
                self.output_cache_status()

            elif(instructionChar == 'w'):
                print('write instruction')
                # self.write(address, ) -- having issue here, not sure what the data will be that needs to be written to
            # after the input was parsed, call the output function


    # Rather than print after every read, might be a better idea to save the delays and cache misses/hit ratio until all the instructions are read
    def output_cache_status(self):
        # Output cache status image, hit/miss rates, and finish time of read accesses
        print('-----The finsish time of each read, and its corresponding latency-----')
        for hit in range(read_finish_times):
            print('Finish time of read ${hit}: ', self.read_finish_times[hit])
            print('Total latency of read ${hit}: ', self.read_finish_latencies[hit])
