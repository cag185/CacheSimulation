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
        self.read_finish_times = []
        self.read_finish_latencies = []
        self.block_size = block_size
        self.memory_access_latency = 100
        self.n_size = 0 # placeholder for the block offset bits
        self.s_size = 0 # placeholder for the set-index bits
        self.m_n_s = 0 # placeholder for the tag bits

        # cache hit/miss code variables
        # self.read_instruction_count = 0 # this is the variable to track the read instruction count
        self.cache_layer_miss_count =  [0] * num_layers# this is a list to hold the number of misses in each cache layer as the read instructions are computed
        self.cache_layer_hit_count = [0] * num_layers# this is a list to hold the number of hits in each cache layer as the read instructions are computed
        
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
        address = int(address)
        # attempt another way to get tag
        address_len = len(str(address))
        # Calculate the number of bits needed for the index
        index_bits = int(math.log2(self.cache_hierarchy[0]["num_sets"]))
        s_size = int(index_bits) # the size of s (the set index)
        n_size = int(math.log2(self.block_size)) # the size of n (the block offset)
        m_n_s = int((address_len) - (s_size) - (n_size)) # gets the size of m-s-n (the tag)
        address = str(address)
        # assign the actual value for tag, index, and offset
        tag = str(address[0:m_n_s])
        cache_set_index = str(address[m_n_s:s_size+m_n_s])
        block_offset = str(address[s_size: n_size+s_size])

        # convert the binary numbers into decimal
        tag = int(tag, 2)
        cache_set_index = int(cache_set_index, 2)
        block_offset = int(block_offset, 2)


        # # Calculate the mask and shift values for the tag and index
        # tag_shift = self.block_offset_bits + index_bits
        # index_mask = (1 << index_bits) - 1
        # # Extract the tag, index, and offset from the address
        # tag = address >> tag_shift
        # cache_set_index = (address >> self.block_offset_bits) & index_mask
        # block_offset = address & ((1 << self.block_offset_bits) - 1)

        return tag, cache_set_index, block_offset

    
    
    def create_cache_block(self):
        return {
            "tag": None,
            "valid": False,
            "dirty": False,
            "lru_counter": 0,
            "data": [0] * self.block_size # Initialize the data field as a bytearray of the specified block size
    }
    
    def load_data_into_cache(self, layer, tag, cache_set_index, data):
        """
        This function loads data into a cache set within a layer.
        """
        cache_set = layer["sets"][cache_set_index]

        # Try to find an available (not valid) cache block
        available_block = None
        # find the block index where the LRU counter is highest
        highest_lru_block_index = 0
        highest_lru_block_value = 0

        for block_index, block in enumerate(cache_set):
            # check for the lru counter
            if (block["lru_counter"] > highest_lru_block_value):
                highest_lru_block_index = block_index
                highest_lru_block_value = block["lru_counter"]
            if not block["valid"]:
                available_block = block
                break

        # If no available block is found, evict the LRU block
        if available_block is None:
            lru_block_index = highest_lru_block_index
            # lru_block_index = min(enumerate(cache_set), key=lambda x: x[1]["last_used"])[0]
            available_block = cache_set[lru_block_index]

        # Update the available block with the new data and tag
        available_block["tag"] = tag
        available_block["valid"] = True
        available_block["dirty"] = False
        available_block["data"] = data
        available_block["lru_counter"] = 0

    
    def read(self, address, main_memory):
    # for each read instruction, we want to calculate the hit and miss ratio for each layer
    # ToDO: For each read instruction, check if the instruuction was a hit in the lowest (smallest) cache level
        # if yes, we have a hit
        # ELSE, we have a miss, go to the next layer
    # basically want to track the hit rate of each layer per instruction


    # Calculate the tag, index, and offset from the address
        tag, cache_set_index, block_offset = self.parse_address(address)
        access_latency = 0
        data = None

        layer_index = 0
        for layer in (self.cache_hierarchy):  # Traverse from highest to lowest level
            access_latency += layer["access_latency"]

            try:
                cache_block, cache_block_index = self.find_cache_block(tag, cache_set_index, layer) 
                if cache_block and cache_block["valid"]:
                    # Cache hit: store the data and exit the loop
                    self.cache_layer_hit_count[layer_index] += 1 # increase the count of the hit at that layer
                    data = cache_block["data"][block_offset]
                    # self.update_lru(layer, cache_set_index, cache_block_index)
                    print("test")
                    self.update_lru(layer, cache_set_index, cache_block_index) # use optional param with block index getting hit
                    print('Test2')
                    break
            except:
                # if the data not found in the curr cache layer
                self.cache_layer_miss_count[layer_index] += 1
                print("Miss!")
            # increase the counter
            layer_index += 1

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
                    return cache_block, block_index
            return



    def update_lru(self, layer, cache_set_index, block_index):
        for block in layer["sets"][cache_set_index]:
            block["lru_counter"] += 1

        layer["sets"][cache_set_index][block_index]["lru_counter"] = 0

    # input data is instruction (r/w), address, and the arrival time
    def parse_input(self, input_stream, main_memory):
        # Parse the input stream of memory accesses
        # ToDo - the reason this is read in this way is that the lines are already tokenized in the main file, and are passed in as a tuple that 
        # can be unpacked here

        # for each time this command is called, reset the count for the read instructions and init the values of the hit/miss arrays to 0
        # cache hit/miss code variables
        # self.read_instruction_count = 0
        self.cache_layer_miss_count.clear # reset the list
        self.cache_layer_hit_count.clear # reset the list
        # input_stream.sort(key=lambda x: x[2]) # sort the input stream by arrival time
        
        for line in input_stream:
            instructionChar, address, arr_time = line

            # based on the operation call a different function
            if(instructionChar == 'r'):
                print('read instruction')
                read_results = self.read(address, main_memory)
                self.read_finish_times.append (int(arr_time) + read_results[1]) # append the time taken to get a hit
                self.read_finish_latencies.append(read_results[1]) # append the time taken to get a hit without the initial time
                # output
                # self.output_cache_status()
                self.output_read_times()

            elif(instructionChar == 'w'):
                print('write instruction')
                self.write(address, 1111, main_memory) ##-- having issue here, not sure what the data will be that needs to be written to

        # now the two lists should contain the counters of hits and misses per layer in the cache
        # Output the cache status after processing all instructionsAS
        self.output_cache_status() # might need to comment this out and display all blocks in all layers for every read
        
        self.output_cache_HM_ratio()

   # display the read delay and latency for each read instruction
    def output_read_times(self):
        print("----- Read latencies and Finish times ------")
        print()
        for read in range(len(self.read_finish_latencies)):
            print(f"Read {read} finish time: " , self.read_finish_times[read])
            print(f"Total latency of read {read}: ", self.read_finish_latencies[read])


    # Rather than print after every read, might be a better idea to save the delays and cache misses/hit ratio until all the instructions are read
    def output_cache_status(self):
        for layernum, layer in enumerate(self.cache_hierarchy):
            print()  
            print(f"\t-------- Layer {layernum} --------")
            print()
            print(f" set index | block index | valid | dirty | lru counter | tag ")
            for set_idx, cache_set in layer['sets'].items():
                for block_idx, cache_block in enumerate(cache_set):
                    valid = cache_block['valid'] if cache_block['valid'] is not None else 'N/A'
                    dirty = cache_block['dirty'] if cache_block['dirty'] is not None else 'N/A'
                    lru_counter = cache_block['lru_counter'] if cache_block['lru_counter'] is not None else 'N/A'
                    tag = cache_block['tag'] if cache_block['tag'] is not None else 'N/A'
                    print(f"{set_idx:10} | {block_idx:11} | {valid:5} | {dirty:5} | {lru_counter:11} | {tag:8}")

    def output_cache_HM_ratio(self):
        # this function specifically outputs the Hit to miss ratio of the cache
        # for each layer in the cache, we want to compute and print the layer hit/miss ratio
        # print the layers h/m ratio
        print()
        print('---The Hit to Miss ratio for each layer in the cache: ---')
        print()
        ratio_h_m = []
        for x in range(len(self.cache_layer_hit_count)):
            # ratio of hits to misses = hitcount / misscount
            ratio_h_m.append(0.0) if (self.cache_layer_miss_count[x] == 0 and self.cache_layer_hit_count[x]==0) else ratio_h_m.append(self.cache_layer_hit_count[x] / (self.cache_layer_miss_count[x] + self.cache_layer_hit_count[x])) # should compute hit/ (hit + miss)
            print(f"layer {x}: ", ratio_h_m[x])
        print()
        print('---The Miss to Hit ratio for each layer in the cache: ---')
        print()
        ratio_m_h = []
        for x in range(len(self.cache_layer_miss_count)):
            # ratio of hits to misses = hitcount / misscount
            ratio_m_h.append(0.0) if (self.cache_layer_miss_count[x] == 0 and self.cache_layer_hit_count[x]==0) else ratio_m_h.append(self.cache_layer_miss_count[x] / (self.cache_layer_miss_count[x] + self.cache_layer_hit_count[x])) # should compute hit/ (hit + miss)
            print(f"layer {x}: ", ratio_m_h[x])