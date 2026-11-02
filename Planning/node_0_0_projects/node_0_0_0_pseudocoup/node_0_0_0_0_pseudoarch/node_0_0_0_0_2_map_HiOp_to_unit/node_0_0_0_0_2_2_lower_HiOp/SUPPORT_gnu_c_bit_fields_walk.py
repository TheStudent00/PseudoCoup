"""What a GNU C bit-field is, and why its riscv64 words change with the
operator and with where the result goes, in Python. 

    struct Q { int a : 13; int b : 13; int r : 13; };

A bit-field is a holder that is only some of the bits of a number in memory.
a is bits 0 to 12 of the 4 bytes at q, and b is bits 13 to 25 of the same 4
bytes. r is bits 0 to 12 of the next 4 bytes, since 13 more bits do not fit
in the 6 left. Each holds a whole number from -4096 to 4095.

riscv64 has no instruction that reads or writes 13 bits. It reads the bytes
the field sits in, moves bits with shifts, and writes bytes back. Each line
in the three functions below does what the riscv64 words in its comment do.
The words are clang's, from run elv2_l146: int_add.c and int_div.c, the
functions f_bitfield_bitfield_bitfield and f_bitfield_bitfield_stack. The
words that load q from the stack frame are left out: here q is memory[0].
"""

memory = bytearray(8)       # struct Q: bytes 0 to 3 hold a and b, bytes 4 to 7 hold r


def read_number(p, size):
    # the number held in memory[p : p + size]: the byte at p counts as it is,
    # the next one times 256, the next one times 256 * 256, and so on
    number = 0
    for i in range(size):
        number = number + memory[p + i] * (256 ** i)
    return number


def write_number(p, size, number):
    # the number, put into memory[p : p + size], in the order read_number reads it
    for i in range(size):
        memory[p + i] = (number // (256 ** i)) % 256


def signed(number, bits):
    # number's lowest `bits` bits, read with a sign: if the top one of them
    # is 1, the number is negative (in 13 bits, 8185 reads as 8185 - 8192 = -7)
    kept = number % (2 ** bits)
    if kept >= 2 ** (bits - 1):
        kept = kept - (2 ** bits)
    return kept


def divide_toward_zero(x, y):
    # C's division of whole numbers: the fraction is dropped (1000 / -7 is -142.86, so -142)
    quotient = abs(x) // abs(y)
    if (x < 0) != (y < 0):
        quotient = -quotient
    return quotient


def show(name, number):
    # number's lowest 32 bits, top bit first, cut where struct Q cuts a and b
    text = ""
    for i in range(31, -1, -1):
        text = text + str((number // (2 ** i)) % 2)
        if i == 26 or i == 13:
            text = text + " "
    print(f"  {name:<7} {text}   {number}")


def write_r(total):
    # r = total: read the 2 bytes r sits in, keep their top 3 bits, put
    # total's lowest 13 bits below them, and write the 2 bytes back
    old = read_number(4, 2)                     # lhu  a0, 4(a1)
    r_bits = total % (2 ** 13)                  # c.slli a2, 51 ; c.srli a2, 51
    top_3 = (old // (2 ** 13)) * (2 ** 13)      # c.lui a3, 0xe ; c.and a0, a3
    write_number(4, 2, top_3 + r_bits)          # c.or a0, a2 ; sh a0, 4(a1)


def add_into_r():
    # q->r = q->a + q->b
    word = signed(read_number(0, 4), 32)        # c.lw a0, 0(a1): the 4 bytes holding a and b
    show("word", word)
    b_down = word // (2 ** 13)                  # srli a2, a0, 13: every bit moved down 13 places
    show("b_down", b_down)
    total = signed(word + b_down, 32)           # c.addw a2, a0: added as they are, a and b never taken out
    show("total", total)
    write_r(total)


def divide_into_r():
    # q->r = q->a / q->b
    word = signed(read_number(0, 4), 32)        # c.lw a2, 0(a1): the same 4 bytes
    a = signed(word, 13)                        # slli a0, a2, 51 ; c.srai a0, 51: a taken out, with its sign
    show("a", a)
    b = signed(word // (2 ** 13), 13)           # c.slli a2, 38 ; c.srai a2, 51: b taken out, with its sign
    show("b", b)
    total = divide_toward_zero(a, b)            # divw a2, a0, a2
    show("total", total)
    write_r(total)


def add_into_s_r():
    # s_r = q->a + q->b, where s_r is a plain int on the stack
    word = signed(read_number(0, 4), 32)        # c.lw a1, 0(a0)
    a = signed(word, 13)                        # slli a0, a1, 51 ; c.srai a0, 51: a taken out, with its sign
    show("a", a)
    b = signed(word // (2 ** 13), 13)           # slliw a1, a1, 6 ; sraiw a1, a1, 19: b taken out, with its sign
    show("b", b)
    s_r = signed(a + b, 32)                     # c.addw a0, a1 ; sw a0, -0x2c(s0): all 32 bits kept
    show("s_r", s_r)
    return s_r


# a = 1000 and b = -7, each put into its 13 bits of the 4 bytes at q
write_number(0, 4, (1000 % (2 ** 13)) + (-7 % (2 ** 13)) * (2 ** 13))
print("the 4 bytes at q:")
print("          unused b             a")
show("word", read_number(0, 4))

# 1. q->r = q->a + q->b: a and b are never taken out of their bytes. That is
# right, because only r's 13 bits are kept, and the lowest 13 bits of a sum
# come only from the lowest 13 bits of what is added.
print("1. q->r = q->a + q->b")
add_into_r()
print(f"  r = {signed(read_number(4, 2), 13)}")

# 2. q->r = q->a / q->b: the same places, another operator. Now a and b are
# taken out first, because a quotient depends on every bit and on the sign.
print("2. q->r = q->a / q->b")
divide_into_r()
print(f"  r = {signed(read_number(4, 2), 13)}")
word = read_number(0, 4)                        # the same division, on the bytes as they are:
write_r(divide_toward_zero(word, word // (2 ** 13)))
print(f"  without taking a and b out, r would be {signed(read_number(4, 2), 13)}, not -142")

# 3. s_r = q->a + q->b: the same operator as 1, the result kept whole. Now a
# and b are taken out first, because all 32 bits of the sum are kept.
print("3. s_r = q->a + q->b")
s_r = add_into_s_r()
print(f"  without taking a and b out, s_r would be {signed(word + word // (2 ** 13), 32)}, not 993")
