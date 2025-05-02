"""test additional functionality added to the sano fork of flask_openapi3"""

from http import HTTPStatus
from typing import Literal

import pydantic
from flask_openapi3 import OpenAPI
from flask import Flask, Blueprint, Response


def test_flask_responses() -> None:
    sano_flask = Flask(__name__)
    blueprint = Blueprint("test", __name__)

    @blueprint.route("/hello")
    def handler() -> Response:
        return Response(status=HTTPStatus.OK)

    sano_flask.register_blueprint(blueprint)
    api = OpenAPI(__name__)
    api.collect_metadata(sano_flask)
    api.generate_spec_json()
    assert api.spec_json["paths"]["/hello"]["get"]["responses"] == {"200": {"description": "OK"}}


def test_const_for_literals() -> None:
    sano_flask = Flask(__name__)
    blueprint = Blueprint("test", __name__)

    class Body1(pydantic.BaseModel):
        name: Literal["i-am-literal"] = "i-am-literal"

    @blueprint.post("/hello")
    def handler(body: Body1) -> Response:
        return Response(status=HTTPStatus.OK)

    sano_flask.register_blueprint(blueprint)
    api = OpenAPI(__name__)
    api.collect_metadata(sano_flask)
    api.generate_spec_json()
    assert api.spec_json["components"]["schemas"]["Body1"] == {
        "title": "Body1",
        "type": "object",
        "properties": {"name": {"title": "Name", "type": "string", "default": "i-am-literal", "const": "i-am-literal"}},
    }
