import websocket
import json
import urlparse
import hmac
import hashlib
import time
import requests

commission = ''
leverage = '' 
avgCostPrice = '' # Entered Price
marginCallPrice = '' #MarginCall Price
lastPrice = '' #Market Average Price 
unrealisedRoePcnt = '' #Revenue percentage 

amount = ''
currentQty = '' # -1 is short, 1 is long

def indexing_tuple(string, key, find_values):

	data = []
	true = 1
	false = 0
	null = ''
	
	result = eval(string)
	result = result[key]
	result = result[0]

	for i in range(0, len(find_values)):
		data.append(result[find_values[i]])

	return data

def  marginState(ws):

        request = {"op" : "subscribe", "args" : ["position"]}
        ws.send(json.dumps(request))

	ws.recv() #success message
	recvData = ws.recv()
	#print recvData
	
	marginData = ['avgCostPrice', 'lastPrice', 'marginCallPrice', 'leverage', 'commission','unrealisedRoePcnt', 'currentQty']	
	resultData = []

	resultData = indexing_tuple(recvData,'data', marginData)
	
	avgCostPrice = resultData[0]
	lastPrice = resultData[1]
	marginCallPrice = resultData[2]
	leverage = resultData[3]
	commission = resultData[4] * 100
	unrealisedRoePcnt = resultData[5] * 100
	currentQty = resultData[6]


	print "\n**********Current Margin State**********" 
	print "Entered Price: "+ str(avgCostPrice)  #table part
	print "Market Average Price: "+ str(lastPrice)
	print "Leverage : "+str(leverage)
	print "Margin Call Price: "+ str(marginCallPrice)
	print "Commission :"+str(commission)
	print "Revenue Percentage: "+str(unrealisedRoePcnt)+"%"

	if currentQty is -1:
		print "Now Position : Short"
	elif currentQty is 1:
		print "Now Position : Long"

	print "****************************************"
def auth(ws, apiSecret, apiKey, endpoint):

	VERB = 'GET'
	expires = int(time.time()) + 5

	signature = bitmex_signature(apiSecret, VERB, endpoint,expires)

	#ws = websocket.create_connection(BITMEX_URL + endpoint +"?api-expires=%s&api-signature=%s&api-key=%s" % (expires, signature, apiKey))
	#ws = websocket.create_connection(BITMEX_URL + endpoint)
	#print "-Create Connection Recv Message-"
	#result = ws.recv()
	#print result

	request = {"op": "authKeyExpires", "args": [API_KEY, expires, signature]}
	ws.send(json.dumps(request))
	#print "-Send authKeyExpires-"
	ws.recv()

	return signature

def bitmex_signature(apiSecret, verb, url, nonce):
	
	parsedURL = urlparse.urlparse(url)
	path = parsedURL.path

	if parsedURL.query:
		path = path+'?'+parsedURL.query

	message = (verb + path + str(nonce)).encode('utf-8')

	print "Signing: "+str(message)

	signature = hmac.new(apiSecret.encode('utf-8'), message, digestmod=hashlib.sha256).hexdigest()

	return signature	

def myAmountXBT(ws):

	walletData = ['amount']
        request = {"op" : "subscribe", "args" : ["wallet"]}
        ws.send(json.dumps(request))


	ws.recv()	
	resultData = indexing_tuple(ws.recv(),'data', walletData)	
	amount = resultData[0]

	print "\n**********Current Margin State**********"	
	print "My XBT: "+ str(amount)  #table part
	print "****************************************"


if __name__ == "__main__":

	ENDPOINT = "/realtime"	
	#ENDPOINT = "/api/v1/position"
	BITMEX_URL = "wss://www.bitmex.com"
	API_KEY = 'Ly4C-nrzgkS2QwKOLCA'
	API_SECRET ='awtpjaEfaMhnRKPNvIJFenXqmZDrtVMCYjxFe'

        ws = websocket.create_connection(BITMEX_URL + ENDPOINT)
        result = ws.recv()

	signature = auth(ws, API_SECRET, API_KEY, ENDPOINT)

	marginState(ws)
	myAmountXBT(ws)
	order('BUY', 1, 6500.0, 'Limit', API_KEY, API_SECRET)
