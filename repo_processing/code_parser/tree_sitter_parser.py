from typing import Dict, List

from repo_processing.extractor.extract import clone_or_instantiate
from repo_processing import parser_dir
from repo_processing.lang_parser.enry_parser import get_content

from tree_sitter import Language, Parser, Tree
from tree_sitter import Node

# query of imports, used methods, classes
java_imports_used_methods_query_string = """
(import_declaration (scoped_identifier (identifier)) @name)
(import_declaration (identifier) @name)
(import_declaration ((scoped_identifier (identifier)) (asterisk)) @name)
(package_declaration  (identifier) @name)  
(method_invocation name: (identifier) @function.call) 
(local_variable_declaration declarator: (variable_declarator name: (identifier) @name)) 
"""

# query of names of created packages, classes, interfaces, methods, arguments, fields
java_names_query = """
(package_declaration (scoped_identifier (identifier)) @name)
(class_declaration name: (identifier) @name)
(interface_declaration name: (identifier) @name)
(method_declaration name: (identifier) @name)  
(method_declaration (formal_parameters(formal_parameter (identifier) @name))) 
(field_declaration declarator: (variable_declarator name: (identifier) @name))
"""

# query of imports, called functions
python_imports_used_methods_query_string = """
(import_from_statement (dotted_name (identifier)) @dotted_name)
(import_statement (dotted_name (identifier)) @dotted_name)
(aliased_import (dotted_name (identifier)) @dotted_name)
(call function: (identifier) @function.call)
"""

# query of names of classes, functions, fields
python_names_query_string = """
(class_definition name: (identifier) @name)
(function_definition name: (identifier) @function.def)
(expression_statement (assignment left: (identifier) @name)) 
"""

# query of imports, called functions
js_imports_used_methods_query_string = """
(expression_statement (member_expression) @name)
(expression_statement (call_expression (member_expression (call_expression (import) (arguments (string (string_fragment) @name))) 
    (property_identifier)) (arguments (arrow_function (formal_parameters (identifier) @name) (statement_block)))))
(import_statement (import_clause (identifier) @name) (string (string_fragment)) @name)
(import_statement (import_clause (namespace_import (identifier) @name)) (string (string_fragment) @name))
(import_statement (import_clause (named_imports (import_specifier (identifier)) @name)) (string (string_fragment) @name))
(import_statement (import_clause (named_imports (import_specifier (identifier)) (import_specifier (identifier) (identifier) @name))) 
    (string (string_fragment)))
"""

# query of names of classes, functions, fields
js_names_query_string = """
(assignment_expression (identifier) @name) (variable_declaration (variable_declarator (
identifier) @name)) (lexical_declaration (variable_declarator (identifier) @name)) (expression_statement (
call_expression (member_expression (call_expression (import) (arguments (string (string_fragment) @name))) (
property_identifier)) (arguments (arrow_function (formal_parameters (identifier) @name) (statement_block))))) (
expression_statement (member_expression) @name) (class_declaration name: (identifier) @name) (function_declaration 
    name: (identifier) @name) """


def setup_tree_sitter_parser() -> None:
    """
    Function sets up the parser for Python, JavaScript and Java languages cloning the repositories, that contain
    grammars.

    :return: Returns parser.
    """
    tree_sitter_python = clone_or_instantiate("https://github.com/tree-sitter/tree-sitter-python")
    tree_sitter_javascript = clone_or_instantiate("https://github.com/tree-sitter/tree-sitter-javascript")
    tree_sitter_java = clone_or_instantiate("https://github.com/tree-sitter/tree-sitter-java")

    Language.build_library(
        f"{parser_dir}/build/my-languages.so",
        [
            "tree-sitter-python",
            "tree-sitter-javascript",
            "tree-sitter-java"
        ]
    )


def process_query(query_str, LANGUAGE: Language, code: bytes, root_node: Node) -> List[str]:
    """
    Processes query using query_str for LANGUAGE.
    :param query_str: query string to extract info.
    :param LANGUAGE: Language instance.
    :param code: Part of code represented in bytes(str) utf8 encoding.
    :param root_node: Root of the parsed tree.

    :return: Returns list of queried results.
    """
    query = LANGUAGE.query(query_str)
    return list(set([code[x[0].start_byte: x[0].end_byte].decode() for x in query.captures(root_node)]))


def process_tree_sitter(LANGUAGE: str, code: bytes, tree) -> Dict:
    """
    Process lines of code returning dict
    :param LANGUAGE: Language instance.
    :param code: Part of code represented in bytes(str) utf8 encoding.
    :param tree: Parsed tree.

    :return: Returns dict with list of imports and names.
    """

    if LANGUAGE == "unknown":
        return {"imports": [], "names": []}

    parse_lang = Language(f"{parser_dir}/build/my-languages.so", LANGUAGE.lower())

    choice = {
        "java": [java_imports_used_methods_query_string, java_names_query],
        "python": [python_imports_used_methods_query_string, python_names_query_string],
        "javascript": [js_imports_used_methods_query_string, js_names_query_string]
    }

    imports_and_names = {
        "imports": process_query(choice[parse_lang.name][0], parse_lang, code, tree.root_node),
        "names": process_query(choice[parse_lang.name][1], parse_lang, code, tree.root_node)
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


def go_parse(language: str, code: bytes):
    parser = Parser()
    parser.set_language(Language(f"{parser_dir}/build/my-languages.so", language.lower()))

    tree = parse_code(code, parser)

    return process_tree_sitter(language, code, tree)


def parse_file(languages: List[str], path: str) -> Dict:
    """
    Function processes pipeline for parsing file.
    :param languages: List of languages of file.
    :param path: Path to file.

    :return: Returns dictionary with used imports and named fields, variables and methods.
    """
    code_str = get_content(path)
    code = bytes(code_str, "utf8")

    language = list({"java", "javascript", "python"} & set([x.lower() for x in languages]))
    language = language[0] if len(language) > 0 else "unknown"

    if language != "unknown":
        return go_parse(language, code)

    return {"imports": [], "names": []}


parsed_nodes = list()


def dfs_traverse_tree(root: Node) -> None:
    """
    Recursive DFS method for traversing parse tree
    given by tree-sitter library and filling parsed_nodes list by with each node.

    :param root: root node of parsed tree.
    """

    parsed_nodes.append(root)
    for child in root.children:
        dfs_traverse_tree(child)
