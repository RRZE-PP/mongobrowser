from flask import jsonify, Flask, Response, request
from pymongo import MongoClient

import bson.json_util

app = Flask(__name__)
app.cursors = {}


class ResultFlagType():
    # returned, with zero results, when getMore is called but the cursor id
    #    is not valid at the server.
    ResultFlag_CursorNotFound = 1

    # { $err : ... } is being returned
    ResultFlag_ErrSet = 2

    # Have to update config from the server, usually $err is also set
    ResultFlag_ShardConfigStale = 4

    #  for backward compatibility: this let's us know the server supports
    #    the QueryOption_AwaitData option. if it doesn't, a repl slave client should sleep
    # a little between getMore's.
    ResultFlag_AwaitCapable = 8

#TODO: Use json scheme here
def setDefault(dict, key, val):
	if key not in dict or dict[key] is None:
		dict[key] = val

def checkType(dict, typeTuple):
	for key, expType in typeTuple:
		if not type(dict[key]) == expType:
			print("{} is not {} but {}".format(key, expType, type(dict[key])))
			return False

	return True

def validateAuthData(request):
	try:
		auth = request.json["connection"]["auth"]
		setDefault(auth, "authDatabase", "admin")
		setDefault(auth, "authMechanism", "scram-sha-1")

		return checkType(auth, [("user", unicode), ("password", unicode)])
	except KeyError:
		print("Missing key:" + str(e))
		return False

def validateConnectionData(request):
	try:
		conn = request.json["connection"]
		setDefault(conn, "hostname", "127.0.0.1")
		setDefault(conn, "port", 27017)
		setDefault(conn, "performAuth", False)

		if conn["performAuth"] and not validateAuthData(request):
			return False

		return True
	except KeyError:
		print("Missing key:" + str(e))
		return False

def validateCommandRequest(request):
	try:
		return validateConnectionData(request) and \
			checkType(request.json, [("database", unicode), ("command", unicode)])

	except KeyError:
		print("Missing key:" + str(e))
		return False


def validateInitCursorRequest(request):
	try:
		setDefault(request.json, "query", u"null")
		setDefault(request.json, "fieldsToReturn", u"null")
		setDefault(request.json, "nToSkip", 0)

		return validateConnectionData(request) and \
			checkType(request.json, [("query", unicode), ("ns", unicode), ("nToReturn", int),
			           ("nToSkip", int), ("fieldsToReturn", unicode)])

	except KeyError as e:
		print("Missing key:" + str(e))
		return False

def validateRequestMoreRequest(request):
	try:
		# This is duplicated from the routed function, because we cannot assign it to
		# cursorId here, but want to make sure it does not fail later
		if type(request.json["cursorId"]) == str and \
			request.json["cursorId"].startswith("NumberLong(\"") and \
			request.json["cursorId"].endswith("\")"):

				int(request.json["cursorId"][12:-3]) #keeping this here, but should never be invoced

		elif type(request.json["cursorId"]) == dict and \
			 '$numberLong' in request.json["cursorId"]:

				int(request.json["cursorId"]['$numberLong'])

		else:
			return False

		return validateConnectionData(request) and checkType(request.json, [("nToReturn", int)])

	except KeyError as e:
		print("Missing key:" + str(e))
		return False
	except (TypeError, ValueError) as e:
		print("Couldn't convert:" + str(e))
		return False

@app.route("/shell/runCommand", methods=["POST"])
def runCommand():
	print("=== RunCommand ===")
	if not validateCommandRequest(request):
		print("   Error")
		print("    " + str(request.json))
		return jsonify(error = "Invalid command sent"), 422

	json = request.json
	conn = json["connection"]
	auth = conn["auth"]

	print("{}:{}@{}:{}".format(auth["user"], auth["password"], conn["hostname"], conn["port"]))
	print("DB[{}].runCommand({})".format(json["database"], json["command"]))


	client = MongoClient(conn["hostname"], conn["port"], serverSelectionTimeoutMS=1000)

	if conn["performAuth"]:
		client[auth["authDatabase"]].authenticate(auth["user"], auth["password"], mechanism=auth["authMechanism"].upper())

	print(client)
	result = (client[json["database"]].command(bson.json_util.loads(json["command"])))

	return Response(bson.json_util.dumps(result), mimetype="application/json")


@app.route("/shell/initCursor", methods=["POST"])
def initCursor():
	print("=== InitCursor ===")
	print(request.json)
	if not validateInitCursorRequest(request):
		print("   Error")
		print("    " + str(request.json))
		return jsonify(error = "Invalid command sent"), 422

	json = request.json
	conn = json["connection"]
	auth = conn["auth"]

	print("{}:{}@{}:{}".format(auth["user"], auth["password"], conn["hostname"], conn["port"]))
	print("{}.find({}, {}).get({})".format(json["ns"], json["query"], json["fieldsToReturn"], json["nToReturn"]));


	client = MongoClient(conn["hostname"], conn["port"], serverSelectionTimeoutMS=1000)

	if conn["performAuth"]:
		client[auth["authDatabase"]].authenticate(auth["user"], auth["password"], mechanism=auth["authMechanism"].upper())

	database = json["ns"][0 : json["ns"].index(".")]
	collection = json["ns"][json["ns"].index(".") + 1 : ]

	isFindOne = False
	cursorUsedUp = False

	query = bson.json_util.loads(json["query"]);
	cursor = client[database].get_collection(collection).find(query,
	                                                          projection = bson.json_util.loads(json["fieldsToReturn"]),
	                                                          skip = json["nToSkip"])

	nToReturn = json["nToReturn"]
	if nToReturn == 0:
		nToReturn = 20
	if nToReturn == -1:
		isFindOne = True
		nToReturn = 1

	data = []
	for i, item in enumerate(cursor):
		if item is not None and i < nToReturn:
			data.append(bson.json_util.dumps(item))
		else:
			break
	else:
		#this branch is reached when for loop terminates normally (no break)
		cursorUsedUp = True

	cursorId = 0
	if not isFindOne and not cursorUsedUp:
		cursorId = cursor.cursor_id
		app.cursors[conn["hostname"] + str(conn["port"]) + str(cursorId)] = [cursor, client]
	else:
		client.close()

	return jsonify({"nReturned": len(data),
			"data": data,
			"resultFlags": 0,
			"cursorId": "NumberLong(\"" + str(cursorId) + "\")"})

@app.route("/shell/requestMore", methods=["POST"])
def requestMore():
	print("=== RequestMore ===")
	print(request.json)
	if not validateRequestMoreRequest(request):
		print("   Error")
		print("    " + str(request.json))
		return jsonify(error = "Invalid command sent"), 422

	json = request.json
	conn = json["connection"]

	cursorId = 0
	if type(request.json["cursorId"]) == str:
			cursorId = int(request.json["cursorId"][12:-3])
	elif type(request.json["cursorId"]) == dict:
			cursorId = int(request.json["cursorId"]['$numberLong'])

	cursorKey = conn["hostname"] + str(conn["port"]) + str(cursorId)

	print("Cursor(" + str(cursorId) + ").get(" + str(json["nToReturn"]) + ")")

	nToReturn = json["nToReturn"]
	if nToReturn == 0:
		nToReturn = 20

	if cursorKey in app.cursors:
		cursor, client = app.cursors[cursorKey]
		cursorUsedUp = False

		data = []
		for i, item in enumerate(cursor):
			if item is not None and i < nToReturn:
				data.append(bson.json_util.dumps(item))
			else:
				break
		else:
			#this branch is reached when for loop terminates normally (no break)
			cursorUsedUp = True

		if cursorUsedUp:
			cursors[cursorKey][1].close()
			del cursors[cursorKey]
			cursorId = 0

		return jsonify({"nReturned": len(data),
				"data": data,
				"resultFlags": 0,
				"cursorId": "NumberLong(\"" + str(cursorId) + "\")"})
	else:
		return jsonify({"resultFlags": ResultFlagType.ResultFlag_CursorNotFound})


if __name__ == "__main__":
    app.run(debug=True, port=8080)