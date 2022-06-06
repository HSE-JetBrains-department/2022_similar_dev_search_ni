import pytest

from repo_processing.code_parser.tree_sitter_parser import go_parse

py_names_entries = [
    {"code": bytes(""" class A():
ss = 5
a1 = a1 """, "utf8"), "expected_names": ["A", "ss", "a1"]},
    {"code": bytes(
        """ class A():
def foo():
    vall = 5
    if bar:
        baz()""", "utf8"), "expected_names": ["foo", "vall"]},
    {"code": bytes(""" class A():
class B():
class C(): """, "utf8"), "expected_names": ["foo", "vall"]}
]

py_imports_entries = [
    {"code": bytes(""" import sys1
from a import * """, "utf8"), "expected_imports": ["sys1", "a"]},
    {"code": bytes(""" from s import sys
from . import b """, "utf8"), "expected_imports": ["s", "sys", "b"]},
    {"code": bytes(""" import a2, b2
import b1.c as d
import a1.b.c """, "utf8"),
     "expected_imports": ["a2", "b2", "b1.c", "a1.b.c"]}
]


@pytest.mark.parametrize("code, expected_names", [(py_names_entries[0]["code"], py_names_entries[0]["expected_names"]),
                                                  (py_names_entries[1]["code"], py_names_entries[1]["expected_names"])])
def test_python_variables(code, expected_names):
    assert go_parse("python", code)["names"] == list(set(expected_names))


@pytest.mark.parametrize("code, expected_imports",
                         [(py_imports_entries[0]["code"], py_imports_entries[0]["expected_imports"]),
                          (py_imports_entries[1]["code"], py_imports_entries[1]["expected_imports"]),
                          (py_imports_entries[2]["code"], py_imports_entries[2]["expected_imports"])])
def test_python_imports(code, expected_imports):
    assert go_parse("python", code)["imports"] == list(set(expected_imports))


java_names_entries = [
    {"code": bytes("""
package test;
package test2.tt;
package com.javacodeexamples.collections.arraylist;
package com.javacodeexamples.collections.arraylist.testing;
""", "utf8"), "expected_names": ["test2.tt", "com.javacodeexamples.collections.arraylist",
                                 "com.javacodeexamples.collections.arraylist.testing"]},
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
""", "utf8"), "expected_names": ["ArrayListInsertElementExample", "valic", "main", "args", "fives", "tens"]}
]

java_imports_entries = [
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
""", "utf8"), "expected_imports": ["java3.util3.new", "java2.util2", "java1", "java.util.ArrayList"]}
]


@pytest.mark.parametrize("code, expected_names",
                         [(java_names_entries[0]["code"], java_names_entries[0]["expected_names"]),
                          (java_names_entries[1]["code"], java_names_entries[1]["expected_names"]),
                          (java_names_entries[2]["code"], java_names_entries[2]["expected_names"])])
def test_java_variables(code, expected_names):
    assert go_parse("java", code)["names"] == list(set(expected_names))


@pytest.mark.parametrize("code, expected_imports",
                         [(java_imports_entries[0]["code"], java_imports_entries[0]["expected_imports"]),
                          (java_names_entries[1]["code"], java_imports_entries[1]["expected_imports"]),
                          (java_imports_entries[2]["code"], java_imports_entries[2]["expected_imports"])])
def test_java_imports(code, expected_imports):
    assert go_parse("java", code)["imports"] == list(set(expected_imports))


js_names_entries = [
    {"code": bytes("""
a = 0;
var b = 0;
const c = 0;
let d = 0;
""", "utf8"), "expected_names": ['a', 'b', 'c', 'd']},
    {"code": bytes("""
class Foo {
}
""", "utf8"), "expected_names": ["Foo"]}
]

js_imports_entries = [
    {"code": bytes("""
import("a");
import("a").then((m) => {});
import.meta.url.af;
""", "utf8"), "expected_imports": ['a', 'm', "import.meta.url.af"]},
    {"code": bytes("""
import "module-name8";
import defaultMember from "module-name1";
import * as name from "module-name2"
""", "utf8"), "expected_imports": ["name", '"module-name1"', "module-name2", "defaultMember"]},
    {"code": bytes("""
import { member } from "module-name3";
import { member1 , member2 } from "module-name4";
import { member1 , member2 as alias2 } from "module-name5";
import defaultMember1, { member1, member2 as alias2 } from "module-name6";
import defaultMember2, * as name from "module-name7";
import { member1 , member2 as alias2, } from "module-name9";
""", "utf8"), "expected_imports": ["member", "name", "module-name7", "module-name5", "alias2", "defaultMember1",
                                   '"module-name6"',
                                   "member2 as alias2", "module-name4", "defaultMember2", '"module-name7"',
                                   "module-name9",
                                   "member2", "module-name6", "member1", "module-name3"]},
]


@pytest.mark.parametrize("code, expected_names",
                         [(js_names_entries[0]["code"], js_names_entries[0]["expected_names"]),
                          (js_names_entries[1]["code"], js_names_entries[1]["expected_names"])])
def test_js_variables(code, expected_names):
    assert go_parse("javascript", code)["names"] == list(set(expected_names))


@pytest.mark.parametrize("code, expected_imports",
                         [(js_imports_entries[0]["code"], js_imports_entries[0]["expected_imports"]),
                          (js_imports_entries[1]["code"], js_imports_entries[1]["expected_imports"]),
                          (js_imports_entries[2]["code"], js_imports_entries[2]["expected_imports"])])
def test_js_imports(code, expected_imports):
    assert go_parse("javascript", code)["imports"] == list(set(expected_imports))
