The `pydantic.Field` function is used to customize and add metadata to fields of models. To learn more check out the pydantic [documentation](https://docs.pydantic.dev/latest/concepts/fields/) as this is a near replica of that documentation that is relevant to prompting.

## Default values

The `default` parameter is used to define a default value for a field.

```py
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(default='John Doe')


user = User()
print(user)
#> name='John Doe'
```

You can also use `default_factory` to define a callable that will be called to generate a default value.

```py
from uuid import uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
```

!!! info

    The `default` and `default_factory` parameters are mutually exclusive.

!!! note

    If you use `typing.Optional`, it doesn't mean that the field has a default value of `None` you must use `default` or `default_factory` to define a default value. Then it will be considered `not required` when sent to the language model.

## Using `Annotated`

The `Field` function can also be used together with `Annotated`.

```py
from uuid import uuid4

from typing_extensions import Annotated

from pydantic import BaseModel, Field


class User(BaseModel):
    id: Annotated[str, Field(default_factory=lambda: uuid4().hex)]
```

## Exclude

The `exclude` parameter can be used to control which fields should be excluded from the
model when exporting the model. This is helpful when you want to exclude fields that are not relevant to the model
generation like `scratch_pad` or `chain_of_thought`

See the following example:

```py
from pydantic import BaseModel, Field
from datetime import date


class DateRange(BaseModel):
    chain_of_thought: str = Field(
        description="Reasoning behind the date range."
        exclude=True)
    start_date: date
    end_date: date


date_range = DateRange(
    chain_of_thought="""
        I want to find the date range for the last 30 days.
        Today is 2021-01-30 therefore the start date
        should be 2021-01-01 and the end date is 2021-01-30""",
    start_date=date(2021, 1, 1),
    end_date=date(2021, 1, 30),
)
print(date_range.model_dump_json())
#> start_date=datetime.date(2021, 1, 1) end_date=datetime.date(2021, 1, 30)
```

## Customizing JSON Schema

There are fields that exclusively to customise the generated JSON Schema:

- `title`: The title of the field.
- `description`: The description of the field.
- `examples`: The examples of the field.
- `json_schema_extra`: Extra JSON Schema properties to be added to the field.

These all work as great opportunities to add more information to the JSON Schema as part
of your prompt engineering.

Here's an example:

```py
from pydantic import BaseModel, EmailStr, Field, SecretStr


class User(BaseModel):
    age: int = Field(description='Age of the user')
    email: EmailStr = Field(examples=['marcelo@mail.com'])
    name: str = Field(title='Username')
    password: SecretStr = Field(
        json_schema_extra={
            'title': 'Password',
            'description': 'Password of the user',
            'examples': ['123456'],
        }
    )


print(User.model_json_schema())
"""
{
    'properties': {
        'age': {
            'description': 'Age of the user',
            'title': 'Age',
            'type': 'integer',
        },
        'email': {
            'examples': ['marcelo@mail.com'],
            'format': 'email',
            'title': 'Email',
            'type': 'string',
        },
        'name': {'title': 'Username', 'type': 'string'},
        'password': {
            'description': 'Password of the user',
            'examples': ['123456'],
            'format': 'password',
            'title': 'Password',
            'type': 'string',
            'writeOnly': True,
        },
    },
    'required': ['age', 'email', 'name', 'password'],
    'title': 'User',
    'type': 'object',
}
"""
```

## General notes on JSON schema generation

- The JSON schema for Optional fields indicates that the value null is allowed.
- The Decimal type is exposed in JSON schema (and serialized) as a string.
- The JSON schema does not preserve namedtuples as namedtuples.
- When they differ, you can specify whether you want the JSON schema to represent the inputs to validation or the outputs from serialization.
- Sub-models used are added to the `$defs` JSON attribute and referenced, as per the spec.
- Sub-models with modifications (via the Field class) like a custom title, description, or default value, are recursively included instead of referenced.
- The description for models is taken from either the docstring of the class or the argument description to the Field class.
