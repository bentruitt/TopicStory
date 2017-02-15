from website import app

def run():
    app.run(host='0.0.0.0', port=8105, debug=False, threaded=True)
