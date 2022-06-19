import pytest

from repo_processing.code_parser.tree_sitter_parser import go_parse

PY_NAMES_ENTRIES = [
    {"code": bytes(""" class A():
ss = 5
a1 = a1 """, "utf8"), "expected_names": ["A", "ss", "a1"]},
    {"code": bytes(""" class A():
def foo():
    vall = 5
    if bar:
        baz()""", "utf8"), "expected_names": ["A", "foo", "vall"]},
    {"code": bytes(""" class A():
class B():
class C(): """, "utf8"), "expected_names": ["A", "B", "C"]}
]

PY_IMPORTS_ENTRIES = [
    {"code": bytes(""" import sys1
from a import * """, "utf8"), "expected_imports": ["sys1", "a"]},
    {"code": bytes(""" from s import sys
from . import b """, "utf8"), "expected_imports": ["s", "sys", "b"]},
    {"code": bytes(""" import a2, b2
import b1.c as d
import a1.b.c """, "utf8"),
     "expected_imports": ["a2", "b2", "b1.c", "a1.b.c"]}
]


@pytest.mark.parametrize("code, expected_names",
                         [
                             (PY_NAMES_ENTRIES[0]["code"],
                              PY_NAMES_ENTRIES[0]["expected_names"]),
                             (PY_NAMES_ENTRIES[1]["code"],
                              PY_NAMES_ENTRIES[1]["expected_names"])])
def test_python_variables(code, expected_names):
    """
    Testing go_parse function parses names of fields, variables, functions
     correctly for Python language.
    """
    assert go_parse("python", code)["names"] == list(set(expected_names))


@pytest.mark.parametrize("code, expected_imports", [
    (PY_IMPORTS_ENTRIES[0]["code"], PY_IMPORTS_ENTRIES[0]["expected_imports"]),
    (PY_IMPORTS_ENTRIES[1]["code"], PY_IMPORTS_ENTRIES[1]["expected_imports"]),
    (
            PY_IMPORTS_ENTRIES[2]["code"],
            PY_IMPORTS_ENTRIES[2]["expected_imports"])])
def test_python_imports(code, expected_imports):
    """
    Testing go_parse function parses used imports, invoked methods and classes
    correctly for Python language.
    """
    assert sorted(list(go_parse("python", code)["imports"].keys())) == sorted(
        list(set(expected_imports)))


JAVA_NAMES_ENTRIES = [
    {"code": bytes("""
package test;
package test2.tt;
package com.javacodeexamples.collections.arraylist;
package com.javacodeexamples.collections.arraylist.testing;
""", "utf8"), "expected_names": ["test2.tt",
                                 "com.javacodeexamples.collections.arraylist",
                                 "com.javacodeexamples.collections.arraylist"
                                 ".testing"]},
    {"code": bytes("""
interface IFace {
}
public class ArrayListInsertElementExample {
}
""", "utf8"), "expected_names": ["IFace", "ArrayListInsertElementExample"]},
    {"code": bytes("""
public class ArrayListInsertElementExample {
 static int valic = 12;
    public static void main(String[] args, int fives, float tens) {
        ArrayList<String> aListNumbers = new ArrayList<String>();
    }
}
""", "utf8"),
     "expected_names": ["ArrayListInsertElementExample", "valic", "main",
                        "args", "fives", "tens"]}
]

JAVA_IMPORTS_ENTRIES = [
    {"code": bytes("""
aListNumbers.add("One");
aListNumbers.add("Two");
aListNumbers.add("Three");
aListNumbers.add(0, "Zero");
System.out.println("Element added at beginning of ArrayList");
System.out.println(aListNumbers);
""", "utf8"), "expected_imports": ["add", "println"]},
    {"code": bytes("""
Maka mak = new Maka(new Baka());
""", "utf8"), "expected_imports": ["mak"]},
    {"code": bytes("""
import java.util.ArrayList;
import java1;
import java2.util2.*;
import java3.util3.new.*;
""", "utf8"), "expected_imports": ["java3.util3.new", "java2.util2", "java1",
                                   "java.util.ArrayList"]}
]


@pytest.mark.parametrize("code, expected_names",
                         [(JAVA_NAMES_ENTRIES[0]["code"],
                           JAVA_NAMES_ENTRIES[0]["expected_names"]),
                          (JAVA_NAMES_ENTRIES[1]["code"],
                           JAVA_NAMES_ENTRIES[1]["expected_names"]),
                          (JAVA_NAMES_ENTRIES[2]["code"],
                           JAVA_NAMES_ENTRIES[2]["expected_names"])])
def test_java_variables(code, expected_names):
    """
    Testing go_parse function parses names of fields, variables, functions
    correctly for Java language.
    """
    assert sorted(go_parse("java", code)["names"]) == sorted(
        list(set(expected_names)))


@pytest.mark.parametrize("code, expected_imports",
                         [(JAVA_IMPORTS_ENTRIES[0]["code"],
                           JAVA_IMPORTS_ENTRIES[0]["expected_imports"]),
                          (JAVA_IMPORTS_ENTRIES[1]["code"],
                           JAVA_IMPORTS_ENTRIES[1]["expected_imports"]),
                          (JAVA_IMPORTS_ENTRIES[2]["code"],
                           JAVA_IMPORTS_ENTRIES[2]["expected_imports"])])
def test_java_imports(code, expected_imports):
    """
    Testing go_parse function parses used imports, invoked methods and classes
    correctly for Java language.
    """
    assert sorted(list(go_parse("java", code)["imports"].keys())) == sorted(
        list(set(expected_imports)))


JS_NAMES_ENTRIES = [
    {"code": bytes("""
a = 0;
var b = 0;
const c = 0;
let d = 0;
""", "utf8"), "expected_names": ["a", "b", "c", "d"]},
    {"code": bytes("""
class Foo {
}
""", "utf8"), "expected_names": ["Foo"]}
]

JS_IMPORTS_ENTRIES = [
    {"code": bytes("""
import("a");
import("a").then((m) => {});
import.meta.url.af;
""", "utf8"), "expected_imports": ["a", "m", "import.meta.url.af"]},
    {"code": bytes("""
import "module-name8";
import defaultMember from "module-name1";
import * as name from "module-name2"
""", "utf8"), "expected_imports": ["name", '"module-name1"', "module-name2",
                                   "defaultMember"]},
    {"code": bytes("""
import { member } from "module-name3";
import { member1 , member2 } from "module-name4";
import { member1 , member2 as alias2 } from "module-name5";
import defaultMember1, { member1, member2 as alias2 } from "module-name6";
import defaultMember2, * as name from "module-name7";
import { member1 , member2 as alias2, } from "module-name9";
""", "utf8"),
     "expected_imports": ['"module-name6"', 'name', 'module-name7', 'member',
                          'defaultMember2', 'defaultMember1',
                          'module-name6', '"module-name7"', 'member2',
                          'module-name5', 'alias2', 'module-name9',
                          'member2 as alias2', 'module-name3', 'module-name4',
                          'member1']},
]


@pytest.mark.parametrize("code, expected_names",
                         [(JS_NAMES_ENTRIES[0]["code"],
                           JS_NAMES_ENTRIES[0]["expected_names"]),
                          (JS_NAMES_ENTRIES[1]["code"],
                           JS_NAMES_ENTRIES[1]["expected_names"])])
def test_js_variables(code, expected_names):
    """
    Testing go_parse function parses names of fields, variables, functions
    correctly for JavaScript language.
    """
    assert sorted(list(go_parse("javascript", code)["names"].keys())) == sorted(
        list(set(expected_names)))


@pytest.mark.parametrize("code, expected_imports",
                         [(JS_IMPORTS_ENTRIES[0]["code"],
                           JS_IMPORTS_ENTRIES[0]["expected_imports"]),
                          (JS_IMPORTS_ENTRIES[1]["code"],
                           JS_IMPORTS_ENTRIES[1]["expected_imports"]),
                          (JS_IMPORTS_ENTRIES[2]["code"],
                           JS_IMPORTS_ENTRIES[2]["expected_imports"])])
def test_js_imports(code, expected_imports):
    """
    Testing go_parse function parses used imports, invoked methods and classes
    correctly for JavaScript language.
    """
    assert sorted(list(go_parse("javascript", code)["imports"])) == sorted(
        list(set(expected_imports)))
