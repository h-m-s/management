#!/usr/bin/python3
"""
"""
from flask import Flask, render_template
from parse import parse_data
from models import storage
from datetime import datetime
import json
import pytz
app = Flask(__name__)

@app.route('/')
def display_information():
    results = parse_data()
    ping_results = json.loads(results.ping_results)
    timestamp = str(utc_to_local(results.time_results_parsed.timestamp()))
    timestamp = timestamp[:timestamp.find('.')]
    return render_template("index.html",
                           timestamp=timestamp,
                           last_24_hrs=results.last_24_hrs,
                           last_week=results.last_week,
                           last_hour=results.last_hr,
                           last_month=results.last_month,
                           total_patterns=results.total_attack_patterns,
                           total_attacks=results.total,
                           top_clients=json.loads(results.top_clients),
                           top_asns=json.loads(results.top_asns),
                           total_servers=len(ping_results),
                           ping_results=ping_results
)

def utc_to_local(timestamp):
    local_dt = datetime.fromtimestamp(timestamp, pytz.timezone('US/Pacific'))
    return(local_dt)

                                                        
@app.teardown_appcontext
def close_session(exception):
    """Remove the db session or save file"""
    storage.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")

