from unittest.mock import Mock, call
from monsteronomicon import App, get_adapter
import responses


def test_quit():
    input_mock = Mock(return_value="q")
    app = App(None, input_mock, None)

    app.loop()

    assert input_mock.call_count == 1
    input_mock.assert_has_calls(
        [call("Type the name of the monster (or 'q' to quit): ")]
    )


def test_one_check():
    input_mock = Mock(side_effect=["Adult black Dragon", "q"])
    get_mock = Mock(
        return_value={
            "index": "adult-black-dragon",
            "name": "Adult Black Dragon",
            "size": "Huge",
            "type": "dragon",
            "attacks": ["claw", "talon"],
            "alignment": "chaotic evil",
        }
    )
    print_mock = Mock()
    app = App(get_mock, input_mock, print_mock)

    app.loop()

    assert input_mock.call_count == 2
    input_mock.assert_has_calls(
        [
            call("Type the name of the monster (or 'q' to quit): "),
            call("Type the name of the monster (or 'q' to quit): "),
        ]
    )
    get_mock.assert_called_once_with(
        "https://www.dnd5eapi.co/api/monsters/adult-black-dragon"
    )
    assert print_mock.call_count == 7
    print_mock.assert_has_calls(
        [
            call("Monsteronomicon presents!\n"),
            call("index: adult-black-dragon"),
            call("name: Adult Black Dragon"),
            call("size: Huge"),
            call("type: dragon"),
            call("alignment: chaotic evil"),
            call(""),
        ]
    )


def test_multiple_checks():
    input_mock = Mock(side_effect=["Adult black Dragon", "Pit Fiend", "q"])
    get_mock = Mock(
        side_effect=(
            {
                "index": "adult-black-dragon",
                "name": "Adult Black Dragon",
                "size": "Huge",
                "type": "dragon",
                "attacks": ["claw", "talon"],
                "alignment": "chaotic evil",
            },
            {
                "index": "pit-fiend",
                "name": "Pit Fiend",
                "size": "Large",
                "environments": ["abyssal", "infernal"],
                "type": "fiend",
                "alignment": "lawful evil",
            },
        )
    )
    print_mock = Mock()
    app = App(get_mock, input_mock, print_mock)

    app.loop()

    assert input_mock.call_count == 3
    input_mock.assert_has_calls(
        [
            call("Type the name of the monster (or 'q' to quit): "),
            call("Type the name of the monster (or 'q' to quit): "),
            call("Type the name of the monster (or 'q' to quit): "),
        ]
    )
    assert get_mock.call_count == 2
    get_mock.assert_has_calls(
        [
            call("https://www.dnd5eapi.co/api/monsters/adult-black-dragon"),
            call("https://www.dnd5eapi.co/api/monsters/pit-fiend"),
        ]
    )
    assert print_mock.call_count == 14
    print_mock.assert_has_calls(
        [
            call("Monsteronomicon presents!\n"),
            call("index: adult-black-dragon"),
            call("name: Adult Black Dragon"),
            call("size: Huge"),
            call("type: dragon"),
            call("alignment: chaotic evil"),
            call(""),
            call("Monsteronomicon presents!\n"),
            call("index: pit-fiend"),
            call("name: Pit Fiend"),
            call("size: Large"),
            call("type: fiend"),
            call("alignment: lawful evil"),
            call(""),
        ]
    )


@responses.activate
def test_get_adapter():
    url = "https://some.api/and/some/path"
    responses.get(url, json={"foo": "bar"})

    response = get_adapter(url)

    assert response == {"foo": "bar"}
    assert responses.assert_call_count(url, 1)
