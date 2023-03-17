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
