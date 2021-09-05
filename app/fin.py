import requests
import smtplib
from datetime import datetime, timedelta

fin_api_base = 'http://abf0-185-48-37-99.ngrok.io'
headers = {'Authorization': 'token'}

def create_wallet():
    response = requests.get(
        '{}/wallet/create'.format(fin_api_base),
        headers = headers
    )
    json = response.json()
    return json

def create_contract(id):
    response = requests.get(
        '{}/contract/create'.format(fin_api_base),
        params = {"id": id, "startTime": get_dt(datetime.now()), "endTime": get_dt(datetime.now() + timedelta(days=30)), "startShare": 100, "endShare": 0},
        headers = headers
    )
    json = response.json()
    print(json)
    return json

def get_amount(summ):
    return summ * 100

def get_dt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_acceptable_share(id):
    print(get_dt(datetime.now()))
    response = requests.get(
        '{}/contract/check'.format(fin_api_base),
        params = {'id': id, 'startTime': get_dt(datetime.now())},
        headers = headers
    )
    print(response)
    json = response.json()
    print(json)
    return json

def deposit_money(address, summ):
    amount = get_amount(summ)
    response = requests.get(
        '{}/send'.format(fin_api_base),
        params = {'address': address, 'amount': amount},
        headers = headers
    )
    json = response.json()
    return json

if __name__ == "__main__":
    #create_wallet()
    #create_contract(1)
    get_acceptable_share(1)