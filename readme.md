# Blockchain based chatroom application

This repository contains the implementation of blockchain its usage in building a chatroom.

The following features have been implemented in the blockchain:
- createBlock() method creates a block with the given data.
- mineBlock() method finds the nonce value required to create a new block and adds it to the blockchain.
- verifyTransaction() method uses zero knowledge proof with discrete log mathematics to verify the identity of a user who makes a transaction (in this case, sending a message).
- viewUser() method in server.py returns all transactions (messages) associated with a particular user.

- /replace_chain endpoint is used to ensure blockchains in all other nodes are updated when a new block is mined.
- /get_chain endpoint returns the blockchain in json format

