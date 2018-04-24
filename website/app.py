from flask import Flask
from flask import render_template
from flask import request

app=Flask(__name__)

# @app.route("/")
# def hello():
# 	return "Welcome"

@app.route('/',methods=['GET','POST'])
def index():
	return render_template('mta.html')

@app.route('/testpy',methods=['POST'])
def testpy():
	data=request.form.get('data')
	return data


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