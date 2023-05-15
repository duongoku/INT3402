# 📦 INT3402

Mini project for compiler course

## Table of Contents

- [📦 INT3402](#-int3402)
  - [Table of Contents](#table-of-contents)
  - [📄 Lexical Analyzer](#-lexical-analyzer)
    - [📜 Introduction](#-introduction)
    - [🔧 Prerequisites](#-prerequisites)
    - [🗄️ Data File](#️-data-file)
    - [⚙️ Run](#️-run)
  - [📄 Parser](#-parser)
    - [Introduction](#introduction)
    - [🔧 Prerequisites](#-prerequisites-1)
    - [🗄️ Data File](#️-data-file-1)
    - [⚙️ Run](#️-run-1)

## 📄 Lexical Analyzer

### 📜 Introduction

This is a lexical analyzer for a subset of C language (VC) implemented using Python 3. The lexical analyzer is able to recognize tokens, comments and throw errors for invalid tokens. The language definition is defined in [VC Language Definition](https://duongoku.github.io/archive/2023/VC%20Language%20Definition.pdf).

### 🔧 Prerequisites

-   [Python 3.10](https://www.python.org/downloads/) (you can also try other versions, it might work).
-   A data file containing information about the Deterministic finite automata (DFA) used in the lexical analyzer, the format of the file is defined in [🗄️ Data File](#️-data-file).
-   A source code file written in VC language.

### 🗄️ Data File

-   The data file is in json format but the extension is _.dat_, there's a [sample data](dfa.dat) file in the root directory of this project. The data file contains the following fields:
    -   `keywords`: a list of keywords in target the language.
    -   `special_literals`: a list of special literals used in target the language.
    -   `separators`: a list of characters used to separate tokens in target the language.
    -   `terminal_types`: a list of types of tokens in target the language.
    -   `nodes`: a list of nodes in the DFA, this includes:
        -   the key of each node is the name of the node.
        -   `children` is a list of children of the node, each child is a map from a list of characters to the name of the child node
        -   if the node is the starting node, it will include a field `start` with value _true_.
        -   if the node is terminal, it will include a field `terminal` with value _true_ and a field `terminal_type` with the type of the token from `terminal_types`, else it will have a field `terminal` with value _false_.
-   There is also a [sample source file](sample.vc) for you to use in the root directory of this project.

### ⚙️ Run

To run the lexical analyzer, run the following command in the terminal (default value for `data_file` is _dfa.dat_):

```
python lexer.py <source_code_file> [data_file]
```

To see more information about the command, run the following command in the terminal:

```
python lexer.py -h
```

You can also run this online on [Repl.it](https://replit.com/@duongoku/Lexer#README.md).

## 📄 Parser

### Introduction

This is a parser for a subset of C language (VC) implemented using Python 3. The parser is able to recognize the syntax of the source code and throw errors for invalid syntax. The language definition is defined in [VC Language Definition](https://duongoku.github.io/archive/2023/VC%20Language%20Definition.pdf).

### 🔧 Prerequisites

The same as [📄 Lexical Analyzer](#-lexical-analyzer).

### 🗄️ Data File

- The data file is in a human-readable format with `.dat` extension.
- The first line in the data file is a list of terminal types in the language (if that terminal type is used directly in the grammar). The terminal types mentioned here may be LITERAL or IDENTIFIER in the language. The terminal types are separated by a vertical bar `|`. Caution: terminal types are not terminal symbols, they represent a group of terminal symbols.
- The grammar is written from the second line. Each line represents a production rule. The production rule is written in the following format: `non-terminal -> production`. The non-terminal is the left-hand side of the production rule, and the production is the right-hand side of the production rule. The production is a list of terminal types and non-terminals separated by a space. If there are multiple productions for a non-terminal, they are separated by a vertical bar `|`. Each symbol in a production is separated by a space. - The first non-terminal in the grammar is the start symbol.

### ⚙️ Run

To run the parser, run the following command in the terminal (default value for `parser_data` is _grammar.dat_, default value for `lexer_data` is _dfa.dat_):

```
python vcparser.py <source_code_file> [lexer_data] [parser_data]
```

To see more information about the command, run the following command in the terminal:

```
python vcparser.py -h
```

You can also run this online on [Repl.it](https://replit.com/@duongoku/Parser#README.md).