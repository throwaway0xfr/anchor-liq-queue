from terra_sdk.client.lcd import LCDClient
from terra_sdk.core.auth.data.tx import StdFee
from terra_sdk.core.wasm import MsgExecuteContract
from terra_sdk.key.mnemonic import MnemonicKey

seed = ""

mm_liquidation_queue = "terra1e25zllgag7j9xsun3me4stnye2pcg66234je3u"
bluna_token = "terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp"
beth_token = "terra1dzhzukyezv0etz22ud940z7adyv7xgcjkahuun"

terra = LCDClient(chain_id="columbus-5", url="https://lcd.terra.dev")
mk = MnemonicKey(mnemonic=seed)
wallet = terra.wallet(mk)


def withdraw_collat(collat_token):
    fee = StdFee(982360, "147355uusd")
    exec_msg = MsgExecuteContract(
        wallet.key.acc_address,
        mm_liquidation_queue,
        {
            "claim_liquidations": {
                "collateral_token": collat_token,
            }
        },
    )
    execute_tx = wallet.create_and_sign_tx(msgs=[exec_msg], fee=fee)
    execute_tx_result = terra.tx.broadcast(execute_tx)
    print("Pending collat token claimed: " + str(execute_tx_result.txhash))


def get_queue_status(bidder):
    bluna_res = terra.wasm.contract_query(
        mm_liquidation_queue,
        {
            "bids_by_user": {
                "collateral_token": bluna_token,
                "bidder": bidder,
            }
        },
    )

    beth_res = terra.wasm.contract_query(
        mm_liquidation_queue,
        {
            "bids_by_user": {
                "collateral_token": beth_token,
                "bidder": bidder,
            }
        },
    )
    return (bluna_res, beth_res)


def main():
    if seed == "":
        print("Wallet seed required")
        return

    bluna_res, beth_res = get_queue_status(wallet.key.acc_address)

    if len(bluna_res["bids"]) > 0:
        pending_collat = int((bluna_res["bids"][0]["pending_liquidated_collateral"]))
        if pending_collat > 0:
            withdraw_collat(bluna_token)
        else:
            print("No pending bluna collateral")
    else:
        print("No bluna bids found")

    if len(beth_res["bids"]) > 0:
        pending_collat = int((beth_res["bids"][0]["pending_liquidated_collateral"]))
        if pending_collat > 0:
            withdraw_collat(beth_token)
        else:
            print("No pending beth collateral")
    else:
        print("No beth bids found")


if __name__ == "__main__":
    main()
