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


def test_error():
    input_mock = Mock(side_effect=["Dragon", "q"])
    get_mock = Mock(side_effect=({"error": "not found"}, {}))
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
    assert get_mock.call_count == 2
    get_mock.assert_has_calls(
        [
            call("https://www.dnd5eapi.co/api/monsters/dragon"),
            call("https://www.dnd5eapi.co/api/monsters/?name=dragon"),
        ]
    )
    assert print_mock.call_count == 1
    print_mock.assert_has_calls([call("Sorry! No monsters found!")])


def test_pick_option():
    input_mock = Mock(side_effect=["Dragon", "1", "q"])
    get_mock = Mock(
        side_effect=(
            {"error": "not found"},
            {
                "count": 3,
                "results": [
                    {
                        "index": "adult-black-dragon",
                        "name": "Adult Black Dragon",
                        "url": "/api/monsters/adult-black-dragon",
                    },
                    {
                        "index": "adult-blue-dragon",
                        "name": "Adult Blue Dragon",
                        "url": "/api/monsters/adult-blue-dragon",
                    },
                    {
                        "index": "adult-brass-dragon",
                        "name": "Adult Brass Dragon",
                        "url": "/api/monsters/adult-brass-dragon",
                    },
                ],
            },
            {
                "index": "adult-blue-dragon",
                "name": "Adult Blue Dragon",
                "size": "Huge",
                "type": "dragon",
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
            call("Which one of these? "),
            call("Type the name of the monster (or 'q' to quit): "),
        ]
    )
    assert get_mock.call_count == 3
    get_mock.assert_has_calls(
        [
            call("https://www.dnd5eapi.co/api/monsters/dragon"),
            call("https://www.dnd5eapi.co/api/monsters/?name=dragon"),
            call("https://www.dnd5eapi.co/api/monsters/adult-blue-dragon"),
        ]
    )
    assert print_mock.call_count == 8
    print_mock.assert_has_calls(
        [
            call("0. Adult Black Dragon\n1. Adult Blue Dragon\n2. Adult Brass Dragon"),
            call("Monsteronomicon presents!\n"),
            call("index: adult-blue-dragon"),
            call("name: Adult Blue Dragon"),
            call("size: Huge"),
            call("type: dragon"),
            call("alignment: lawful evil"),
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
