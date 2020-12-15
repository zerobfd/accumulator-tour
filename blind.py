from rsa import N, E, D, encode_string_as_int, decode_int_string, raise_to_e, raise_to_d, verify, sign
P = 0xF5B2E183392A27F85CBF274A24D2F07301B9619220AF0F6876D5128E2830F98086C5D7182F23615235DC885E8FB8E643D04677FC9DDC7B0764E4E44C707F684D
Q = 0xE35E6325E49C1B5FFBB6A162E2A43A76138E2A54B5CD7F8B788C5D485D4C4277B87D0FAD15B24A0AE8EBF245F7E0BC592A50AE12886A3D77EE2F50B216D91D55

# never never never never use the normal random package for anything actually
# related to crypto
from random import randrange

# Euler's totient function, easy since we know P and Q
# (used to compute an inverse mod N very quickly, not conceptually important)
tot = (P-1) * (Q-1)

# Assume here we're on the "client" side, and we want something signed
# by a "server"
# Pick a random number, find the inverse via Euler's theorem
r = randrange(N >> 10, N)
r_i = pow(r, tot - 1, N)

# Now we need to raise r^e, which is "verifying" it. (Encrypting, but w/e)
re = raise_to_e(r)

def blind_sign(msg):
    return raise_to_d(msg)

# We know already that sign() is the opposite of verify, so when the "server"
# signs re the result will be r. Now we mix re in with the message we want:

def blind(msg):
    msg = encode_string_as_int(msg)
    return (msg * re) % N

msg = "No true Scotsman"
blind_msg = blind(msg)

# Now we sent this message over to the server. The server has the private key,
# but has no idea what r, r_i, or re are. It can look at the message and sign
# it:
signed_blind_msg = blind_sign(blind_msg)

# Pretty much the only thing it can do is to send it back, so let's pretend
# we're back to the client side with the signed message. Now we need to remove
# the random stuff we multiplied in earlier. We already calculated the inverse,
# so now we just multiply by that:

def unblind(msg):
    return f"{msg * r_i % N:x}"

unblinded_signed_msg = unblind(signed_blind_msg)

# We end up with the signed message, which we can verify now to make sure that
# it matches what we originally sent:

if __name__ == "__main__":
    print("From server's point of view:")
    print("---")
    print(f"Received msg = {blind_msg:x}")
    print(f"Signed msg = {signed_blind_msg:x}")
    print("---")
    print("From client's point of view:")
    print("---")
    print(f"Verified signed message: {verify(unblinded_signed_msg)}")
    print(f"Received signed message post-unblinding: {unblinded_signed_msg}")
    print("---")
    print(f"If the server would have signed without blinding: {sign(msg)}")

# Sample output from running this file
# Note that these values will be different for each run, since r is random
# From server's point of view:
# ---
# Received msg = 849d2001ab31a78dd4069747bafbb88061db580cb87cfa41b1ddc8df67bedfbc11d80f070c1d09e2e879a657172da123799c67f5e0dbf22ab30d0531a2771283d270911d639f01c60a64fc8b3da89282c77157273313526e5e0309cd89849654cbb74d0bae96ceb174eb8fb724933db3f6d27aa513f423752177c2747a95386c
# Signed msg = 976978edfd27d3f8531b1b043d9f88f3d19aad2461ce6df6648bc1798701e16fce7043868394587f72b7a52093735b6b4e3b0dc3e93937c4b3b9fc1f785512c715e61f7d411e941670b8c8657ef2ffceccfdb196fd8d9ccb6d06ac93dc58797e3a855009de4d150db181051f4c15f2e7462b6f7845961d2b09ed407bbd925068
# ---
# From client's point of view:
# ---
# Verified signed message: No true Scotsman
# Received signed message post-unblinding: 1bac7ef2b36fa8afff4097e4c5f6670ce5e6cc4b291fe5f98642273cb354b7b0422d3b5dc3e01c975820296f4e4678f8f16d8fdcaf7ed4e89d3adad272a07edabba44c89c1c7d8152987c736d0c05db4b051f3bf060055b49fadb0ee122de4f69aa9d423c6ad86d9315f8db3908bd97a6267c3f22b6ecaa66fe4ebe0f36c21e6
# ---
# If the server would have signed without blinding: 1bac7ef2b36fa8afff4097e4c5f6670ce5e6cc4b291fe5f98642273cb354b7b0422d3b5dc3e01c975820296f4e4678f8f16d8fdcaf7ed4e89d3adad272a07edabba44c89c1c7d8152987c736d0c05db4b051f3bf060055b49fadb0ee122de4f69aa9d423c6ad86d9315f8db3908bd97a6267c3f22b6ecaa66fe4ebe0f36c21e6
