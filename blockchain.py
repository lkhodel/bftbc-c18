import streamlit as st

from dataclasses import astuple, dataclass
from typing import List

import datetime as datetime
import hashlib
import pandas as pd

@dataclass
class Record():
    sender: str
    receiver: str
    amount: float

@dataclass
class Block:
    creator_id: int
    record: Record
    nonce: int = 0
    prev_hash: str = "0"
    timestamp: str = datetime.datetime.utcnow().strftime("%H:%M:%S")

    def hash_block(self):
        return hashlib.sha256(\
            b''.join(str(field).encode() for field in astuple(self))
        ).hexdigest()

@dataclass
class Blockchain:
    chain: List[Block]
    difficulty: int = 4

    def append(self, candidate_block):
        self.chain.append(self.hash(candidate_block))

    def hash(self, block):
        calculated_hash = block.hash_block()
        num_of_zeros = "0" * self.difficulty

        while not calculated_hash.startswith(num_of_zeros):
            block.nonce += 1
            calculated_hash = block.hash_block()

        print("Winning hash:", calculated_hash)
        return block

    def is_valid(self):
        block_hash = self.chain[0].hash_block()

        for block in self.chain[1:]:
            if block_hash != block.prev_hash:
                print("Blockchain is invalid!")
                return False

            block_hash = block.hash_block()

        print("Blockchain is valid")
        return True

# Layout and initialization section follows
@st.cache(allow_output_mutation=True)
def setup():
    print("Initializing chain")
    return Blockchain([Block("Genesis", 0)])

blockchain = setup()

st.markdown("## Write transaction")
sender      = st.text_input("Source")
receiver    = st.text_input("Destination")
amount      = st.text_input("Quantity")

if st.button("Send"): # returns True if button was clicked on last run...
    prev_block = blockchain.chain[-1]
    prev_block_hash = prev_block.hash_block()
    new_block = Block(
        record=Record(sender, receiver, amount),
        creator_id=0,
        prev_hash=prev_block_hash
    )
    blockchain.append(new_block)
    st.balloons() # surprise!

st.markdown("## Ledger")

pychain_df = pd.DataFrame(blockchain.chain).astype(str)
st.write(pychain_df)

difficulty = st.sidebar.slider("Block difficulty", 1, 5, 2)
blockchain.difficulty = difficulty

st.sidebar.write("# Block viewer")
selected_block = st.sidebar.selectbox("Select block:", blockchain.chain)
st.sidebar.write(selected_block)
if st.button("Validate"):
    st.write(blockchain.is_valid())
