from typing import List, Dict

from src.dulwich.extract import clone_repo
from tree_sitter import Language, Parser, Tree
from tree_sitter import Node

# query of imports, used methods, classes
java_imports_usedmethods_query_string = """
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
python_imports_usedmethods_query_string = """
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

js_imports_used_methods_query_string = ""

js_names_query_string = ""


def setup_tree_sitter_parser() -> Parser:
    """
    Function sets up the parser for Python, JavaScript and Java languages cloning the repositories, that contain
    grammars.
    :return: Returns parser.
    """
    tree_sitter_python = clone_repo('https://github.com/tree-sitter/tree-sitter-python')
    tree_sitter_javascript = clone_repo('https://github.com/tree-sitter/tree-sitter-javascript')
    tree_sitter_java = clone_repo('https://github.com/tree-sitter/tree-sitter-java')

    Language.build_library(
        'build/my-languages.so',
        [
            'tree-sitter-python',
            'tree-sitter-javascript',
            'tree-sitter-java'
        ]
    )

    PY_LANGUAGE = Language('build/my-languages.so', 'python')
    JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
    JS_LANGUAGE = Language('build/my-languages.so', 'javascript')

    parser = Parser()
    parser.set_language(PY_LANGUAGE)
    parser.set_language(JAVA_LANGUAGE)
    parser.set_language(JS_LANGUAGE)

    return parser


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
    parse_lang = Language('build/my-languages.so', LANGUAGE.lower())

    choice = {
        'java': [java_imports_usedmethods_query_string, java_names_query],
        'python': [python_imports_usedmethods_query_string, python_names_query_string],
        'javascript': [js_imports_used_methods_query_string, js_names_query_string]
    }

    imports_and_names = {
        'imports': process_query(choice[parse_lang.name][0], parse_lang, code, tree.root_node),
        'names': process_query(choice[parse_lang.name][1], parse_lang, code, tree.root_node)
    }

    return imports_and_names


def parse_code(code_str: str) -> Tree:
    """
    Parses code_str using created tree-sitter parser. To get it use setup_tree_sitter_parser() function.
    :param code_str: Lines of code.
    :return: Returns parsed tree.
    """
    code = bytes(code_str, "uft8")
    parser = setup_tree_sitter_parser()
    return parser.parse(code)


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
