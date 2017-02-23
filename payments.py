import hashlib
import json
import uuid
from base64 import decodebytes, encodebytes
from datetime import datetime
from urllib.parse import quote_plus

import lxml.etree
import requests
from Crypto.Hash import SHA, SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from lxml.builder import E

from config import Config


def _timestamp_from_datetime(dt):
    epoch = datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds())


class AliPayAgent(object):
    __REFUND_GATEWAY = "https://openapi.alipaydev.com/gateway.do"

    def __init__(self):
        """
        # app, wap支付:
        alipay = AliPay(
          app_notify_url="", appid="", app_private_key_path="", app_alipay_public_key_path=""
        )
        # web支付:
        alipay = AliPay(
          web_notify_url="", partner="", partner_private_key_path="", partner_alipay_public_key_path=""
        )
        # 如果你想要同时支持三种支付方式，将所有参数传入
        """

        self.__appid = Config.ALIPAY_PARTNER_ID
        self.__app_notify_url = Config.ALIPAY_NOTIFY_URL
        self.__app_private_key_path = Config.ALIPAY_PRIVATE_KEY
        self.__app_alipay_public_key_path = Config.ALIPAY_PUBLIC_KEY
        self.__sign_type = "RSA2"

    def __ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def __check_internal_configuration(self, paid_type):
        if paid_type in ("wap", "app"):
            assert self.__appid, "appid is not configured"
            assert self.__app_notify_url, "app_notify_url is not configured"
            assert self.__app_private_key_path, "app_private_key_path is not configured"
            assert self.__app_alipay_public_key_path, "app_alipay_public_key_path is not configured"

    def _sign(self, unsigned_string, private_key_path):
        """
        通过如下方法调试签名
        方法1
            key = rsa.PrivateKey.load_pkcs1(open(self.__private_key_path).read())
            sign = rsa.sign(unsigned_string.encode("utf8"), key, "SHA-1")
            # base64 编码，转换为unicode表示并移除回车
            sign = base64.encodebytes(sign).decode("utf8").replace("\n", "")
        方法2
            key = RSA.importKey(open(self.__private_key_path).read())
            signer = PKCS1_v1_5.new(key)
            signature = signer.sign(SHA.new(unsigned_string.encode("utf8")))
            # base64 编码，转换为unicode表示并移除回车
            sign = base64.encodebytes(signature).decode("utf8").replace("\n", "")
        方法3
            echo "abc" | openssl sha1 -sign alipay.key | openssl base64

        """
        # 开始计算签名
        with open(private_key_path) as fp:
            key = RSA.importKey(fp.read())
            signer = PKCS1_v1_5.new(key)
            if self.__sign_type == "RSA":
                signature = signer.sign(SHA.new(unsigned_string.encode("utf8")))
            else:
                signature = signer.sign(SHA256.new(unsigned_string.encode("utf8")))
            # base64 编码，转换为unicode表示并移除回车
            sign = encodebytes(signature).decode("utf8").replace("\n", "")
            return sign

    def sign_data_with_private_key(self, data, private_key_path):
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.__ordered_data(data)
        unsigned_string = "&".join("{}={}".format(k, v) for k, v in unsigned_items)
        return self._sign(unsigned_string, private_key_path)

    def create_app_trade(self, out_trade_no, total_amount, subject):
        self.__check_internal_configuration("app")

        data = {
            "app_id": self.__appid,
            "method": "alipay.trade.app.pay",
            "charset": "utf-8",
            "sign_type": self.__sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": self.__app_notify_url,
            "biz_content": {
                "subject": subject,
                "out_trade_no": out_trade_no,
                "total_amount": total_amount,
                "product_code": "QUICK_MSECURITY_PAY"
            }
        }

        return self.create_trade(data, self.__app_private_key_path)

    def create_wap_trade(self, out_trade_no, total_amount, subject, return_url):
        self.__check_internal_configuration("wap")

        data = {
            "app_id": self.__appid,
            "method": "alipay.trade.wap.pay",
            "format": "JSON",
            "return_url": return_url,
            "charset": "utf-8",
            "sign_type": self.__sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": self.__app_notify_url,
            "biz_content": {
                "subject": subject,
                "out_trade_no": out_trade_no,
                "total_amount": total_amount,
                "product_code": "QUICK_MSECURITY_PAY"
            }
        }
        return self.create_trade(data, self.__app_private_key_path)

    def create_trade(self, data, private_key_path):
        sign = self.sign_data_with_private_key(data, private_key_path)
        ordered_items = self.__ordered_data(data)
        quoted_string = "&".join("{}={}".format(k, quote_plus(v)) for k, v in ordered_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def verify_app_notify(self, data, signature):
        return self.verify_notify(data, signature, self.__app_alipay_public_key_path)

    def verify_wap_notify(self, data, signature):
        return self.verify_app_notify(data, signature)

    def _verify(self, raw_content, signature, publickey_path):
        # 开始计算签名
        with open(publickey_path) as fp:
            key = RSA.importKey(fp.read())
            signer = PKCS1_v1_5.new(key)
            if self.__sign_type == "RSA":
                digest = SHA.new()
            else:
                digest = SHA256.new()
            digest.update(raw_content.encode("utf8"))
            if signer.verify(digest, decodebytes(signature.encode("utf8"))):
                return True
            return False

    def verify_notify(self, data, signature, alipay_public_key_path):
        # 排序后的字符串
        unsigned_items = self.__ordered_data(data)
        message = "&".join("{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature, alipay_public_key_path)


class NeoTenpayAgent(object):
    def __init__(self):
        self.partner_id = Config.WEIXIN_MCH_ID
        self.partner_key = Config.WEIXIN_MCH_KEY
        self.app_id = Config.WEIXIN_APP_ID
        self.notify_url = Config.WEIXIN_NOTIFY_URL
        self.session = requests.Session()

    def generate_params(self, user_id, order_no,
                        item_name, item_description, price):
        params = {
            'body': item_name,
            'fee_type': 'CNY',
            'notify_url': self.notify_url,
            'out_trade_no': order_no,
            'mch_id': self.partner_id,
            'spbill_create_ip': '196.168.1.1',
            'total_fee': str(price),
            'appid': self.app_id,
            'nonce_str': uuid.uuid4().hex,
            'trade_type': 'APP',
        }
        chunk = '&'.join(
                '{}={}'.format(k, v)
                for k, v in sorted(params.items())
        )
        chunk += '&key=' + self.partner_key
        params['sign'] = hashlib.md5(chunk.encode('utf-8')).hexdigest().upper()

        xml_params = E.xml(
                E.body(params['body']),
                E.fee_type(params['fee_type']),
                E.notify_url(params['notify_url']),
                E.out_trade_no(params['out_trade_no']),
                E.mch_id(params['mch_id']),
                E.spbill_create_ip(params['spbill_create_ip']),
                E.total_fee(params['total_fee']),
                E.appid(params['appid']),
                E.nonce_str(params['nonce_str']),
                E.sign(params['sign']),
                E.trade_type(params['trade_type']),
        )
        data = lxml.etree.tostring(xml_params, encoding='utf-8')
        page = self.session.post(
                'https://api.mch.weixin.qq.com/pay/unifiedorder',
                data=data,
        )
        page.encoding = 'utf-8'
        resp = lxml.etree.fromstring(page.text)
        if resp.xpath('/xml/err_code/text()'):
            for item in resp.xpath('/xml/err_code/text()'):
                err_code = item
            for item in resp.xpath('/xml/err_code_des/text()'):
                err_code_des = item
                if err_code == 'ORDERPAID':
                    # 订单已支付，无需再次尝试
                    raise ValueError(err_code_des)
            else:
                raise Exception('({}) {}'.format(
                        err_code, err_code_des
                ))
        # 调起支付的参数
        for item in resp.xpath('/xml/prepay_id/text()'):
            params = {
                'appid': params['appid'],
                'noncestr': params['nonce_str'],
                'package': 'Sign=WXPay',
                'partnerid': self.partner_id,
                'prepayid': item,
                'timestamp': _timestamp_from_datetime(datetime.now()),
            }
        chunk = '&'.join(
                '{}={}'.format(k, v)
                for k, v in sorted(params.items())
        )
        chunk += '&key=' + self.partner_key
        params['sign'] = hashlib.md5(
                chunk.encode('utf-8')
        ).hexdigest().upper()

        return params

    def verify(self, params):
        params = lxml.etree.fromstring(params)
        if not params.xpath('/xml/sign/text()'):
            raise ValueError('参数 sign 不存在')

        # 值为空的字段不参与签名
        sign_params = {}
        for item in params.xpath('/xml')[0]:
            if item.tag not in ['sign'] and item.text:
                sign_params[item.tag] = item.text
        chunk = '&'.join(
                '{}={}'.format(
                        k.decode('utf-8') if isinstance(k, str) else k,
                        v.decode('utf-8') if isinstance(v, str) else v,
                )
                for k, v in sorted(sign_params.items())
        )
        chunk = (chunk + '&key=' + self.partner_key).encode('utf-8')
        signature = hashlib.md5(chunk).hexdigest().upper()
        if params.xpath('/xml/sign/text()')[0] != signature:
            raise ValueError('签名不正确')
