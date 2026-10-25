import os
import sys
import mmap
import time
import concurrent.futures

# Amjed H - EN 525.742 Lab 9

GREEN_LED_ADDR = 0x41200000
DIP_SW_ADDR    = 0x41200008
RGB_LED_ADDR   = 0x41210000

REDS   = 0b100100
GREENS = 0b010010
BLUES  = 0b001001

# Lazy dictinoary....thing.
# Based on SW inputs (left), set RGBs.
SW_TO_RGB_LUT = { \
0b000 : 0x0   , # OFF
0b001 : REDS  , # RED
0b010 : GREENS, # GREEN
0b100 : BLUES , # BLUE
0b011 : REDS  | GREENS, # R+G
0b101 : REDS  | BLUES , # R+B
0b110 : BLUES | GREENS, # B+G
0b111 : REDS  | GREENS | BLUES  # R+G+B
}

def open_mem(addr):
    try:
        fd = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
    except PermissionError:
        print("Error: You must run this script as root (sudo).", file=sys.stderr)
        exit(-1)
    try:
        page_size = os.sysconf('SC_PAGE_SIZE')
        # This probably varies based on page size. But our platform isn't changing soo.. gonna
        # keep this hardcoded.
        address = addr & 0xFFFF0000
        mem = mmap.mmap(fd, page_size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=address)
        os.close(fd)
        return mem
    
    except Exception as e:
        print(e)
        exit(-1)

def write_mem(addr, data):
    mem = open_mem(addr)
    offset = addr & 0xFFFF
    mem[offset] = data
    mem.close()

def read_mem(addr):
    mem = open_mem(addr)
    offset = addr & 0xFFFF
    val = mem[offset]
    mem.close()
    return val

def sw_handler():
    while(1):
        sw = read_mem(DIP_SW_ADDR)
        write_mem(RGB_LED_ADDR, SW_TO_RGB_LUT.get(sw & 0b111))

def led_pattern_gen():
    i = 1
    while(1):
        write_mem(GREEN_LED_ADDR, i)
        time.sleep(0.5)
        i <<= 1
        i %= 15


print("Entering forever loop.")
print("Use SW(3:0) to set RGB LEDs")
print("Strobing green LEDs in a fun pattern...")
# First start two thread tasks. Yes, this is overkill.
with concurrent.futures.ProcessPoolExecutor() as executor:
    task1 = executor.submit(sw_handler)
    task2 = executor.submit(led_pattern_gen)
    nc_1 = task1.result()
    nc_2 = task2.result()
    
    
