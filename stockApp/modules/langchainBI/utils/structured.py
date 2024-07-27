from __future__ import annotations
from langchain_core.output_parsers import BaseOutputParser
from langchain.output_parsers.format_instructions import (
    STRUCTURED_FORMAT_INSTRUCTIONS,
    STRUCTURED_FORMAT_SIMPLE_INSTRUCTIONS,
)
from langchain.output_parsers.json import parse_and_check_json_markdown
# from pydantic import BaseModel
from langchain_core.pydantic_v1 import BaseModel
from typing import Any, List


class ResponseSchema(BaseModel):
    """A schema for a response from a structured output parser."""

    name: str
    """The name of the schema."""
    description: str
    """The description of the schema."""
    type: str = "string"
    """The type of the response."""


class StructuredOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a structured output."""

    response_schemas: List[ResponseSchema]

    @classmethod
    def _get_sub_string(cls, schema: ResponseSchema) -> str:
        return '\t"{name}": {type} '.format(
            name=schema.name, type=schema.type
        )

    @classmethod
    def set_response_schemas(
            cls, response_schemas: List[ResponseSchema]
    ) -> StructuredOutputParser:
        return cls(response_schemas=response_schemas)

    def get_format_instructions(self) -> str:
        schema_str = "\n".join(
            [self._get_sub_string(schema) for schema in self.response_schemas]
        )
        return """
        ```json[{{
            {format}
        }}]```
        """.format(format=schema_str)

    def parse(self, text: str) -> Any:
        expected_keys = [rs.name for rs in self.response_schemas]
        return parse_and_check_json_markdown(text, expected_keys)

    @property
    def _type(self) -> str:
        return "structured"