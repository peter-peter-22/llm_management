from pydantic import BaseModel


# Example tools
class GetWeatherArgs(BaseModel):
    location: str
    unit: str = "celsius"


def get_weather(location: str, unit: str = "celsius") -> str:
    # Mock implementation
    return f"Weather in {location}: 72° {unit}"


register_tool("get_weather", get_weather, GetWeatherArgs)


class AddNumbersArgs(BaseModel):
    a: float
    b: float


def add_numbers(a: float, b: float) -> float:
    return a + b


register_tool("add_numbers", add_numbers, AddNumbersArgs)
