from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

app=Flask(__name__)

# @app.route("/")
# def hello():
# 	return "Welcome"

@app.route('/')
@app.route('/mta.html')
def index():
	return render_template('mta.html')

@app.route('/testpy',methods=['GET'])
def fc():
	a=request.args.get('a',0,type=float)
	b=request.args.get('b',0,type=float)
	c=request.args.get('c',0,type=float)
	return jsonify(result=a+b+c)

# @app.route('/testpy',methods=['POST'])
# def testpy():
# 	# x=int(request.form.get('line'))
# 	# x=request.get_json()
# 	return jsonify({'result':'ok'})


# @app.route('/testpy',methods=['POST'])
# def testpy():
# 	x=request.form['l']
# 	y=request.form['s']
# 	z=request.form['e']
# 	c=x+y+z
# 	return c

# # 	# temp={'a':'1'}
# # 	# return render_template('mta.html',temp=temp)

	# return render_template('mta.html',pyvar=c)
	

# def func(x,y,z):
#     c=x+y+z
#     return c

if __name__=="__main__":
    app.run()