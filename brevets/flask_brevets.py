"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html) 

"""
import os
import requests
import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import logging

# Set up Flask app
app = flask.Flask(__name__)
app.debug = True if "DEBUG" not in os.environ else os.environ["DEBUG"]
port_num = True if "PORT" not in os.environ else os.environ["PORT"]
app.logger.setLevel(logging.DEBUG)


##################################################
################### API Callers ################## 
##################################################

API_ADDR = os.environ["API_ADDR"]
API_PORT = os.environ["API_PORT"]
API_URL = f"http://{API_ADDR}:{API_PORT}/api/"

def get_brevet():
    """
    Obtains the newest document in the "brevets" collection in database
    by calling the RESTful API.

    Returns brevet_dist (string), datetime (datetime),
    and controls (list of dictionaries) as a tuple.
    """
    # Get documents (rows) in our collection (table),
    # Sort by primary key in descending order and limit to 1 document (row)
    # This will translate into finding the newest inserted document.
    brevets = requests.get(f"{API_URL}/brevets").json()

    # lists should be a list of dictionaries.
    # we just need the last one:
    brevet = brevets[-1]
    return brevet["length"], brevet["start_time"], brevet["checkpoints"]

def get_all_brevets():
    brevets = requests.get(f"{API_URL}/brevets").json()

    return brevets

def get_particular_brevet(id):
    brevet = requests.get(f"{API_URL}/brevet/{id}").json()
    return brevet

def update_brevet(id, brevet_dist, datetime, controls):
    requests.put(f"{API_URL}/brevet/{id}", json={"length": brevet_dist,
                                                 "start_time": datetime,
                                                 "checkpoints": controls}).json()
    return 

def insert_brevet(brevet_dist, datetime, controls):
    """
    Inserts a new brevet into the database by calling the API.
    
    Inputs a start time (string), total distance (string), and 
    controls (list[dicts]) for a brevet
    """

    _id = requests.post(f"{API_URL}/brevets", json={"length": brevet_dist,
                                                     "start_time": datetime,
                                                     "checkpoints": controls}).json()
    return _id

def delete_brevet(id):
    requests.delete(f"{API_URL}/brevet/{id}")
    return


###################################################
# AJAX request handlers ###########################
# These return JSON, rather than rendering pages. #
###################################################


@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    # retrieve the values from the jQuery call
    # km is a complete dud of a name; both the controle and total are in km
    control_dist = request.args.get('control_dist', 999, type=float)
    total_dist = request.args.get('total_dist', 200, type=float)
    start_time = request.args.get('time', arrow.now().isoformat)

    app.logger.debug("km={}".format(control_dist))
    app.logger.debug("request.args: {}".format(request.args))
    open_time = acp_times.open_time(control_dist, total_dist, arrow.get(start_time)).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(control_dist, total_dist, arrow.get(start_time)).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)


##################################################
################## Flask routes ################## 
##################################################


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


@app.route("/insert", methods=["POST"])
def insert():
    """
    /insert : inserts a brevet into the database.
    only accepts POST requests.
    JSON interface: gets JSON, responds with JSON
    """
    try:
        # Read the entire request body as a JSON
        # This will fail if the request body is NOT a JSON.
        input_json = request.json
        # if successful, input_json is automatically parsed into a python dictionary!
        
        # Because input_json is a dictionary, we can do this:
        brevet_dist = input_json["brevet_dist"] # Should be a string
        datetime = input_json["datetime"] # Should be a string
        controls = input_json["controls"] # Should be a list of dictionaries
        
        todo_id = insert_brevet(brevet_dist, datetime, controls)

        return flask.jsonify(result={},
                        message="Inserted!", 
                        status=1, 
                        mongo_id=todo_id)
    except:
        # The reason for the try and except is to ensure Flask responds with a JSON.
        # If Flask catches any error, it means you didn't catch it yourself,
        # And Flask, by default, returns the error in an HTML.
        # We want /insert to respond with a JSON no matter what!
        return flask.jsonify(result={},
                        message="Oh no! Server error!", 
                        status=0, 
                        mongo_id='None')


@app.route("/fetch", methods=["GET"])
def fetch():
    """
    /fetch : fetches the newest brevet data from the database.
    Only Accepts GET requests.
    JSON interface: gets JSON, responds with JSON
    """
    try:
        brevet_dist, datetime, controls = get_brevet()
        return flask.jsonify(
                result={"brevet_dist": brevet_dist, "datetime": datetime, 
                        "controls": controls}, 
                status=1,
                message="Successfully fetched brevet data!")
    except:
        return flask.jsonify(
                result={}, 
                status=0,
                message="Something went wrong, couldn't fetch any brevet data!")
    
@app.route("/api/brevets", methods=["GET", "POST"])
def all_brevets():
    """
    /api/brevets: fetches all brevet data from the database
    only accepts get requests when associated with endpoint /api/brevets
    JSON Interface: gets JSON, repsponds with JSON
    """
    if request.method == "GET": 
        try:
            output = []
            for brevet in get_all_brevets():
                _id = brevet["_id"]["$oid"]
                checkpoints = brevet["checkpoints"]
                length = brevet["length"]
                start_time = brevet["start_time"]
                result={"id": _id, "brevet_dist": length, "start time": start_time, 
                        "controls": checkpoints}
                output.append(result)
            return flask.jsonify(output)
        except:
            return flask.jsonify(
                    result={}, 
                    status=0,
                    message="Something went wrong, couldn't fetch any brevet data!")
    if request.method == "POST":
        try:
            input_json = request.json
            # if successful, input_json is automatically parsed into a python dictionary
            
            brevet_dist = input_json["brevet_dist"] # Should be a string
            datetime = input_json["datetime"] # Should be a string
            controls = input_json["controls"] # Should be a list of dictionaries
            
            brevet_id = insert_brevet(brevet_dist, datetime, controls)

            return flask.jsonify(result={},
                            message="Inserted!", 
                            status=1, 
                            mongo_id=brevet_id)
        except:
            return flask.jsonify(result={},
                            message="Oh no! Server error!", 
                            status=0, 
                            mongo_id='None')

    
@app.route("/api/brevet/<id>", methods=["GET", "PUT", "DELETE"])
def particular_brevet(id):
    if request.method == "GET":
        try:
            brevet = get_particular_brevet(id)
            _id = brevet["_id"]["$oid"]
            checkpoints = brevet["checkpoints"]
            length = brevet["length"]
            start_time = brevet["start_time"]
            result={"id": _id, "brevet_dist": length, "start time": start_time, 
            "controls": checkpoints}
            return flask.jsonify(result)
        except:
            return flask.jsonify(
                    result={}, 
                    status=0,
                    message="Something went wrong, couldn't fetch any brevet data!")
    elif request.method == "PUT":
        try:
            input_json = request.json
            # if successful, input_json is automatically parsed into a python dictionary
            
            brevet_dist = input_json["brevet_dist"] # Should be a string
            datetime = input_json["datetime"] # Should be a string
            controls = input_json["controls"] # Should be a list of dictionaries
            update_brevet(id, brevet_dist, datetime, controls)
            return flask.jsonify(
                result={},
                status=1,
                message=f"Successfully updated brevet with id {id}")
        except:
            return flask.jsonify(
                    result={}, 
                    status=0,
                    message="Something went wrong, couldn't update any brevet data!")
            
    elif request.method == "DELETE":
        try:
            delete_brevet(id)
            return flask.jsonify(
                result={},
                status=1,
                message=f"Successfully deleted brevet with id {id}")
        except:
            return flask.jsonify(
                    result={}, 
                    status=0,
                    message="Something went wrong, couldn't update any brevet data!")





##################################################
################# Start Flask App ################ 
##################################################


if __name__ == "__main__":
    app.run(port=port_num, host="0.0.0.0")
