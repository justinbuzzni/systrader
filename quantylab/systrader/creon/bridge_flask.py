# from quantylab.systrader.creon import constants
# from quantylab.systrader.creon import Creon
import constants as constants
from _creon import Creon

from flask import Flask, request, jsonify
import sys
sys.path.append("\\VBOXSVR\workspace\systrader")


app = Flask(__name__)
c = Creon()


@app.route('/connection', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_connect():
    if request.method == 'GET':
        # check connection status
        return jsonify(c.connected())
    elif request.method == 'POST':
        # make connection
        data = request.get_json()
        _id = data['id']
        _pwd = data['pwd']
        _pwdcert = data['pwdcert']
        return jsonify(c.connect(_id, _pwd, _pwdcert))
    elif request.method == 'DELETE':
        # disconnect
        return jsonify(c.disconnect())


@app.route('/stockcodes', methods=['GET'])
def handle_stockcodes():
    c.wait()
    market = request.args.get('market')
    if market == 'kospi':
        return jsonify(c.get_stockcodes(constants.MARKET_CODE_KOSPI))
    elif market == 'kosdaq':
        return jsonify(c.get_stockcodes(constants.MARKET_CODE_KOSDAQ))
    else:
        return '"market" should be one of "kospi" and "kosdaq".', 400


@app.route('/stockstatus', methods=['GET'])
def handle_stockstatus():
    c.wait()
    stockcode = request.args.get('code')
    if not stockcode:
        return '', 400
    status = c.get_stockstatus(stockcode)
    return jsonify(status)


@app.route('/stockcandles', methods=['GET'])
def handle_stockcandles():
    c.wait()
    stockcode = request.args.get('code')
    n = request.args.get('n')
    unit = request.args.get('unit', 'D')
    if n:
        n = int(n)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    if not (n or date_from):
        return 'Need to provide "n" or "date_from" argument.', 400
    stockcandles = c.get_chart(
        stockcode, target='A', unit=unit, n=n, date_from=date_from, date_to=date_to)
    return jsonify(stockcandles)


@app.route('/marketcandles', methods=['GET'])
def handle_marketcandles():
    c.wait()
    marketcode = request.args.get('code')
    n = request.args.get('n')
    if n:
        n = int(n)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    if marketcode == 'kospi':
        marketcode = '001'
    elif marketcode == 'kosdaq':
        marketcode = '201'
    elif marketcode == 'kospi200':
        marketcode = '180'
    else:
        return [], 400
    if not (n or date_from):
        return '', 400
    marketcandles = c.get_chart(
        marketcode, target='U', unit='D', n=n, date_from=date_from, date_to=date_to)
    return jsonify(marketcandles)


@app.route('/stockfeatures', methods=['GET'])
def handle_stockfeatures():
    c.wait()
    stockcode = request.args.get('code')
    if not stockcode:
        return '', 400
    stockfeatures = c.get_stockfeatures(stockcode)
    return jsonify(stockfeatures)


@app.route('/short', methods=['GET'])
def handle_short():
    c.wait()
    stockcode = request.args.get('code')
    n = request.args.get('n')
    if n:
        n = int(n)
    if not stockcode:
        return '', 400
    shorts = c.get_shortstockselling(stockcode, n=n)
    return jsonify(shorts)


@app.route('/investorbuysell', methods=['GET'])
def handle_investorbuysell():
    c.wait()
    stockcode = request.args.get('code')
    n = request.args.get('n')
    if n:
        n = int(n)
    if not stockcode:
        return '', 400
    investorbuysell = c.get_investorbuysell(stockcode, n=n)
    return jsonify(investorbuysell)


@app.route('/get_balance', methods=['GET'])
def handle_get_balance():
    c.wait()
    return jsonify(c.get_balance())


@app.route('/get_remain_balance', methods=['GET'])
def handle_get_remain_balance():
    c.wait()
    return jsonify(c.get_account_balance())


@app.route('/buy', methods=['GET'])
def handle_buy():
    c.wait()
    stockcode = request.args.get('code')
    amount = request.args.get('amount')

    return jsonify(c.buy(stockcode, amount))


@app.route('/sell', methods=['GET'])
def handle_sell():
    c.wait()
    stockcode = request.args.get('code')
    amount = request.args.get('amount')
    if amount:
        amount = int(amount)

    return jsonify(c.sell(stockcode, amount))


@app.route('/holdingstocks', methods=['GET'])
def handle_holdingstocks():
    c.wait()
    return jsonify(c.get_holdings())


@app.route('/get_trade_history', methods=['GET'])
def handle_get_trade_history():
    c.wait()
    return jsonify(c.get_trade_history())


@app.route('/get_marketcap', methods=['GET'])
def handle_get_marketcap():
    c.wait()
    return jsonify(c.get_marketcap())


@app.route('/get_investorbuysell', methods=['GET'])
def handle_get_investorbuysell():
    c.wait()
    stockcode = request.args.get('code')
    n = request.args.get('n', None)
    if n:
        n = int(n)

    return jsonify(c.get_investorbuysell(stockcode, n=n))


@app.route('/get_shortstockselling', methods=['GET'])
def handle_get_shortstockselling():
    c.wait()
    stockcode = request.args.get('code')
    n = request.args.get('n', None)
    if n:
        n = int(n)

    return jsonify(c.get_shortstockselling(stockcode, n=n))


@app.route('/get_stockfeatures', methods=['GET'])
def handle_get_stockfeatures():
    c.wait()
    stockcode = request.args.get('code')
    return jsonify(c.get_stockfeatures(stockcode))


@app.route('/get_stockstatus', methods=['GET'])
def handle_get_stockstatus():
    c.wait()
    stockcode = request.args.get('code')
    return jsonify(c.get_stockstatus(stockcode))


@app.route('/get_stockcodes', methods=['GET'])
def handle_get_stockcodes():
    c.wait()
    code = request.args.get('code')
    return jsonify(c.get_stockcodes(code))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
