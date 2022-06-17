from typing import List

import os
import pytest
import tempfile

from repo_processing.lang_parser.enry_parser import get_languages_method
from tests.lang_parser import test_dir

PY_CODE = b"""import re


for test_string in ['555-1212', 'ILL-EGAL']:
\tif re.match(r'^$', test_string):
\t\tprint(test_string, 'is a valid US local phone number')
\telse:
\t\tprint(test_string, 'rejected')"""

JAVA_CODE = b"""public class Factorial
{
\tpublic static void main(String[] args)
\t{	final int NUM_FACTS = 100;
\t\tfor(int i = 0; i < NUM_FACTS; i++)
\t\t\tSystem.out.println( i + "! is " + factorial(i));
\t}
\tpublic static int factorial(int n)
\t{	int result = 1;
\t\tfor(int i = 2; i <= n; i++)
\t\t\tresult *= i;
\t\treturn result;
\t}
}"""

JS_CODE = b"""const num1 = parseFloat(prompt("Enter first number: "));
const num2 = parseFloat(prompt("Enter second number: "));
const num3 = parseFloat(prompt("Enter third number: "));
let largest;

if(num1 >= num2 && num1 >= num3) {
    largest = num1;
}
else if (num2 >= num1 && num2 >= num3) {
    largest = num2;
}
else {
    largest = num3;
}

console.log("The largest number is " + largest);"""


def setup_file(code: bytes, filename: str) -> None:
    """
    Function to set up file with code to test enry parser functions.
    :param code: Code that will be written to file.
    :param filename: File name to write provided code.
    """
    with tempfile.NamedTemporaryFile(dir=test_dir, delete=True) as temp:
        temp.write(code)
        temp.seek(0)
        os.link(temp.name, f"{test_dir}/{filename}")


@pytest.fixture(scope='session', autouse=True)
def fixture_session():
    """
    Function that creates test_dir directory before all tests execution
    and removes test_dir after all.
    """
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    yield
    if os.path.exists(test_dir):
        os.removedirs(test_dir)


@pytest.mark.parametrize("filename, code, expected_list",
                         [("filepy.py", PY_CODE, ["Python"]),
                          ("filej.java", JAVA_CODE, ["Java"]),
                          ("filejs.js", JS_CODE, ["JavaScript"])])
def test_enry_code(filename: str, code: bytes, expected_list: List[str]):
    """
    Testing get_languages_method function of enry_parser file parses file
    correctly returning
    right list of languages.
    """
    setup_file(code, filename)
    result = get_languages_method(f"{test_dir}/{filename}")
    os.remove(f"{test_dir}/{filename}")
    assert list(set(result)) == list(set(expected_list))
