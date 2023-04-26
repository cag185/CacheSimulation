import math
from math import log2
import os # module to load in data from the system
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
        self.read_finish_latencies = []
        self.block_size = block_size
        memory_access_latency = 100
        
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

            # This code is initializing the cache sets for a given cache layer. It is creating a list
            # of cache blocks for each set in the layer, where the number of blocks in each set is
            # equal to the set associativity. The `for` loop iterates over the range of `num_sets` in
            # the layer, and for each set index, it creates a list of cache blocks using a list
            # comprehension. The list comprehension creates a list of `associativity` number of cache
            # blocks using the `create_cache_block()` method. The resulting list of cache blocks is
            # then assigned to the `sets` dictionary for the corresponding set index in the layer.
            for set_index in range(layer["num_sets"]):
                layer["sets"][set_index] = [self.create_cache_block() for _ in range(layer["associativity"])]

            cache_hierarchy.append(layer)

        return cache_hierarchy

    def parse_address(self, address):
        # Calculate the number of bits needed for the index
        index_bits = int(math.log2(self.cache_hierarchy[0]["num_sets"]))

        # Calculate the mask and shift values for the tag and index
        tag_shift = self.block_offset_bits + index_bits
        index_mask = (1 << index_bits) - 1

        # Extract the tag, index, and offset from the address
        tag = address >> tag_shift
        cache_set_index = (address >> self.block_offset_bits) & index_mask
        block_offset = address & ((1 << self.block_offset_bits) - 1)

        return tag, cache_set_index, block_offset

    
    def create_cache_block(self):
        return {
            "tag": None,
            "valid": False,
            "dirty": False,
            "lru_counter": 0,
            "data": bytearray(self.block_size)  # Initialize the data field as a bytearray of the specified block size
    }
    
    def load_data_into_cache(self, layer, tag, cache_set_index, data):
        """
        This function loads data into a cache set within a layer.
        """
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
            cache_block, cache_block_index = self.find_cache_block(tag, cache_set_index, layer)

            if cache_block and cache_block["valid"]:
                # Cache hit: store the data and exit the loop
                data = cache_block["data"][block_offset]
                self.update_lru(layer, cache_set_index, cache_block_index)
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
            cache_block, cache_block_index = self.find_cache_block(tag, cache_set_index, layer)

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
                    main_memory[address] = data
                    
                    self.update_lru(layer, cache_set_index, cache_block_index)

        if not write_hit:
            if self.write_policy == "write-back" and self.allocation_policy == "write-allocate":
                for layer in self.cache_hierarchy:
                    self.load_data_into_cache(layer, tag, cache_set_index, data)

            elif self.write_policy == "write-through" and self.allocation_policy == "non-write-allocate":
                main_memory[address] = data


    def find_cache_block(self, tag, cache_set_index, layer):
        cache_set = layer["sets"][cache_set_index]

        for block_index, cache_block in enumerate(cache_set):
            if cache_block["valid"] and cache_block["tag"] == tag:
                return block_index, cache_block
        return None, None

    def update_lru(self, layer, cache_set_index, block_index):
        for block in layer["sets"][cache_set_index]:
            block["lru_counter"] += 1

        layer["sets"][cache_set_index][block_index]["lru_counter"] = 0

    # input data is instruction (r/w), address, and the arrival time
    def parse_input(self, input_stream, main_memory):
        # Parse the input stream of memory accesses
        # ToDo - the reason this is read in this way is that the lines are already tokenized in the main file, and are passed in as a tuple that 
        # can be unpacked here
        
        input_stream.sort(key=lambda x: x[2]) # sort the input stream by arrival time
        
        for line in input_stream:
            instructionChar, address, arr_time = line

            # based on the operation call a different function
            if(instructionChar == 'r'):
                print('read instruction')
                read_results = self.read(address, main_memory)
                self.read_finish_times.append (arr_time + read_results.access_latency) # append the time taken to get a hit
                self.read_finish_latencies.append(read_results.access_latency) # append the time taken to get a hit without the initial time
                # output
                self.output_cache_status()

            elif(instructionChar == 'w'):
                print('write instruction')
                self.write(address,main_memory) ##-- having issue here, not sure what the data will be that needs to be written to
            # Output the cache status after processing all instructionsAS
            self.output_cache_status()
    
    # def parse_input(self, input_stream,main_memory):
    # # Iterate over the input stream line by line
    #     for line in input_stream:
    #         # Remove any leading/trailing whitespaces and split the line into components
    #         components = line.strip().split()

    #         # Get the instruction, address, and arrival time from the components
    #         instruction = components[0]
    #         address = int(components[1], 16)  # Assuming the address is in hexadecimal format
    #         arrival_time = float(components[2])
    #         data_to_write = components[3] if len(components) > 3 else None

    #         # Process the instruction based on whether it's a read (r) or write (w) operation
    #         if instruction == 'r':
    #             print('read instruction')
    #             data, access_latency = self.read(address, main_memory)
    #             self.read_finish_times.append(arrival_time + access_latency)
    #             self.read_finish_latencies.append(access_latency)
    #             self.output_cache_status()

    #         elif instruction == 'w':
    #             print('write instruction')
    #             # Replace 'data_to_write' with the appropriate data to write
    #             self.write(address, data_to_write, main_memory)

    # # Output the cache status after processing all instructions
    #         self.output_cache_status()


    # Rather than print after every read, might be a better idea to save the delays and cache misses/hit ratio until all the instructions are read
    def output_cache_status(self):
        for layer_idx, layer in enumerate(self.cache_hierarchy):
            print(f"Layer {layer_idx + 1}:")
            print("Set | Block | Valid | Dirty | LRU Counter | Tag")

            for set_idx, cache_set in layer["sets"].items():
                for block_idx, cache_block in enumerate(cache_set):
                    print(f"{set_idx:3} | {block_idx:5} | {cache_block['valid']:5} | {cache_block['dirty']:5} | {cache_block['lru_counter']:10} | {cache_block['tag']:4}")

            print("\n")

