"""test additional functionality added to the sano fork of flask_openapi3"""
from http import HTTPStatus
from flask_openapi3 import OpenAPI
from flask import Flask, Blueprint, Response

def test_flask_responses():
    sano_flask = Flask(__name__)
    blueprint = Blueprint("test", __name__)

    @blueprint.route("/hello")
    def handler() -> Response:
        return Response(status=HTTPStatus.OK)
    
    sano_flask.register_blueprint(blueprint)
    api = OpenAPI(__name__)
    api.collect_metadata(sano_flask)
    api.generate_spec_json()
    assert api.spec_json['paths']['/hello']['get']['responses'] == {'200': {'description': 'OK'}}
