# This is a simple implementation of a Merkle tree using the md5 function that
# we made earlier. 
from md5 import md5

class Node:
    def __init__(self, val="", left=None, right=None):
        self.hash = md5(val)
        self.left = left
        self.right = right


important_data = [
    "Say Ho",
    "(Ho)",
    "Say Ho Ho",
    "(Ho Ho)",
    "Say Ho Ho Ho",
    "(Ho Ho Ho)",
    "Now scream!",
    "(waooooo!)",
]

leaf_nodes = [Node(data) for data in important_data]

# We'll build the tree starting with the leaves and hashing them in pairs
# until we're only at 1 node. (I'm lazy so this only works of the number of
# nodes is a power of 2
def build_tree(list_of_data):
    cur = list_of_data

    while len(cur) > 1:
        next_level = []
        for i in range(len(cur)//2):
            l = cur[2*i]
            r = cur[2*i+1]
            val = l.hash + r.hash
            next_level.append(Node(l.hash + r.hash, l, r))
        cur = next_level

    return cur[0]

root = build_tree(leaf_nodes)


# Now let's validate the tree.

def validate_tree(root):
    stack = [root]
    while stack:
        cur = stack.pop()
        if cur is None or not cur.left:
            continue

        val = cur.left.hash +  cur.right.hash

        target_hash = md5(val)
        if target_hash != cur.hash:
            print(f"Failed validation! Wanted {cur.hash} got {target_hash}")
            return False

        stack.append(cur.left)
        stack.append(cur.right)

    print("Passed validation!")
    return True

validate_tree(root)
# This should have printed "Passed validation!"

# Let's fidget with some data and see if it still validates

leaf_nodes[0].hash = "Parappa comin' atcha"
validate_tree(root)

# This should have printed 
# "Failed validation! Wanted 90738f360feb773740705eef9a919e5a got 9842743baba713aadab974a1bc09a1d0"

# If you imagine that you're about to download a bunch of files from a server,
# you might first get the root hash:

root_hash = root.hash

# Now you download a bunch of stuff, but a message gets corrupted.

important_data = [
    "Say Ho",
    "(Ho)",
    "Say Ho Ho",
    "(Ho Ho)",
    #"Say Ho Ho Ho",
    "Say Ho Ho Ho Merry Xmas", # bit flip or something i dunno
    "(Ho Ho Ho)",
    "Now scream!",
    "(waooooo!)",
]

# We can build the tree ourselves and see if it checks out:

leaf_nodes = [Node(data) for data in important_data]

root_again = build_tree(leaf_nodes)

print(f"Got {root.hash} from server")
print(f"Computed {root_again.hash} locally")

# Well shoot. How do we know which one got an error?
# One way: we can ask the server for the left and right hashes for a node.
# Whichever one doesn't match, we ask for those children, and so on until we
# hit the leaf node that's wrong. For the purposes of this example, let's
# imagine that the order of the messages are the order of the leaf nodes, so
# we can look for the index of the mismatched hash and re-download that message.
# (turns out we can be fancy with bit manipulation)

def find_error_index(trusted_root, broken_root):
    if trusted_root.hash == broken_root.hash:
        print("The trees match!")
        return -1

    cur_trust = trusted_root
    cur_broke = broken_root
    path = 0

    while True:
        path <<= 1
        if cur_trust.left.hash != cur_broke.left.hash:
            cur_trust = cur_trust.left
            cur_broke = cur_broke.left
        else:
            path |= 1
            cur_trust = cur_trust.right
            cur_broke = cur_broke.right
        if not cur_trust.left:
            return path

i = find_error_index(root, root_again)

print(f"It looks like '{important_data[i]}' is the corrupted message!")

# Try changing the list at line 85 to swap where the corrupted message is, it
# should find it in log time!
