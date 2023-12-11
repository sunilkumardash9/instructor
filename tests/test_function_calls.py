import pytest
from pydantic import BaseModel

from instructor import openai_schema, OpenAISchema


def test_openai_schema():
    @openai_schema
    class Dataframe(BaseModel):
        """
        Class representing a dataframe. This class is used to convert
        data into a frame that can be used by pandas.
        """

        data: str
        columns: str

        def to_pandas(self):
            pass

    assert hasattr(Dataframe, "openai_schema")
    assert hasattr(Dataframe, "from_response")
    assert hasattr(Dataframe, "to_pandas")
    assert Dataframe.openai_schema["name"] == "Dataframe"  # type: ignore


def test_openai_schema_raises_error():
    with pytest.raises(TypeError, match="must be a subclass of pydantic.BaseModel"):

        @openai_schema
        class Dummy:
            pass


def test_no_docstring():
    class Dummy(OpenAISchema):
        attr: str

    assert (
        Dummy.openai_schema["description"]
        == "Correctly extracted `Dummy` with all the required parameters with correct types"
    )
