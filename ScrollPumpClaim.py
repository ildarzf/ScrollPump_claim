from config import chain_info, ZERO_ADDRESS, info_logo
from settings import *
import requests
from web3 import Web3
from loguru import logger
import random
import time
from fake_useragent import UserAgent
import uuid



def wallet():
    with open('wallets.txt', 'r') as f:
        wallets = f.read().splitlines()
        return wallets

def resfile_clean():
    with open("results.txt", "w") as file:
        pass

def get_gas():
    try:
        web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
        gas_price = web3.eth.gas_price
        gwei_gas_price = web3.from_wei(gas_price, 'gwei')
        return gwei_gas_price
    except Exception as error:
        return get_gas()

def wait_gas():
    while True:
        current_gas = get_gas()
        if current_gas > ACCEPTABLE_GWEI_BASE:
            logger.info(f'current gas in Ethereum : {current_gas} > {ACCEPTABLE_GWEI_BASE}')
            time.sleep(20)
        else:
            break


def get_reward_data(address, proxie, count_err):

        url = f"https://api.scrollpump.xyz/api/Airdrop/GetSign?address={address}"

        ua = UserAgent()
        headers = {
            "Content-Type": 'application/json',
            "User-Agent": ua.random,
            "referer": url,
            "baggage": (
                f"sentry-environment=vercel-production,"
                f"sentry-release=8db980a63760b2e079aa1e8cc36420b60474005a,"
                f"sentry-public_key=7ea9fec73d6d676df2ec73f61f6d88f0,"
                f"sentry-trace_id={uuid.uuid4()}"
            )
        }

        response = requests.get(url=url, headers = headers, proxies=proxie)
        if count_err < 3:
            count_err += 1
            # print(response.status_code)
            # print(response.json())
            if response.status_code != 200:
                time.sleep(1)
                get_reward_data(address, proxie,count_err)


        return response.json()



def claim(address, chain_from, amount, sign, proxie):

        abi = '[{"inputs":[{"internalType":"address","name":"_signer","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"OwnableInvalidOwner","type":"error"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"OwnableUnauthorizedAccount","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"inputs":[],"name":"BONUS_AMOUNT","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"BONUS_AMOUNT_REFERRER","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"signature","type":"bytes"},{"internalType":"address","name":"refUser","type":"address"}],"name":"claim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"claimReferralBonus","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"claimed","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"referralAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"referralBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"newBonusAmount","type":"uint256"}],"name":"setBonusAmount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"newBonusAmountReferrer","type":"uint256"}],"name":"setBonusAmountReferrer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newSignerAddress","type":"address"}],"name":"setSignerAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"signerAddress","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"token","outputs":[{"internalType":"contract SPumpMainToken","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
        claim_cont = web3.to_checksum_address('0xCe64dA1992Cc2409E0f0CdCAAd64f8dd2dBe0093')  # contract mint fun pass
        claimer = web3.eth.contract(address=claim_cont, abi=abi)
        account_addr = web3.eth.account.from_key(private_key).address

        if int(amount) > 0:


                tx = claimer.functions.claim(int(amount),sign, refUser
                                                ).build_transaction({
                    'from': account_addr,
                    'value': 0,  # web3.to_wei(0.00005, 'ether'),
                    'nonce': web3.eth.get_transaction_count(account_addr),
                    'maxFeePerGas': 0,
                    'maxPriorityFeePerGas': 0,
                    'gas': 0,

                })

                tx.update({'maxFeePerGas': int(web3.eth.gas_price * 1.05)})
                tx.update({'maxPriorityFeePerGas': int(web3.eth.gas_price * 1.05)})
                gasLimit = web3.eth.estimate_gas(tx)
                tx.update({'gas': gasLimit})

                signed_tx = web3.eth.account.sign_transaction(tx, private_key)

                tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

                tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

                if tx_receipt['status'] == 1:
                    logger.success(f'Claim - Tx hash: {chain_info[chain_from]["scan"]}/{tx_hash.hex()}')


                elif tx_receipt['status'] == 0:
                    logger.warning(f'Не удался Claim')
                    logger.warning(f'Tx hash: {chain_info[chain_from]["scan"]}/{tx_hash.hex()}')






if __name__ == "__main__":
    print(info_logo)
    resfile_clean()
    wallets = wallet()

    if shuffle:
        random.shuffle(wallets)

    num = 0


    for data in wallets:
        try:
            private_key, proxy = data.split(';')


            if proxy is not None and len(proxy) > 4 and proxy[:4] != 'http':
                proxy = 'http://' + proxy

            proxie = {'http': proxy, 'https': proxy} if proxy and proxy != '' else {}

            rpc = chain_info[chain_from]['rpc']

            web3 = Web3(Web3.HTTPProvider(rpc))
            address = web3.eth.account.from_key(private_key).address

            count_err = 0

            response = get_reward_data(address, proxie, count_err)
            success = response['success']
            message = response['message']
            amount = response['data']['amount']
            sign = response['data']['sign']

            balance_amount = web3.from_wei(int(amount), 'ether')

            with open("results.txt", "a") as file:
                file.write(str(address) +' : '+str(balance_amount)+ "\n")

            num= num+1
            wait_gas()
            logger.info(f'Реварда {balance_amount} PUMP  {address} Перехожу к клейму')

            time.sleep(3)

            try:
                claim(address, chain_from, amount, sign, proxie)
            except Exception as err:
                print(address + err)

            tm = random.randint(time_wait_wal[0], time_wait_wal[1])
            logger.info(f'Сплю {tm}')
            time.sleep(tm)
        except Exception as err:
           if 'ContractLogicError' in str(err):
               logger.info(f'Уже заклеймил. Перехожу к следующему действию')
           else:
               print(err)






