"""What GNU C's __sync_fetch_and_add_4(p, v) does, in Python.

memory is a row of bytes; each byte holds a whole number from 0 to 255.
p is a position in it. size is how many bytes, from p on, hold one number:
the _4 in __sync_fetch_and_add_4 is size 4. 
"""

memory = bytearray(4)       # 4 bytes, all 0


def read_number(p, size):
    # the number held in memory[p : p + size], the size bytes from p on.
    # The byte at p counts as it is, the next one times 256, the next one
    # times 256 * 256, and the next one times 256 * 256 * 256.
    number = 0
    for i in range(size):
        number = number + memory[p + i] * (256 ** i)
    return number


def write_number(p, size, number):
    # the number, put into memory[p : p + size], in the same order read_number reads it
    for i in range(size):
        memory[p + i] = (number // (256 ** i)) % 256


def fetch_and_add(p, size, v):
    old = read_number(p, size)      # the number at p, size bytes long
    total = old + v                 # the add
    kept = total % (256 ** size)    # what fits back into size bytes
    write_number(p, size, kept)     # the sum, written back at p
    return old                      # given back: the number as it was


# Threads A and B run at the same time, each on its own processor core. They
# share two files to work on, and next_file: the 4 bytes memory[0 : 4], the
# number of the next file nobody has taken. Python runs one line at a time,
# so the two threads' steps are written below in the order the cores did them.
files = ["a.txt", "b.txt"]

# 1. Without fetch_and_add: each thread takes a file by reading next_file,
# then writing next_file + 1.
write_number(0, 4, 0)                   # next_file = 0
a = read_number(0, 4)                   # A reads 0
b = read_number(0, 4)                   # B reads 0: A has not written yet
write_number(0, 4, a + 1)               # A writes 1
write_number(0, 4, b + 1)               # B writes 1
next_file = read_number(0, 4)
print(f"read, then write: A takes {files[a]}, B takes {files[b]}, next_file is {next_file}")

# 2. With fetch_and_add: each thread's read and write are one step, so B's
# step comes after A's, never between A's read and A's write.
write_number(0, 4, 0)                   # next_file = 0
a = fetch_and_add(0, 4, 1)              # A gets 0, and next_file becomes 1
b = fetch_and_add(0, 4, 1)              # B gets 1, and next_file becomes 2
next_file = read_number(0, 4)
print(f"fetch_and_add:    A takes {files[a]}, B takes {files[b]}, next_file is {next_file}")
