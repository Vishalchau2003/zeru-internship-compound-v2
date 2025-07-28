 Basic Terms

🔗 Blockchain

A blockchain is a decentralized digital ledger that records transactions across many computers. It's secure, transparent, and tamper-resistant. Each new set of transactions is added in a "block" and linked to the previous block — forming a chain.

🌐 Ethereum

Ethereum is a blockchain-based platform that allows developers to create and run smart contracts — self-executing programs that run on the blockchain. Ethereum has its own cryptocurrency called Ether (ETH).

🏦 Compound Protocol

Compound is a decentralized finance (DeFi) protocol built on Ethereum. It allows users to lend and borrow cryptocurrencies without intermediaries.

If you lend, you earn interest and receive cTokens.

If you borrow, you lock collateral and receive real tokens.

🪙 cDAI / cETH

When you lend tokens to Compound:

Lending DAI gives you cDAI

Lending ETH gives you cETH

These are called cTokens and represent your deposits in the protocol. They automatically increase in value over time as you earn interest.

🔁 Borrowing on Compound

When you borrow:

You supply collateral (e.g., ETH)

You borrow real tokens (like DAI)

You do NOT receive cTokens when borrowing

🧬 v2 vs v3

Compound has versions:

v2 is the current widely-used version.

v3 introduces new improvements such as:

Isolated lending markets

Improved risk management

Gas optimizations

This script interacts with v2 cTokens.

🧾 Full Code Explanation

import csv, requests, time
from datetime import datetime

csv: For reading/writing CSV files

requests: To call the Etherscan API

time: To avoid rate limits

datetime: Imported but not used

API_KEY = "<your_etherscan_api_key>"
CHAIN = 1

API_KEY: Your Etherscan API key

CHAIN = 1: Ethereum Mainnet (not used in this script)

CONTRACTS = {
    'cDAI': '0x5d3a536E4d6dbd6114cc1ead35777bab948e3643',
    'cETH': '0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5'
}

Contract addresses of cDAI and cETH — used to fetch transactions.

📡 fetch_tokentx(wallet, contract)

def fetch_tokentx(wallet, contract):
    url = (f"https://api.etherscan.io/api?module=account&action=tokentx"
           f"&address={wallet}&contractaddress={contract}"
           f"&startblock=0&endblock=99999999&sort=asc&apikey={API_KEY}")
    resp = requests.get(url).json()
    if resp.get('status') == '1':
        return resp['result']
    return []

Contacts Etherscan to get all token transfers involving a specific wallet and token.

Returns a list of transactions (if successful) or empty list.

📊 extract_features(wallet)

def extract_features(wallet):
    feats = {'borrow_tx': 0, 'redeem_tx': 0, 'total_volume': 0}
    for token_symbol, addr in CONTRACTS.items():
        txs = fetch_tokentx(wallet, addr)
        for tx in txs:
            val = int(tx['value']) / (10 ** int(tx['tokenDecimal']))
            feats['total_volume'] += val
            if tx['from'].lower() == wallet.lower():
                feats['redeem_tx'] += 1
            else:
                feats['borrow_tx'] += 1
        time.sleep(0.2)
    return feats

Loops through cDAI and cETH contracts

For each transaction:

Converts value to human-readable format

If the wallet is the sender → count as redeem

If the wallet is receiver → count as borrow

🧮 compute_score(f)

def compute_score(f):
    score = 1000
    if f['total_volume'] > 0:
        ratio = f['borrow_tx'] / (f['redeem_tx'] + 1e-9)
        score -= min(ratio * 300, 300)
    score -= min(f['redeem_tx'] * 50, 200)
    return max(0, int(score))

Everyone starts with 1000 points.

Penalties:

High borrow-to-redeem ratio: max -300 points

Many redeem transactions: max -200 points

Score never goes below 0.

🚀 main()

def main():
    with open("wallet.csv") as f:
        wallets = [row[0].strip() for row in csv.reader(f)]

    results = []
    for i, w in enumerate(wallets, 1):
        print(f"{i}/{len(wallets)}: Analyzing {w}")
        fdata = extract_features(w)
        score = compute_score(fdata)
        print(f" → Score: {score}")
        results.append({'wallet_id': w, 'score': score})
        time.sleep(0.5)

    with open("wallet_scores.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=['wallet_id', 'score'])
        writer.writeheader()
        writer.writerows(results)

    print("✅ wallet_scores.csv created!")

Reads wallet addresses from wallet.csv

For each wallet:

Fetches and analyzes activity

Calculates score

Saves results

Writes final scores to wallet_scores.csv

✅ Entry Point

if __name__ == "__main__":
    main()

Ensures the script runs when executed directly.

🧪 Sample Input (wallet.csv)

0x742d35Cc6634C0532925a3b844Bc454e4438f44e
0xfe9e8709d3215310075d67e3ed32a380ccf451c8

🧾 Sample Output (wallet_scores.csv)

wallet_id,score
0x742d35Cc6634C0532925a3b844Bc454e4438f44e,820
0xfe9e8709d3215310075d67e3ed32a380ccf451c8,940

🧠 Summary

You now understand Compound, cTokens, and Etherscan API.

This script helps score wallets based on borrow vs redeem behavior.

It is useful for trust scoring, whitelisting, or risk analysis in DeFi applications.

