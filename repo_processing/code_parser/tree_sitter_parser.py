from typing import Dict, List

from repo_processing.extractor import REPO_CLONES_DIR
from repo_processing.extractor.extract import clone_or_instantiate
from repo_processing.code_parser import PARSER_DIR
from repo_processing.lang_parser.enry_parser import get_content

from tree_sitter import Language, Parser, Tree
from tree_sitter import Node

# query of imports, used methods, classes
JAVA_IMPORTS_USED_METHODS_QUERY_STRING = """(import_declaration (
scoped_identifier (identifier)) @name) (import_declaration (identifier)
@name) (import_declaration ((scoped_identifier (identifier)) (asterisk))
@name) (package_declaration  (identifier) @name) (method_invocation name: (
identifier) @function.call) (local_variable_declaration declarator: (
variable_declarator name: (identifier) @name)) """

# query of names of created packages, classes, interfaces, methods,
# arguments, fields
JAVA_NAMES_QUERY_STRING = """
(package_declaration (scoped_identifier (identifier)) @name)
(class_declaration name: (identifier) @name)
(interface_declaration name: (identifier) @name)
(method_declaration name: (identifier) @name)
(method_declaration (formal_parameters(formal_parameter (identifier) @name)))
(field_declaration declarator: (variable_declarator name: (identifier) @name))
"""

# query of imports, called functions
PYTHON_IMPORTS_USED_METHODS_QUERY_STRING = """
(import_from_statement (dotted_name (identifier)) @dotted_name)
(import_statement (dotted_name (identifier)) @dotted_name)
(aliased_import (dotted_name (identifier)) @dotted_name)
(call function: (identifier) @function.call)
"""

# query of names of classes, functions, fields
PYTHON_NAMES_QUERY_STRING = """
(class_definition name: (identifier) @name)
(function_definition name: (identifier) @function.def)
(expression_statement (assignment left: (identifier) @name))
"""

# query of imports, called functions
JS_IMPORTS_USED_METHODS_QUERY_STRING = """(expression_statement (
member_expression) @name) (expression_statement (call_expression (
member_expression (call_expression (import) (arguments (string (
string_fragment) @name))) (property_identifier)) (arguments (arrow_function
(formal_parameters (identifier) @name) (statement_block))))) (
import_statement (import_clause (identifier) @name) (string (
string_fragment)) @name) (import_statement (import_clause (namespace_import
(identifier) @name)) (string (string_fragment) @name)) (import_statement (
import_clause (named_imports (import_specifier (identifier)) @name)) (string
(string_fragment) @name)) (import_statement (import_clause (named_imports (
import_specifier (identifier)) (import_specifier (identifier) (identifier)
@name))) (string (string_fragment))) """

# query of names of classes, functions, fields
JS_NAMES_QUERY_STRING = """(assignment_expression (identifier) @name) (
variable_declaration (variable_declarator ( identifier) @name)) (
lexical_declaration (variable_declarator (identifier) @name)) (
expression_statement ( call_expression (member_expression (call_expression (
import) (arguments (string (string_fragment) @name))) (
property_identifier)) (arguments (arrow_function (formal_parameters (
identifier) @name) (statement_block))))) ( expression_statement (
member_expression) @name) (class_declaration name: (identifier) @name) (
function_declaration name: (identifier) @name) """


def setup_tree_sitter_parser() -> None:
    """
    Function sets up the parser for Python, JavaScript and Java languages
    cloning the repositories, that contain grammars.

    :return: Returns parser.
    """
    clone_or_instantiate(
        "https://github.com/tree-sitter/tree-sitter-python")
    clone_or_instantiate(
        "https://github.com/tree-sitter/tree-sitter-javascript")
    clone_or_instantiate(
        "https://github.com/tree-sitter/tree-sitter-java")

    Language.build_library(
        f"{PARSER_DIR}/build/my-languages.so",
        [
            f"{REPO_CLONES_DIR}/tree-sitter-python",
            f"{REPO_CLONES_DIR}/tree-sitter-javascript",
            f"{REPO_CLONES_DIR}/tree-sitter-java"
        ]
    )


def process_query(query_str, language: Language, code: bytes,
                  root_node: Node) -> List[str]:
    """
    Processes query using query_str for LANGUAGE.
    :param query_str: query string to extract info.
    :param language: Language instance.
    :param code: Part of code represented in bytes(str) utf8 encoding.
    :param root_node: Root of the parsed tree.

    :return: Returns list of queried results.
    """
    query = language.query(query_str)
    return list(set([code[x[0].start_byte: x[0].end_byte].decode() for x in
                     query.captures(root_node)]))


def process_tree_sitter(language: str, code: bytes, tree) -> Dict:
    """
    Process lines of code returning dict
    :param language: Language instance.
    :param code: Part of code represented in bytes(str) utf8 encoding.
    :param tree: Parsed tree.

    :return: Returns dict with list of imports and names.
    """

    if language == "unknown":
        return {"imports": [], "names": []}

    parse_lang = Language(f"{PARSER_DIR}/build/my-languages.so",
                          language.lower())

    choice = {
        "java": [JAVA_IMPORTS_USED_METHODS_QUERY_STRING,
                 JAVA_NAMES_QUERY_STRING],
        "python": [PYTHON_IMPORTS_USED_METHODS_QUERY_STRING,
                   PYTHON_NAMES_QUERY_STRING],
        "javascript": [JS_IMPORTS_USED_METHODS_QUERY_STRING,
                       JS_NAMES_QUERY_STRING]
    }

    imports_and_names = {
        "imports": process_query(choice[parse_lang.name][0], parse_lang, code,
                                 tree.root_node),
        "names": process_query(choice[parse_lang.name][1], parse_lang, code,
                               tree.root_node)
    }

    return imports_and_names


def parse_code(code: bytes, parser: Parser) -> Tree:
    """
    Parses code_str using created tree-sitter parser.
    :param code: Lines of code in bytes.
    :param parser: Specified code parser.

    :return: Returns parsed tree.
    """

    return parser.parse(code)


def go_parse(language: str, code: bytes) -> Dict:
    """
    Creates Parser instance and processing code parsing.
    """
    parser = Parser()
    parser.set_language(
        Language(f"{PARSER_DIR}/build/my-languages.so", language.lower()))

    tree = parse_code(code, parser)

    return process_tree_sitter(language, code, tree)


def parse_file(languages: List[str], path: str) -> Dict:
    """
    Function processes pipeline for parsing file.
    :param languages: List of languages of file.
    :param path: Path to file.

    :return: Returns dictionary with used imports and named fields,
     variables and methods.
    """
    code_str = get_content(path)
    code = bytes(code_str, "utf8")

    language = list(
        {"java", "javascript", "python"} & set([x.lower() for x in languages]))
    language = language[0] if len(language) > 0 else "unknown"

    if language != "unknown":
        return go_parse(language, code)

    return {"imports": [], "names": []}


def apply_parsing(mapped_repos_list: List[Dict]) -> List[Dict]:
    """
    Sets to each element in mapped_repos_list list of used imports and names.

    :param mapped_repos_list: List of mapped commits info.

    :return:  List of dictionaries.
    """
    for x in mapped_repos_list:  # tree-sitter
        try:
            if ("Python" in x["lang"]) or ("JavaScript" in x["lang"]) or (
                    "Java" in x["lang"]):
                setup_tree_sitter_parser()
                parsed_d = parse_file(x["lang"], x["path"])
                x["tree_parse"] = parsed_d
        except FileNotFoundError:  # deleted files.
            pass

    return mapped_repos_list
