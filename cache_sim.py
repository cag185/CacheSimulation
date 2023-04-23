# Code written by Caleb Gibson and Peter Bertola
from cache import cache



# run the program
def main():
    print("Welcome to Caleb and Peter's Cache simulation!")
    print('Before we can begin, lets set up the following settings: ')

    busy = False

    cache_layer_num = 0 # number of levels in cache
    cache_layer_size = [] # number of bytes each cache layer will hold
    cache_layer_latency = [] # number of clock cycles each cache layer will have in latency
    block_size = 0 # number of bytes a block can hold
    set_associativity = [] # holds the set associativity for a given cache level
    write_allocation_style = -1 # holds the write policy and allocation policy for the cache
    #--IMPORTANT-- if write_allocation_style = 0 -- CACHE IS WRITE BACK AND WRITE ALLOCATE
    # if write_allocation_style = 1 -- CACHE IS WRITE THROUGH AND NON-WRITE-ALLOCATE
    # otherwise, cache write allocation style has not been set yet


    # if the simulation not busy ask for user input
    if(busy == False):
        # ask for user input
        print("Please set the number of cache layers. Enter a postive integer (ex. 1,2,3): ")
        cache_layer_num = int(input()) # retrieve input

        # for each layer in the cache, assign the mem size in bytes
        for cache_level in range(cache_layer_num):
            print("Please enter the memory size in bytes (ex. 1000, 200000, 1000000) for layer ", cache_level,": ")
            temp_size = int(input()) # retrieve size of cache layer
            cache_layer_size.append(temp_size)
        
        # for each layer in the cache, assign a latency
        for cache_level in range(cache_layer_num):
            print("Please enter the latency in clock cycles (ex. 1, 10, 100) for layer ", cache_level,": ")
            temp_lat = int(input()) # retrieve latency
            cache_layer_latency.append(temp_lat)

        # ask the user for the block size in bytes
        print("Please enter the size in bytes for the block size (ex. 64, 128, etc.): ")
        block_size = int(input())

        # set associativity for each layer
        for cache_level in range(cache_layer_num):
            print("Please enter the set-associativity (ex. 1, 2, 4, 8) for layer ", cache_level, ":  ")
            temp_ass = int(input()) # hehe
            set_associativity.append(temp_ass)
        
        # set the write policy - controls the write allocation
        print('Please set the Write-Policy for the Cache. The options are as follows: ')
        print("Write-Back with Write-Allocate allocation policy [0].")
        print("Write-through with Non-Write-Allocate allocation policy [1].")
        print("Please enter '0' for the first option or '1' for the second: ")
        temp_setting = int(input())
        if(temp_setting == 1):
            write_allocation_style = temp_setting
        else:
            while ((temp_setting != 0) or (temp_setting != 1)):
                print("Please enter '0' for the first option or '1' for the second: ")
                temp_setting = int(input())
        write_policy = ""
        allocation_policy = ""
        if (write_allocation_style == 0):
            write_policy = "write-back"
            allocation_policy = "write-allocate"
        elif(write_allocation_style == 1):
            write_policy = "write-through"
            allocation_policy = "non-write-allocate"
        # done with settings
        busy = True
    # Create a Cache instance with the gathered parameters
    cache1 = cache(cache_layer_num, cache_layer_size, cache_layer_latency, block_size, set_associativity, write_policy, allocation_policy)

    # Read the input stream from a text file
    input_file_path = "input_stream.txt"  # Replace with your input file path
    with open(input_file_path, "r") as input_file:
        input_stream = input_file.readlines()

    # Call the parse_input function of the Cache instance with the input stream
    cache.parse_input(input_stream)

# run the program
if __name__ == "__main__":
    main()

    
