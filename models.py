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
    type: str = "text"
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

# Basic Math Operations Models

class SubtractInput(BaseModel):
    a: int
    b: int

class SubtractOutput(BaseModel):
    result: int

class MultiplyInput(BaseModel):
    a: int
    b: int

class MultiplyOutput(BaseModel):
    result: int

class DivideInput(BaseModel):
    a: int
    b: int

class DivideOutput(BaseModel):
    result: float

class PowerInput(BaseModel):
    a: int
    b: int

class PowerOutput(BaseModel):
    result: int

class CbrtInput(BaseModel):
    a: int

class CbrtOutput(BaseModel):
    result: float

class FactorialInput(BaseModel):
    a: int

class FactorialOutput(BaseModel):
    result: int

class LogInput(BaseModel):
    a: int

class LogOutput(BaseModel):
    result: float

class RemainderInput(BaseModel):
    a: int
    b: int

class RemainderOutput(BaseModel):
    result: int

class SinInput(BaseModel):
    a: int

class SinOutput(BaseModel):
    result: float

class CosInput(BaseModel):
    a: int

class CosOutput(BaseModel):
    result: float

class TanInput(BaseModel):
    a: int

class TanOutput(BaseModel):
    result: float

class MineInput(BaseModel):
    a: int
    b: int

class MineOutput(BaseModel):
    result: int
