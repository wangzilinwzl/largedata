from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import routePlan
import routePlan2
import os


def fun():
    os.system("nohup python dynamodata.py &")
    print "start collecting data"


fun()
app=Flask(__name__)

@app.route('/')
@app.route('/mta.html')
def index():
	return render_template('mta.html')

@app.route('/testpy')
def fc():
	x=request.args.get('a',0,type=int)
	y=request.args.get('b',0,type=int)
	z=request.args.get('c',0,type=int)
	res = "hello"
	if x < 4:
		res = routePlan.routePlan(y, z)
		print y
		print z
	else:
		res = routePlan2.routePlan(y, z)
	return jsonify(result=res)


if __name__=="__main__":
    app.run()