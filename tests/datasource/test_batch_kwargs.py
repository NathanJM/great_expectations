import pytest

from great_expectations.datasource.types import *  # noqa: F403


@pytest.mark.unit
def test_batch_kwargs_id():
    test_batch_kwargs = PathBatchKwargs({"path": "/data/test.csv"})  # noqa: F405
    # When there is only a single "important" key used in batch_kwargs, the ID can prominently include it  # noqa: E501
    assert test_batch_kwargs.to_id() == "path=/data/test.csv"

    test_batch_kwargs = PathBatchKwargs(  # noqa: F405
        {
            "path": "/data/test.csv",
            "reader_method": "read_csv",
            "reader_options": {
                "iterator": True,
                "chunksize": 2e7,
                "parse_dates": [0, 3],
                "names": ["start", "type", "quantity", "end"],
            },
        }
    )
    # When there are multiple relevant keys we use the hash of the batch_kwargs dictionary
    print(test_batch_kwargs.to_id())
    assert test_batch_kwargs.to_id() == "8607e071c6383509c8cd8f4c1ea65518"


@pytest.mark.unit
def test_batch_kwargs_attributes_and_keys():
    # When BatchKwargs are typed, the required keys should become accessible via dot notation and immutable  # noqa: E501
    test_batch_kwargs = PathBatchKwargs(  # noqa: F405
        {
            "path": "/data/test.csv",
            "reader_method": "read_csv",
            "reader_options": {
                "iterator": True,
                "chunksize": 2e7,
                "parse_dates": [0, 3],
                "names": ["start", "type", "quantity", "end"],
            },
        }
    )
    assert test_batch_kwargs.path == "/data/test.csv"
    assert test_batch_kwargs["path"] == test_batch_kwargs.path

    # We do not allow setting the special attributes this way
    with pytest.raises(AttributeError):
        test_batch_kwargs.path = "/a/new/path.csv"

    # Nor do we provide attribute-style access to unreserved names
    with pytest.raises(AttributeError):
        assert test_batch_kwargs.names == ["start", "type", "quantity", "end"]

    # But we can access and set even protected names using dictionary notation
    assert test_batch_kwargs["reader_options"]["names"] == [
        "start",
        "type",
        "quantity",
        "end",
    ]
    test_batch_kwargs["path"] = "/a/new/path.csv"
    assert test_batch_kwargs.path == "/a/new/path.csv"
