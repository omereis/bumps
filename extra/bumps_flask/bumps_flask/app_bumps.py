from flask import Flask, render_template, request
# Source:
# https://stackoverflow.com/questions/40963401/flask-dynamic-data-update-without-reload-page
app = Flask(__name__)

#------------------------------------------------------------------------------
@app.route('/onsendfitjob')
def on_send_fit_job():
    res = {}
    try:
        res = request.args['message']
#        print(f'res:\n---------------\n{res}\n-------------------\n')
#        print(f'type(res): {type(res)}')
        cm = json.loads(res)
#        print(f'cm = {cm}')
#        print(f'type(cm): {type(cm)}')
#        for key in cm.keys():
#            print(f'\t{key}:\t{cm[key]}')
    except Exception as e:
        print (f'run time error in on_send_fit_job: {e}')
    return json.dumps(res)
#------------------------------------------------------------------------------
@app.route('/')
def index():
        return render_template('bumps_mp_gui.html')

if __name__ == '__main__':
        app.run(debug=False, host='localhost', port=4000)