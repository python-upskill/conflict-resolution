import requests
from typing import Any, Callable


def get_adapter(url: str) -> Any:
    return requests.get(url).json()


class App:
    ROOT_URL = "https://www.dnd5eapi.co/api/monsters/"

    def __init__(
        self,
        get_function: Callable[[str], Any],
        input_function: Callable[[str], str],
        print_function: Callable[[str], None],
    ):
        self._get_function = get_function
        self._input_function = input_function
        self._print_function = print_function

    def loop(self) -> None:
        while (
            choice := self._input_function(
                "Type the name of the monster (or 'q' to quit): "
            )
        ) != "q":
            monster_data = self._get_function(
                self.ROOT_URL + choice.lower().replace(" ", "-")
            )
            self._print_function("Monsteronomicon presents!\n")
            for key, value in monster_data.items():
                if isinstance(value, str):
                    self._print_function(f"{key}: {value}")
            self._print_function("")


if __name__ == "__main__":
    App(get_adapter, input, print).loop()  # pragma: no cover
