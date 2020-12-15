# The structure of this file follows the ordering in RFC 2104
# which describes keyed-hashing for message authentication.
# It's done this way for ease of following along.
# See https://www.ietf.org/rfc/rfc2104.txt

# This implementation uses the MD5 hash in this repo for the hash.

from md5 import md5

# The relevant bit is section 2. Definition of HMAC.
# We know that we need a hash and a key. Our hash will be MD5 from the hash
# section, and we can choose our key at will.
# There are far fewer bits of information we need compared to the RFC that we
# used for MD5. We do need: B, the byte-length of blocks, which for us
# will be 64 (since MD5 operates on 512 bits at a time). There are also some
# magic constants with no particular semantic meaning, ipad and opad.
# It's also important to note that the key we use can be at most B bytes long,
# although the RFC gives us a method to handle that if the key is longer
# (just hash the key and use that instead)

B = 64
ipad = 0x36
opad = 0x5C

# The algorithm itself is pretty simple:
# H(K ^ opad, H(K ^ ipad, text))
# The rest is just applying the steps, so here we go!
def hmac_md5(text, key):
# We want everything to be bytes, not a string
    try:
        key = key.encode()
    except AttributeError:
        pass

# Step 0: hash the key if it's too long
    if len(key) > B:
        key = md5(key)

# Step 1: zero pad the key up to B.

    padded_key = bytearray(B)
    for i in range(len(key)):
        padded_key[i] = key[i]

# We'll need a copy of the key for later

    padded_key_copy = padded_key[:]

# Step 2: XOR padded key and ipad

    for i in range(B):
        padded_key[i] ^= ipad

# Step 3: append the text we want to HMAC to kipad
    
    kipad_text = padded_key + text.encode()

# Step 4: hash it!
    hkipad = md5(kipad_text)

# Step 5: XOR padded key and opad

    for i in range(B):
        padded_key_copy[i] ^= opad

# Step 6: append the inner hash result to kopad
    
    kopad_text = padded_key_copy + bytes.fromhex(hkipad)

# Step 7: hash it again!

    return md5(kopad_text)

# We'll take a string and then a key to run hmac on
# From the RFC: key="Jefe" text="what do ya want for nothing?" should
# print 750c783e6ab0b503eaa86e310a5db738
if __name__ == "__main__":
    import sys
    print(hmac_md5(sys.argv[1], sys.argv[2]))
