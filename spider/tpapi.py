import requests
import json

from .config import TRAVEL_PAYOUTS_TOKEN


headers = {"X-Access-Token": TRAVEL_PAYOUTS_TOKEN}

API_BASE = "http://api.travelpayouts.com/"

EP_LATEST = {"endpoint": "v2/prices/latest",
             "defaults": {"currency": "rub",
                          "page": 1,
                          "limit": 30,
                          "show_to_affiliates": "false",
                          "sorting": "price",
                          "trip_class": 0,
                          "period_type": "month",
                          "one_way": "false",
                          "beginning_of_period": "2017-12-1",
                          "origin": "MOW",
                          "destination": "BKK"
                          }
             }


def tp_request(endpoint, p={}):

    params = endpoint['defaults']
    params.update(p)

    api_request = API_BASE+endpoint['endpoint']+"?"+"&".join([k + '=' + str(v) for k, v in params.items()])

    try:
        response = requests.get(api_request, headers=headers)
    except requests.exceptions.ConnectionError:
        #print ("CONNECTION ERROR")
        return {"data": [], "params": params}

    return {"data": json.loads(response.text)['data'], "params": params}


def get_month_bids(p={}):
    return tp_request(EP_LATEST,p)
