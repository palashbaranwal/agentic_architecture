from pydantic import BaseModel
from typing import List

# Input/Output models for tools

class AddInput(BaseModel):
    a: int
    b: int

class AddOutput(BaseModel):
    result: int

class SqrtInput(BaseModel):
    a: int

class SqrtOutput(BaseModel):
    result: float

class StringsToIntsInput(BaseModel):
    string: str

class StringsToIntsOutput(BaseModel):
    ascii_values: List[int]

class ExpSumInput(BaseModel):
    int_list: List[int]

class ExpSumOutput(BaseModel):
    result: float

# Text/Reasoning Based Function Models

class ShowReasoningInput(BaseModel):
    steps: List[str]

class ShowReasoningOutput(BaseModel):
    text: str

class CalculateInput(BaseModel):
    expression: str

class CalculateOutput(BaseModel):
    text: str

class VerifyInput(BaseModel):
    expression: str
    expected: float

class VerifyOutput(BaseModel):
    text: str

class CheckConsistencyInput(BaseModel):
    steps: List[str]

class CheckConsistencyOutput(BaseModel):
    text: str

class FallbackReasoningInput(BaseModel):
    step_description: str

class FallbackReasoningOutput(BaseModel):
    text: str
