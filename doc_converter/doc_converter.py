""" base file for conversion of file formats api """
from flask import Flask

doc_converter = Flask(__name__)

@doc_converter.route("/")
def hello():
    """ test function """
    return "hello world!"

if __name__ == '__main__':
    doc_converter.run()

