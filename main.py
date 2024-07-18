from web3 import Web3
from ABI_config import ABI_Uniswap_v2_Pair, ABI_Uniswap_v2_Factory
from config import INFURA_ID

# Connecting to Ethereum node via Infura
infura_url = f'https://mainnet.infura.io/v3/{INFURA_ID}'
web3 = Web3(Web3.HTTPProvider(infura_url))

if not web3.is_connected():
    print("Failed to connect to Ethereum network")
    exit()

print("Connected to Ethereum network")
print("Current block number:", web3.eth.block_number)

# Uniswap v2 Contracts
uniswap_v2_factory_address = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'  # Uniswap V2 Factory Address
uniswap_v2_factory_abi = ABI_Uniswap_v2_Factory  # Uniswap V2 Factory ABI

# Connecting to Uniswap V2 Factory contract
uniswap_v2_factory = web3.eth.contract(address=uniswap_v2_factory_address, abi=uniswap_v2_factory_abi)

# Pools
pools = [
    '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc',  # ETH/USDC pool
    '0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11'  # ETH/DAI pool
]

# ABI for Uniswap V2 pair
pair_abi = ABI_Uniswap_v2_Pair  # Uniswap V2 Pair ABI


def get_liquidity_reserves(pool_address):
    pool_contract = web3.eth.contract(address=pool_address, abi=pair_abi)
    return pool_contract.functions.getLiquidityReserves().call()


def get_tokens(pool_address):
    pool_contract = web3.eth.contract(address=pool_address, abi=pair_abi)
    token0 = pool_contract.functions.token0().call()
    token1 = pool_contract.functions.token1().call()
    return token0, token1


def get_price(reserves, token0, token1):
    # Determine which token is WETH
    if token0 == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2':  # WETH
        reserve_eth = reserves[0]
        reserve_other = reserves[1]
    elif token1 == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2':  # WETH
        reserve_eth = reserves[1]
        reserve_other = reserves[0]
    else:
        raise ValueError("WETH token not found in the pool")

    if reserve_eth == 0:
        return 0

    return reserve_other / reserve_eth


# Get reserves and prices for two pools
reserves_pool1 = get_liquidity_reserves(pools[0])
reserves_pool2 = get_liquidity_reserves(pools[1])

tokens_pool1 = get_tokens(pools[0])
tokens_pool2 = get_tokens(pools[1])

# Print debug information
print(f"Reserves of the first pool: {reserves_pool1}")
print(f"Tokens of the first pool: {tokens_pool1}")

print(f"Reserves of the second pool: {reserves_pool2}")
print(f"Tokens of the second pool: {tokens_pool2}")

price_pool1 = get_price(reserves_pool1, tokens_pool1[0], tokens_pool1[1])
price_pool2 = get_price(reserves_pool2, tokens_pool2[0], tokens_pool2[1])

# Calculate the price difference in percentage
if price_pool1 == 0 or price_pool2 == 0:
    price_difference_percentage = 0
else:
    price_difference_percentage = abs(price_pool1 - price_pool2) / ((price_pool1 + price_pool2) / 2) * 100

# Print results
print(f"Address of the first pool: {pools[0]}")
print(f"Price in the first pool: {price_pool1:.6f} USDC/ETH")

print(f"Address of the second pool: {pools[1]}")
print(f"Price in the second pool: {price_pool2:.6f} DAI/ETH")

print(f"Price difference: {price_difference_percentage:.2f}%")

if price_difference_percentage > 0.5:
    print("Arbitrage opportunity possible!")
