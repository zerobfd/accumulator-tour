# This implements the very simplest version of RSA signing
# In practice signing/encrypting is more sophisticated in order to prevent
# several types of errors and attacks, but the math is the same as what's
# happening here.

import sys

# First let's talk about the keys themselves. In RSA world, the three monster
# numbers below are the keys. Specifically, the public key is the (E, N) pair,
# and the private key is the (D, N) pair.
# Whatever action is taken using the public key is raising some data
# to the E power, modulus N
# The corresponding action taken using the private key is raising that result
# to the D power, modulus N.
# Why this works is way out of the scope of this repo, but for a taste of why
# it actually works: N here is generated by finding two really really big
# prime numbers and multiplying them together. Finding those two factors given
# N is really hard, even for computers. E and D are then chosen in a specific
# way so that for any X, X^(ed) = X mod N.

N = 0xDA3834CEB558DA1EBF9CF3FA1AAC132E35EA0A1BCBCDF435E4E7E9A89A994D8E173FC84FAAB78A66FDC0F2C15D13C6D1C7F07868232F330BE10016C05D435370A3CD339EC93E7630C987A42D22228DC10978FB36F2867AC5CCE89E84B09020103634FD8E4F05969AB2DBBFC1F8D5450FFDB8AA14B82870FB49A45A9FD0635A91
E = 0x010001
D = 0x0AB99A76D258E4978049618058513EBC15B04400EBBA5A974F81CA6D1BF40EE8BDE1C7A18ABD6C92F543C76A937D865707219D7958C95813EC6209BC3899377F897D451853EE1B69A1DD03D1BEFDCF64D7BE9A3EF0B1D8223F6606784EEBA5C43BC1D836D74655A478239E50FD20B6323AE429CDF0468CBFA2F5A0B3D5982FB1

# Math works best on numbers, so we need some way of representing whatever
# data we have as integers. It doesn't really matter what encoding we use
# here as long as it's consistent between the two.

def encode_string_as_int(s):
    return int.from_bytes(s.encode("ascii"), byteorder=sys.byteorder)

def decode_int_string(s):
    decoded_len = (s.bit_length() + 7) // 8
    return s.to_bytes(decoded_len, byteorder=sys.byteorder).decode("ascii")

# Let's define sign and verify

def verify(msg):
    msg = int(msg, 16)
    return decode_int_string(raise_to_e(msg))

def sign(msg):
    msg = encode_string_as_int(msg)
    s = raise_to_d(msg)
    return f"{s:x}"

def raise_to_d(i):
    return pow(i, D, N)

def raise_to_e(i):
    return pow(i, E, N)

# That's pretty much all of it. Most of the complexity is generating the keys
# (and figuring this out in the first place).
# Here's a simple way to lock/unlock via the CLI
if __name__ == "__main__":
    msg = sys.argv[2]
    if sys.argv[1] == "sign":
        print(sign(msg))
    if sys.argv[1] == "verify":
        print(verify(msg))
