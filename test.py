from alipay import AliPay
#
# from config import Config
#
# alipay = AliPay(appid=Config.ALIPAY_PARTNER_ID, app_private_key_path=Config.ALIPAY_PRIVATE_KEY,
#                 app_alipay_public_key_path=Config.ALIPAY_PUBLIC_KEY, sign_type='RSA2',
#                 app_notify_url=Config.ALIPAY_NOTIFY_URL)
#
# order_string = alipay.create_app_trade(out_trade_no="201611121111", total_amount="0.01", subject="testing order")
#
if __name__ == '__main__':
    import string
    import random
    order_id = [random.choice(string.digits) for _ in range(12)]
    order_id = ''.join(order_id)
    from payments import NeoTenpayAgent
    tenpay = NeoTenpayAgent()
    order_string = tenpay.generate_params(user_id='', order_no=order_id, item_name='qwert', item_description='zxcvb', price=1)
    print(order_string)
    from payments import AliPayAgent
    alipay = AliPayAgent()
    orderString = alipay.create_app_trade(out_trade_no=order_id, total_amount="0.01", subject="testing order")
    print(orderString)






