from models import storage
from models.attacks import Attack
from models.attack_patterns import Pattern
from models.attackers import Attacker
from sqlalchemy import extract
import sqlalchemy
from datetime import datetime, timedelta
from ping import check_servers

import json

def attacks_since(units, num):
    if units is 'days':
        adjusted_time = (datetime.utcnow() - timedelta(days=num))
    elif units is 'hours':
        adjusted_time = (datetime.utcnow() - timedelta(hours=num))
    else:
        return
    results = storage.session.query(Attack).filter(Attack.timestamp > adjusted_time)
    return(results.count())

def total_attacks():
    results = storage.session.query(Attack).count()
    return(results)

def total_attack_patterns():
    results = storage.session.query(Pattern).count()
    return(results)

def top_clients():
    results = storage.session.query(Attacker).order_by(Attacker.count.desc()).limit(10)
    top_client_list = []
    for x in results:
        top_client_list += [{'ip': x.ip, 'count': x.count}]
    return top_client_list

def asn_count():
    asns = [value[0] for value in storage.session.query(Attacker.asn_country_code) if value[0] is not None]
    asn_list = []
    for value in set(asns):
        asn_list += [{'asn': value, 'count': storage.session.query(Attacker).filter(Attacker.asn_country_code == value).count()}]
    return(asn_list)

def parse_data():
    from models.results import Results
    last_results = storage.session.query(Results).order_by(Results.time_results_parsed.desc()).first()
    if last_results is not None:
        last_results_taken = last_results.time_results_parsed
    adjusted_time = (datetime.utcnow() - timedelta(minutes=1))
    if last_results is not None and last_results_taken > adjusted_time:
        print("Returning last results.")
        return(last_results)
    results = Results()
    storage.new(results)
    storage.save()
    print("Parsing new results.")
    return(results)

if __name__ == '__main__':
    parse_data()
