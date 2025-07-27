import csv, requests, time
from datetime import datetime

API_KEY = "C3XPUYU3ZU8N6ECYG9FWK3QEN8PNCV8C37"
CHAIN = 1

CONTRACTS = {
    'cDAI': '0x5d3a536E4d6dbd6114cc1ead35777bab948e3643',
    'cETH': '0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5'
}

def fetch_tokentx(wallet, contract):
    url = (
        f"https://api.etherscan.io/api?module=account&action=tokentx"
        f"&address={wallet}&contractaddress={contract}"
        f"&startblock=0&endblock=99999999&sort=asc&apikey={API_KEY}"
    )
    resp = requests.get(url).json()
    if resp.get('status') == '1':
        return resp['result']
    return []

def extract_features(wallet):
    feats = {'borrow_tx': 0, 'redeem_tx': 0, 'total_volume': 0}
    # cDAI token transfers approximate mint/redeem
    for token_symbol, addr in CONTRACTS.items():
        txs = fetch_tokentx(wallet, addr)
        for tx in txs:
            val = int(tx['value']) / (10 ** int(tx['tokenDecimal']))
            feats['total_volume'] += val
            # approximate logic: transfers from wallet = repay/redeem
            if tx['from'].lower() == wallet.lower():
                feats['redeem_tx'] += 1
            else:
                feats['borrow_tx'] += 1
        time.sleep(0.2)
    return feats

def compute_score(f):
    score = 1000
    if f['total_volume'] > 0:
        ratio = f['borrow_tx'] / (f['redeem_tx'] + 1e-9)
        score -= min(ratio * 300, 300)
    score -= min(f['redeem_tx'] * 50, 200)
    return max(0, int(score))

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

if __name__ == "__main__":
    main()
