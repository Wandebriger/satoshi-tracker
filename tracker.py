import requests
import time
from datetime import datetime, timedelta
from tqdm import tqdm

BLOCKSTREAM_API = "https://blockstream.info/api"

def get_recent_blocks(count=10):
    response = requests.get(f"{BLOCKSTREAM_API}/blocks")
    response.raise_for_status()
    return response.json()[:count]

def get_block_transactions(block_hash):
    response = requests.get(f"{BLOCKSTREAM_API}/block/{block_hash}/txs")
    response.raise_for_status()
    return response.json()

def is_wallet_old(address, years=5):
    # get transactions for address
    response = requests.get(f"{BLOCKSTREAM_API}/address/{address}/txs")
    if response.status_code != 200:
        return False
    txs = response.json()
    if not txs:
        return False
    oldest_tx = txs[-1]
    oldest_time = datetime.fromtimestamp(oldest_tx['status']['block_time'])
    age = datetime.now() - oldest_time
    return age >= timedelta(days=365 * years)

def analyze_block_for_old_wallets(block, years=5):
    txs = get_block_transactions(block['id'])
    old_wallets = []
    for tx in txs:
        if 'vin' not in tx:
            continue
        for vin in tx['vin']:
            if 'prevout' in vin and 'scriptpubkey_address' in vin['prevout']:
                address = vin['prevout']['scriptpubkey_address']
                if is_wallet_old(address, years=years):
                    old_wallets.append((address, tx['txid']))
    return old_wallets
