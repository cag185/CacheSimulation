# Code written by Caleb Gibson and Peter Bertola
from cache import Cache
# import Caleb_Instruction_Example.txt
import os # module to open files from the system


def get_cache_size():
        size_str = input()
        size_str = size_str.strip().lower()
        
        if size_str[-2:] == "kb" or size_str[:-2] == "KB":
            size_bytes = int(size_str[:-2]) * 1024
        elif size_str[-2:] == "mb" or size_str[:-2] == "MB":
            size_bytes = int(size_str[:-2]) * 1024 * 1024
        elif size_str[-2:] == "gb" or size_str[:-2] == "GB":
            size_bytes = int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            size_bytes = int(size_str)
            
        return size_bytes

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

    # main memory in the form of an array
    main_mem_path = "MainMemory.txt"
    main_mem_dict = {}

    with open(main_mem_path, "r") as file:
        for line in file:
            address, value = line.strip().split()

            if address not in main_mem_dict:
                main_mem_dict[address] = value

    # if the simulation not busy ask for user input
    if(busy == False):
        # ask for user input
        print("Please set the number of cache layers. Enter a postive integer (ex. 1,2,3): ")
        cache_layer_num = int(input()) # retrieve input

        # for each layer in the cache, assign the mem size in bytes
        for cache_level in range(cache_layer_num):
            print("Please enter the memory size for layer", cache_level, "in the format (ex. 4KB, 256KB, 1MB, 2GB): ")
            temp_size_str = input() # retrieve size of cache layer as a string
            temp_size = get_cache_size(temp_size_str) # convert the string into bytes
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
        if(temp_setting == 1 or temp_setting == 0):
            write_allocation_style = temp_setting
        else:
            while ((temp_setting != 0) and (temp_setting != 1)):
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
    cache1 = Cache(cache_layer_num, cache_layer_size, cache_layer_latency, block_size, set_associativity, write_policy, allocation_policy)

    # data structure for holding the input stream
    input_data = []

    # load in the input stream 
    folder_path = '/Input_Data'
    # get list of files
    file_list = os.listdir(folder_path)
    if (len(file_list) == 1):
        try :
            selected_file = file_list[0]
            with open(os.path.join(folder_path, selected_file), 'r') as f:
                for line in f:
                    tokens = line.split
                    if(len(tokens)  == 3):
                        data_set = set(tokens) # convert the three data fields into a set
                        input_data.append(data_set) # add the set to the data structure
        except:
            print('something went wrong with opening your data')
        
    else:
        print("ERROR: More than one file in the Input directory. Remove all but one files and try again")

    # instantiate the cache
    # descrepency between the class and the inputs from the user -- write policy and allocation policy should be one variable
    cache1 = Cache(cache_layer_num, cache_layer_size, cache_layer_latency, block_size, set_associativity, write_policy, allocation_policy)
    # parse the input data and send it to the cache
    cache1.parse_input(input_data, main_mem_dict) # parses the input data and calls the read/write functions

# run the program
if __name__ == "__main__":
    main()


    
