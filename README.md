# Introduction

The client server is for corporate users to manage wallets of individual users. The server is also the communication portal between users and SPC payload. When users initiate transactions, the transaction files will be encryted by the client server and sent to SPC payload.


# Functions

#### Obtain satellite public keys
User can create a 2-3 multisignature wallet with Electrum software. Apart from approving a transaction by a user, SPC payload needs to make a second authorization of the transaction with its public key. The satellite public keys are randomly assigned to each corporate user during the wallet registration.

Please refer to the below document for the introduction of SPC Electrum software：
https://github.com/spacechain/opensource_client

#### Call API
The API contains functions for wallet creation, transaction initiation, identity verification. The API are called by corporate user’s Electrum software.

#### Encrypt and compress transaction files
When a wallet user calls API, the first signature signed by the user is stored in the server. Corporate users need to encrypt the transaction details with an OTP. The encrypted transactions are sent to the FTP server and await the second authentication from the SPC payload.

#### Download and broadcast transactions from SPC payload
SPC server regularly checks for new transactions files that have been authenticated by the SPC payload. These transaction files will be automatically downloaded and broadcasted to the blockchain network.

