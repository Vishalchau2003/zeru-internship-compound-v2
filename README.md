# 🧠 Wallet Risk Scorer on Compound Finance

This project analyzes user wallet activity on the Ethereum blockchain (specifically with Compound tokens like cDAI and cETH) and computes a **wallet risk score** based on borrow/redeem patterns.

## 📦 Overview

- **Blockchain**: Ethereum  
- **Tokens**: cDAI, cETH  
- **Data Source**: [Etherscan API](https://etherscan.io/apis)  
- **Output**: A CSV file containing wallet addresses and their respective risk scores.

---

## 📊 Methodology

### 📥 Data Collection Method

We use the **Etherscan Token Transfer API** to fetch all historical ERC-20 token transactions related to Compound's `cDAI` and `cETH` tokens for a given wallet. The API returns:
- Timestamp
- From/To addresses
- Token amount
- Block number
- Token metadata (decimals, name)

This allows us to determine user activity on the Compound protocol.

### 🎯 Feature Selection Rationale

For each wallet, we extract:
- `borrow_tx`: Number of token transfers **into** the wallet (proxy for borrow/mint)
- `redeem_tx`: Number of token transfers **from** the wallet (proxy for redeem/repay)
- `total_volume`: Total value of all cToken transactions in the wallet's history

These three features offer a rough but informative glimpse into user behavior on Compound.

### 🧮 Scoring Method

We assign a score out of 1000 using this logic:

- Start with 1000 points
- Penalize based on **borrow/redeem ratio** → higher ratio = riskier
- Penalize **high redeem activity** → potential aggressive withdrawals

```python
ratio = borrow_tx / (redeem_tx + 1e-9)
score = 1000 - min(ratio * 300, 300) - min(redeem_tx * 50, 200)
