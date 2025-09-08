"""test additional functionality added to the sano fork of flask_openapi3"""

from http import HTTPStatus
from typing import Literal

import pydantic
from flask_openapi3 import OpenAPI
from flask import Flask, Blueprint, Response
import pytest

def test_response_name_conflicts() -> None:
    app = Flask(__name__)

    class APIResponse(pydantic.BaseModel): ...

    @app.post("/hello")
    def handler1() -> APIResponse:
        return APIResponse()


    # Define a different Response class with the same name
    class DataPayload(pydantic.BaseModel):
        title: str
    class APIResponse(pydantic.BaseModel):
        foo: DataPayload

    @app.post("/goodbye")
    def handler2() -> APIResponse:
        return APIResponse(foo=DataPayload(title="Goodbye"))

    api = OpenAPI(__name__)
    api.collect_metadata(app)
    api.generate_spec_json()

    components_schemas = api.spec_json["components"]["schemas"]
    assert "APIResponse" in components_schemas
    assert "APIResponse_1" in components_schemas

    assert components_schemas["APIResponse"] == {
        "title": "APIResponse",
        "type": "object",
        "properties": {},
    }
    assert components_schemas["APIResponse_1"] == {
        "title": "APIResponse",
        "type": "object",
        "properties": {"foo": {"$ref": "#/components/schemas/DataPayload"}},
        "required": ["foo"],
    }
    assert components_schemas["DataPayload"] == {
        "title": "DataPayload",
        "type": "object",
        "properties": {"title": {"title": "Title", "type": "string"}},
        "required": ["title"],
    }

# TODO (SAT-1773): fix remaining name conflicts
@pytest.mark.skip(reason="Name conflict handling not fully implemented yet (SAT-1773)")
def test_parse_body_name_conflicts() -> None:
    app = Flask(__name__)

    class Body(pydantic.BaseModel):
        name: str

    @app.post("/hello")
    def handler1(body: Body) -> Response:
        return Response(status=HTTPStatus.OK)
    
    class Body(pydantic.BaseModel):
        title: str

    @app.post("/goodbye")
    def handler2(body: Body) -> Response:
        return Response(status=HTTPStatus.OK)

    api = OpenAPI(__name__)
    api.collect_metadata(app)
    api.generate_spec_json()
    assert "Body" in api.spec_json["components"]["schemas"]
    assert "Body_1" in api.spec_json["components"]["schemas"]


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
