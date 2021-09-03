import requests
import hashlib
import random
from .config import URL_BASE

#api_base = 'https://business.tinkoff.ru/openapi/sandbox/api/v1/company'
api_base = 'https://rest-api-test.tinkoff.ru/v2'

ACCOUNT_NUMBER = '1111111111111'
TERMINAL_KEY = 'TinkoffBankTest'
TERMINAL_PASSWORD = 'TinkoffBankTest'

headers_base = {
    'Content-Type': 'application/json'
}

def calc_amount(summ: float) -> int:
    return int(summ * 100)

def generate_id():
    return random.randint(111111111111111111111, 9999999999999999999999999999)

def get_key(dictionary):
    keys = list(dictionary.keys())
    return keys[0]

def generate_request_token(data):
    data.append({'Password': TERMINAL_PASSWORD})
    data.sort(key = get_key)
    data_values = [str(list(d.values())[0]) for d in data]
    data_values = ["true" if x == "True" else x for x in data_values]
    values = ''.join(data_values)
    return hashlib.sha256(values.encode('utf-8')).hexdigest()

def get_payment_status(id):
    request_token = generate_request_token([{'TerminalKey': TERMINAL_KEY}, {'PaymentId': id}])

    data = {
        'TerminalKey': TERMINAL_KEY,
        'PaymentId': id,
        'Token': request_token
    }

    response = requests.post(
        '{}/GetState/'.format(api_base), 
        json = data,
        headers = headers_base
    )

    response_body = response.json()
    print(response_body)

    if response_body['Success']:
        return response_body['Status']

    return 'FAILED'

def init_first_payment(summ, customer_key):
    amount = calc_amount(summ)
    NOTIFICATION_URL = 'http://8736-185-48-37-99.ngrok.io/api/businesses/{}/payments/confirm'.format(customer_key)

    data = {
        'TerminalKey': TERMINAL_KEY,
        'Amount': amount,
        'OrderId': generate_id(),
        'PayType': 'T', # двустадийная оплата
        'Recurrent': 'Y', # автоплатёж
        'CustomerKey': customer_key,
        'SuccessURL': URL_BASE,
        'NotificationURL': NOTIFICATION_URL,
    }

    response = requests.post(
        '{}/Init/'.format(api_base), 
        json = data,
        headers = headers_base
    )

    response_body = response.json()

    if response_body['Success']:
        result = {
            'id': response_body['PaymentId'],
            'url': response_body['PaymentURL']
        }

        return result

    else:
        return init_payment(amount)

def init_auto_payment(summ, customer_key):
    amount = calc_amount(summ)
    NOTIFICATION_URL = 'http://8736-185-48-37-99.ngrok.io/api/businesses/{}/payments/confirm'.format(customer_key)

    data = {
        'TerminalKey': TERMINAL_KEY,
        'Amount': amount,
        'OrderId': generate_id(),
        'PayType': 'T', # двустадийная оплата
        'NotificationURL': NOTIFICATION_URL,
    }

    response = requests.post(
        '{}/Init/'.format(api_base), 
        json = data,
        headers = headers_base
    )
    print(response)

    response_body = response.json()
    print(response_body)

    if response_body['Success']:
        return response_body['PaymentId']

    else:
        return init_payment(amount)

def charge_auto_payment(payment_id, rebill_id):
    request_token = generate_request_token([{'TerminalKey': TERMINAL_KEY}, {'PaymentId': payment_id}, {'RebillId': rebill_id}])

    data = {
        'TerminalKey': TERMINAL_KEY,
        'PaymentId': payment_id,
        'RebillId': rebill_id,
        'Token': request_token
    }

    response = requests.post(
        '{}/Charge/'.format(api_base), 
        json = data,
        headers = headers_base
    )
    print(response)

    response_body = response.json()
    print(response_body)
    if response_body['Success']:
        return response_body['Status']

def perform_auto_payment(summ, business_id, rebill_id):
    payment_id = init_auto_payment(summ, business_id)
    charge_auto_payment(payment_id, rebill_id)
    return payment_id

def accept_payment(id, summ):
    amount = calc_amount(summ)
    request_token = generate_request_token([{'TerminalKey': TERMINAL_KEY}, {'PaymentId': id}, {'Amount': amount}])
    
    data = {
        'TerminalKey': TERMINAL_KEY,
        'PaymentId': id,
        'Amount': amount,
        'Token': request_token
    }

    response = requests.post(
        '{}/Confirm/'.format(api_base), 
        json = data,
        headers = headers_base
    )

    print(response)
    print(response.text)

def cancel_payment(id):
    request_token = generate_request_token([{'TerminalKey': TERMINAL_KEY}, {'PaymentId': id}])

    data = {
        'TerminalKey': TERMINAL_KEY,
        'PaymentId': id,
        'Token': request_token
    }

    response = requests.post(
        '{}/Cancel/'.format(api_base), 
        json = data,
        headers = headers_base
    )

    print(response)
    print(response.text)

if __name__ == '__main__':
    perform_auto_payment(1000, 1, 1626939304626)
    #init_auto_payment(1000, 1)
    #get_payment_status('800000279349')
    #charge_auto_payment('800000279352', 1626939304626)