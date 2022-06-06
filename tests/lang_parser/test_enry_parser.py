from typing import List

import pytest

from repo_processing.lang_parser.enry_parser import get_languages_method
from tests.lang_parser import test_dir


@pytest.mark.parametrize("filename, expected_list", [("filepy.py", ["Python"]),
                                                     ("filej.java", ["Java"]),
                                                     ("filejs.js", ["JavaScript"])])
def test_enry_code(filename: str, expected_list: List[str]):
    assert list(set(get_languages_method(f"{test_dir}/{filename}"))) == list(set(expected_list))

