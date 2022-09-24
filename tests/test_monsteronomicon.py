from unittest.mock import Mock, call
from monsteronomicon import App, get_adapter
import responses
import pytest
import json
from collections import namedtuple


Example = namedtuple("Example", ("response", "expected"))


@pytest.fixture(name="example")
def example_fixture():
    with open("tests/adult-black-dragon.json") as example_file:
        json_response = json.loads(example_file.read())

    with open("tests/adult-black-dragon.txt") as example_file:
        expected_output = example_file.read().split("\n")

    return Example(response=json_response, expected=expected_output)


def test_quit():
    input_mock = Mock(return_value="q")
    app = App(None, input_mock, None)

    app.loop()

    assert input_mock.call_count == 1
    input_mock.assert_has_calls(
        [call("Type the name of the monster (or 'q' to quit): ")]
    )


def test_one_check(example):
    input_mock = Mock(side_effect=["Adult black Dragon", "q"])
    get_mock = Mock(return_value=example.response)
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
    assert print_mock.call_count == 40
    print_mock.assert_has_calls(
        [
            call("Monsteronomicon presents!\n"),
        ]
        + [call(line) for line in example.expected]
    )


def test_unknown_field():
    input_mock = Mock(side_effect=["Adult black Dragon", "q"])
    get_mock = Mock(return_value={"unknown": [1, 2, 3]})
    app = App(get_mock, input_mock, None)

    with pytest.raises(ValueError) as exc_info:
        app.loop()

    assert str(exc_info.value) == "Unknown key in monster description: unknown"
    assert input_mock.call_count == 1
    input_mock.assert_has_calls(
        [
            call("Type the name of the monster (or 'q' to quit): "),
        ]
    )
    get_mock.assert_called_once_with(
        "https://www.dnd5eapi.co/api/monsters/adult-black-dragon"
    )


def test_multiple_checks(example):
    input_mock = Mock(side_effect=["Adult black Dragon", "Pit Fiend", "q"])
    get_mock = Mock(
        side_effect=(
            example.response,
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
    assert print_mock.call_count == 48
    print_mock.assert_has_calls(
        [
            call("Monsteronomicon presents!\n"),
        ]
        + [call(line) for line in example.expected]
        + [
            call("Monsteronomicon presents!\n"),
            call("index: pit-fiend"),
            call("name: Pit Fiend"),
            call("size: Large"),
            call("environments: abyssal, infernal"),
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
