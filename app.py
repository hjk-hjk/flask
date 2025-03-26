from flask import Flask, render_template
from board import board_bp
from psd import psd_bp

app  = Flask(__name__)

# 블루프린트 등록하기
app.register_blueprint(board_bp, url_prefix='/board')
app.register_blueprint(psd_bp, url_prefix='/psd')


@app.route('/')
def  index():
    return  render_template("index.html")

if __name__ == '__main__':
    app.run(debug = True)