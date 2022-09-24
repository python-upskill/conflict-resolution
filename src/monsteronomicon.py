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
            try:
                monster_data = self._get_monster_data(choice)
            except ValueError as exception:
                self._print_function(f"Sorry! {exception}")
                continue
            self._print_function("Monsteronomicon presents!\n")
            for key, value in monster_data.items():
                if isinstance(value, str):
                    self._print_function(f"{key}: {value}")
            self._print_function("")

    def _get_monster_data(self, choice: str) -> Any:
        slug = choice.lower().replace(" ", "-")
        monster_data = self._get_function(self.ROOT_URL + slug)
        if monster_data.get("error"):
            monster_list = self._get_function(f"{self.ROOT_URL}?name={slug}")
            if not monster_list.get("count"):
                raise ValueError("No monsters found!")

            options = {
                i: (r["name"], r["index"])
                for i, r in enumerate(monster_list["results"])
            }
            self._print_function("\n".join(f"{i}. {d[0]}" for i, d in options.items()))
            pick = self._input_function("Which one of these? ")
            return self._get_function(self.ROOT_URL + options[int(pick)][1])
        return monster_data


if __name__ == "__main__":
    App(get_adapter, input, print).loop()  # pragma: no cover
