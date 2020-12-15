# The structure of this file follows the ordering in RFC 1321 section 3
# which describes the MD5 algorithm, instead of the normal structure of
# a Python file. It's done this way for ease of following along.
# See https://www.ietf.org/rfc/rfc1321.txt

# 3.1 Append Padding Bits

def bitcount(m):
    return len(m) * 8

def pad(m):
    # Messages are padded s.t. they are 64 bits away from being a multiple
    # of 512 bits long, congruent to 448 % 512
    m_len = bitcount(m) % 512
    if m_len >= 448:
        m_len -= 512
    pad_bits = 448 - m_len
    pad_bytes = pad_bits // 8
    pad = bytearray(pad_bytes)

    # > a single "1" bit is appended, and then "0" bits
    # bytearrays are zero-filled, so we just need to fix the first one

    pad[0] = 128 # 10000000 in binary

    return m + pad

# 3.2 Append Length

def append_length(m, original_len):
    # 64 bits = 8 bytes, and the RFC specifies the low order bits
    return m + original_len.to_bytes(8, byteorder="little")

# 3.3 Initialize buffer

def init_buffer():
    # The hash works on 4 32-bit buffers that start with specified values
    # I'll write the values all on one line to make it apparent, but the
    # specified values have no particular significance, it's just counting
    # to 16 and back.

    init_val = "0123456789abcdeffedcba9876543210"
    buffer = [None, None, None, None]
    buffer[0] = bytearray.fromhex(init_val[:8])
    buffer[1] = bytearray.fromhex(init_val[8:16])
    buffer[2] = bytearray.fromhex(init_val[16:24])
    buffer[3] = bytearray.fromhex(init_val[24:32])

    return [int.from_bytes(x, byteorder="little") for x in buffer]

# 3.4 Process Message in 16-Word Blocks

# Here are the three functions that take 3 words and produce one word
# This is where a lot of the "diffusion" happens in MD5--in these functions
# all of the bits of the answer depend on all bits of the input, so changing
# any one of them will change the answer.

def F(X, Y, Z):
    return (X & Y) | (~X & Z)

def G(X, Y, Z):
    return (X & Z) | (Y & ~Z)

def H(X, Y, Z):
    return X ^ Y ^ Z

def I(X, Y, Z):
    return Y ^ (X | ~Z) 

# Here the RFC describes a 64 entry table where the ith entry is 4294967296
# times the absolute value of the sine of i in radians. Luckily the RFC has
# calculated all of these already and put them in the appendix, so we'll just
# include them here. A lot of hashes include these sorts of numbers (trig functions,
# irrational numbers, etc.) to start out with something that looks "random" from
# the beginning.

T = [
0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x2441453,  0xd8a1e681, 0xe7d3fbc8,
0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x4881d05,  0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
]

# The rest of it is the actual work, so let's start the function
def md5(message):
# Let's get our initial values set up
    a, b, c, d = init_buffer()

# In case it's a string, turn it into bytes
    try:
        message = message.encode()
    except AttributeError:
        pass

# Pad the message and append the length
    padded_message = pad(message)
    padded_message = append_length(padded_message, bitcount(message))

# The next part looks a bit crazy, so let's break it down.
# MD5 can process messages of arbitrary length, but we do it in 512 bit chunks.
# So the outer loop is, "for every 512 bit chunk in the message."
# The next loop is just breaking up that chunk into 16 smaller chunks.
# 32 * 16 = 512 bits, which is good since our buffers are 32 bits!

    num_big_chunks = bitcount(padded_message) // 512

# Now we get this piece of work:
# Let [abcd k s i] denote the operation a = b + ((a + F(b,c,d) + X[k] + T[i]) <<< s).
# That just means we have a function of 7 values. The first four are the buffer
# registers that we're working on, and k, s, and i are the offsets for the
# 32 bit chunk of the 512-bit chunk we're working on (the outer loop), the table T
# above, and a rotation. Looking above at section 2 Terminology and Notation, we see
# X <<< s signifies "the 32-bit value obtained by circularly shifting (rotating)
# X left by s bit positions." Python doesn't really have something like that, so let's
# just say we're going to make a helper function later and call it "rotate".

# If you peek ahead, you see that after the first "round" of operations, the function
# changes--it's the same thing, except instead of F we use G, then H, then I. Since we
# also need to pass in the actual part of the message we're processing, X,
# it's a function of 9 variables where one is the function to be called. Let's write that
# function later and call it "round".

# With that done it's just a matter of writing down all of these calls, so let's get to it

    for i in range(num_big_chunks):
        # Split the 512 bit chunk into 4 byte pieces
        chunk = padded_message[i*64:i*64+64]
        X = [int.from_bytes(chunk[j*4:(j+1)*4], byteorder="little") for j in range(16)]
# Before we start processing, we save the current values of the registers for later
        aa = a
        bb = b
        cc = c
        dd = d


# Round 1
        a = round(a, b, c, d, F, X, 0,  7,  1)
        d = round(d, a, b, c, F, X, 1,  12, 2)
        c = round(c, d, a, b, F, X, 2,  17, 3)
        b = round(b, c, d, a, F, X, 3,  22, 4)
        a = round(a, b, c, d, F, X, 4,  7,  5)
        d = round(d, a, b, c, F, X, 5,  12, 6)
        c = round(c, d, a, b, F, X, 6,  17, 7)
        b = round(b, c, d, a, F, X, 7,  22, 8)
        a = round(a, b, c, d, F, X, 8,  7,  9)
        d = round(d, a, b, c, F, X, 9,  12, 10)
        c = round(c, d, a, b, F, X, 10, 17, 11)
        b = round(b, c, d, a, F, X, 11, 22, 12)
        a = round(a, b, c, d, F, X, 12, 7,  13)
        d = round(d, a, b, c, F, X, 13, 12, 14)
        c = round(c, d, a, b, F, X, 14, 17, 15)
        b = round(b, c, d, a, F, X, 15, 22, 16)

# Let's look at this one round. You can see that every word in the buffer is
# getting mixed together with every other word multiple times, which increases
# the diffusion. Diffusion is a property of good hash functions, where changing
# any bit of the input should change every bit of the output with probability
# 0.5. i just steadily goes up by one here, and will continue to do so throughout
# the remaining rounds. All of the values in the table are different so there's
# no real reason to do anything fancy with the order.

# The amount of bits that we rotate switches between some values--the exact
# values aren't too important, but an important function here is that the
# rotation is changing what bits # depend on other bits! If we didn't rotate,
# then the first bit of a would # only ever interact with the first bits of
# b, c, and d. This isn't good--we'd like each bit to touch 511 other bits,
# not just 3. So, while the values themselves aren't too important, it IS
# important to pick values over the entire hash process to have every position
# of each word interact with as many other positions in other words as possible.

# Enough talk, let's get on with it.

# Round 2
        a = round(a, b, c, d, G, X, 1,  5,  17)
        d = round(d, a, b, c, G, X, 6,  9,  18)
        c = round(c, d, a, b, G, X, 11, 14, 19)
        b = round(b, c, d, a, G, X, 0,  20, 20)
        a = round(a, b, c, d, G, X, 5,  5,  21)
        d = round(d, a, b, c, G, X, 10, 9,  22)
        c = round(c, d, a, b, G, X, 15, 14, 23)
        b = round(b, c, d, a, G, X, 4,  20, 24)
        a = round(a, b, c, d, G, X, 9,  5,  25)
        d = round(d, a, b, c, G, X, 14, 9,  26)
        c = round(c, d, a, b, G, X, 3,  14, 27)
        b = round(b, c, d, a, G, X, 8,  20, 28)
        a = round(a, b, c, d, G, X, 13, 5,  29)
        d = round(d, a, b, c, G, X, 2,  9,  30)
        c = round(c, d, a, b, G, X, 7,  14, 31)
        b = round(b, c, d, a, G, X, 12, 20, 32)

# i keeps going up, the rotation sticks with the same buffer again but changes
# a bit, and which 32 bit chunk of the message we're looking at is a completely
# different order. Round 3 and 4 are similar.

# Round 3
        a = round(a, b, c, d, H, X, 5,  4,  33)
        d = round(d, a, b, c, H, X, 8,  11, 34)
        c = round(c, d, a, b, H, X, 11, 16, 35)
        b = round(b, c, d, a, H, X, 14, 23, 36)
        a = round(a, b, c, d, H, X, 1,  4,  37)
        d = round(d, a, b, c, H, X, 4,  11, 38)
        c = round(c, d, a, b, H, X, 7,  16, 39)
        b = round(b, c, d, a, H, X, 10, 23, 40)
        a = round(a, b, c, d, H, X, 13, 4,  41)
        d = round(d, a, b, c, H, X, 0,  11, 42)
        c = round(c, d, a, b, H, X, 3,  16, 43)
        b = round(b, c, d, a, H, X, 6,  23, 44)
        a = round(a, b, c, d, H, X, 9,  4,  45)
        d = round(d, a, b, c, H, X, 12, 11, 46)
        c = round(c, d, a, b, H, X, 15, 16, 47)
        b = round(b, c, d, a, H, X, 2,  23, 48)

# Round 4
        a = round(a, b, c, d, I, X, 0,  6,  49)
        d = round(d, a, b, c, I, X, 7,  10, 50)
        c = round(c, d, a, b, I, X, 14, 15, 51)
        b = round(b, c, d, a, I, X, 5,  21, 52)
        a = round(a, b, c, d, I, X, 12, 6,  53)
        d = round(d, a, b, c, I, X, 3,  10, 54)
        c = round(c, d, a, b, I, X, 10, 15, 55)
        b = round(b, c, d, a, I, X, 1,  21, 56)
        a = round(a, b, c, d, I, X, 8,  6,  57)
        d = round(d, a, b, c, I, X, 15, 10, 58)
        c = round(c, d, a, b, I, X, 6,  15, 59)
        b = round(b, c, d, a, I, X, 13, 21, 60)
        a = round(a, b, c, d, I, X, 4,  6,  61)
        d = round(d, a, b, c, I, X, 11, 10, 62)
        c = round(c, d, a, b, I, X, 2,  15, 63)
        b = round(b, c, d, a, I, X, 9,  21, 64)

# Finally at the end of each 512 bit block, we take the values we saved way at
# the beginning of the loop and add them again. Let's also make sure that we
# don't go over 32 bits.

        a += aa
        b += bb
        c += cc
        d += dd
        a &= 0xFFFFFFFF
        b &= 0xFFFFFFFF
        c &= 0xFFFFFFFF
        d &= 0xFFFFFFFF

# And after we process everything, we're done! Almost. We still have:
# 3.5 Output
# We start with the *low* order byte of A, then the *high* order byte of A,
# then do the same for B, C, and D. Just for convenience, we'll also output
# everything as a hexadecimal string. Since every 2 characters in hex is
# one byte, we can just take every two characters and reverse it that way.

    a_hex = f"{a:0{8}x}"
    b_hex = f"{b:0{8}x}"
    c_hex = f"{c:0{8}x}"
    d_hex = f"{d:0{8}x}"

    output = []

    for part in (a_hex, b_hex, c_hex, d_hex):
        output.append(part[6])
        output.append(part[7])
        output.append(part[4])
        output.append(part[5])
        output.append(part[2])
        output.append(part[3])
        output.append(part[0])
        output.append(part[1])

    return ''.join(output)

# Finally, we need to go back and write those helper functions. First, one
# that will rotate a number around some number of bits. We also need to make
# sure the output is only 32 bits.

def rotate(x, s):
    x &= 0xFFFFFFFF
    return ((x << s) | (x >> (32 - s))) & 0xFFFFFFFF

# Now finally, we define round by just copying from the RFC.
def round(a, b, c, d, func, X, k, s, i):
    return (b + (rotate((a + func(b, c, d) + X[k] + T[i-1]), s)))

# Let's take an argument from the CLI and hash it
if __name__ == "__main__":
    import sys
    print(md5(sys.argv[1]))
