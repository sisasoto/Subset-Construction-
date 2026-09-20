<div align="center">

<img src="https://skillicons.dev/icons?i=python,vscode,html,js,windows&theme=dark" alt="Python, VS Code, HTML, JavaScript and Windows" />

# 🌌 Subset Construction

### Converting an NFA into an equivalent DFA · with an interactive visual report

![Python](https://img.shields.io/badge/Python-3.13.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![VS Code](https://img.shields.io/badge/VS%20Code-Editor-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Report-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![Windows 11](https://img.shields.io/badge/Windows%2011-25H2-0078D4?style=for-the-badge&logo=windows11&logoColor=white)

![Course](https://img.shields.io/badge/SI2002-Formal%20Languages-15107A?style=for-the-badge)
![Topic](https://img.shields.io/badge/NFA%20%E2%86%92%20DFA-Subset%20Construction-BDF2D0?style=for-the-badge&labelColor=15107A)

**🎓 EAFIT University · Assignment 2**

</div>

---

## 🧭 Table of contents

| # | Section |
|:-:|---|
| 1 | [🎓 Assignment cover page](#cover) |
| 2 | [🛠️ Versions and tools](#versions) |
| 3 | [📖 Assignment description](#description) |
| 4 | [🎥 video evidence](# ) |
| 5 | [🧠 Algorithm explanation](#algorithm) |
| 6 | [▶️ How to run it (VS Code and terminal)](#running) |
| 7 | [📥 How the input is read](#input) |
| 8 | [🖥️ What is printed to the console](#console) |
| 9 | [🌐 What the HTML shows](#html) |
| 10 | [✨ Additional features](#extras) |
| 11 | [🗂️ What each file does](#files) |

---

<a id="cover"></a>

## 🎓 1. Assignment cover page

| | |
|---|---|
| 📝 **Assignment title** | Subset Construction |
| 📚 **Course / class** | SI2002 · Formal Languages |
| 👨‍🏫 **Professor** | Sergio Ramírez Rico |
| 👩‍💻👨‍💻 **Students** | **Dilan Acevedo Rivera** · **Simón Santiago Soto Berrio** |
| 🐍 **Programming language** | Python 3.13.13 |
| 🧰 **Tools** | Visual Studio Code (code) · an HTML file (results) |
| 📖 **Reference** | Kozen, D. C. (1997). *Automata and Computability*, Lecture 6 |

---

<a id="versions"></a>

## 🛠️ 2. Versions and tools

| Category | Detail |
|---|---|
| 🪟 **Operating system** | Windows 11, version **25H2** |
| 🐍 **Programming language** | **Python 3.13.13** |
| 📦 **Python libraries** | Only the **standard library** (`sys`, `os`, `re`, `json`, `typing`, `pathlib`, `webbrowser`). No `pip install` needed. |
| 💻 **Editor** | Visual Studio Code |
| 🌐 **Web browser (for the HTML)**  |
---

<a id="description"></a>

## 📖 3. Assignment description

The assignment asks us to **implement Kozen's subset construction**: an algorithm that takes an **NFA** (nondeterministic finite automaton) and builds a **DFA** (deterministic finite automaton) that accepts exactly the same language.

Our program, written in **Python**, does the following for every input case:

1. 📥 **Reads** the input file and **validates** it.
2. 🧩 **Builds** the NFA in memory.
3. ⚙️ **Applies** the subset construction and obtains the DFA.
4. 🖥️ **Prints** the DFA table, its initial state and its final states to the console.
5. 🌐 **Generates** an interactive HTML report (`resultado_automata.html`) with the diagrams and tables of the NFA and the DFA.

---

<a id="algorithm"></a>

## 🎥 4. Video Evidence
https://github.com/user-attachments/assets/44dd4794-0b36-49b2-8ba1-71c1799c9ecf

## 🧠 5. Algorithm explanation

### 5.1 The idea

An NFA can be in **several states at once**. The subset construction takes advantage of this: **every state of the DFA is a set (subset) of NFA states**, and it represents "all the places where the NFA could be" after reading a string.

An NFA is defined as **M = (Q, Σ, Δ, S, F)**:

| Symbol | Meaning |
|:-:|---|
| **Q** | Set of states (here: `1, 2, …, n`) |
| **Σ** | Alphabet (lowercase letters `a–z`) |
| **Δ** | Transition function: (state, symbol) → **set** of states |
| **S** | Set of **initial** states (there may be several) |
| **F** | Set of **final** states |

### 5.2 The rules of the construction

For a set of states **A ⊆ Q** and a symbol **a ∈ Σ**:

> **δ(A, a) = ⋃ Δ(q, a)**, for every **q ∈ A**
> (the union of the destinations of each state in the set)

| DFA element | How it is obtained |
|---|---|
| 🟣 **Initial state** | The **whole set S** (that is why it matters that S can have several states) |
| 🔀 **Transition** | `δ(A, a)` according to the formula above |
| 🟢 **Final states** | Every subset **A** with **A ∩ F ≠ ∅** (it contains at least one final state of the NFA) |

### 5.3 Only the reachable subsets

With `n` states there are `2ⁿ` possible subsets, but **we only build the ones that can be reached** from the initial one. A queue is used:

```text
initial ← S
queue   ← [ S ]

while the queue is not empty:
    A ← take the first set out of the queue
    for each symbol a of the alphabet:
        B ← union of Δ(q, a) for every q in A
        if B is a new set:
            give it the next number (1, 2, 3, …) and put it in the queue
        δ(A, a) ← B

finals ← { A | A contains some final state of the NFA }
```

Important details:

- 🔢 The DFA states are **renamed 1, 2, 3, …** in the order in which they are discovered (the assignment allows renaming them).
- ⭕ The **empty set ∅** can also be a DFA state (a "trap" or dead state): it is reached when no state of the subset has a transition on that symbol, and from it everything goes back to ∅.
- 🧱 The resulting DFA is **complete**: every state has a transition for every symbol.

### 5.4 Step-by-step example (the one from the assignment, `input.txt`)

NFA with **S = {3, 5}**, **F = {1, 4}**, Σ = {a, b} and this Δ:

| State | a | b |
|:-:|:-:|:-:|
| 1 | {1, 5} | ∅ |
| 2 | {1} | ∅ |
| 3 | {2, 4} | ∅ |
| 4 | ∅ | {5} |
| 5 | {1, 5} | {4} |

| Step | DFA state | Subset | On **a** | On **b** |
|:-:|:-:|:-:|---|---|
| 1 | **1** (initial) | {3, 5} | {2,4} ∪ {1,5} = {1,2,4,5} → new, **2** | ∅ ∪ {4} = {4} → new, **3** |
| 2 | **2** | {1, 2, 4, 5} | {1,5} ∪ {1} ∪ ∅ ∪ {1,5} = {1,5} → new, **4** | ∅ ∪ ∅ ∪ {5} ∪ {4} = {4,5} → new, **5** |
| 3 | **3** | {4} | ∅ → new, **6** | {5} → new, **7** |
| 4 | **4** | {1, 5} | {1,5} → already exists, **4** | {4} → already exists, **3** |
| 5 | **5** | {4, 5} | {1,5} → already exists, **4** | {4,5} → already exists, **5** |
| 6 | **6** | ∅ | ∅ → **6** | ∅ → **6** |
| 7 | **7** | {5} | {1,5} → **4** | {4} → **3** |

- 🟢 **Final states of the DFA:** the subsets that contain 1 or 4 → states **2, 3, 4 and 5**.
- 📉 Out of the `2⁵ = 32` possible subsets, **only 7 are reachable**.

---

<a id="running"></a>

## ▶️ 6. How to run it (VS Code and terminal)

### 6.1 ✅ Requirements

- 🐍 **Python 3** installed (we used **3.13.13**). Check it with `python --version`.
- 📦 **Nothing needs to be installed with `pip`**: the program only uses Python's standard library.
- 🌐 A **web browser** to view the HTML and an **internet connection** so the diagrams can be drawn (see [section 8](#html)).

### 6.2 💻 From Visual Studio Code

1. 📂 Open the **project folder**: `File → Open Folder…`. *(Important: the program looks for `input.txt` in the folder it is run from, so you must open the folder and not just a single file.)*
2. 🐍 Install Microsoft's **Python** extension (recommended) and choose the interpreter: `Ctrl + Shift + P` → **Python: Select Interpreter**.
3. ▶️ Run it in one of these two ways:

   **Option A: the ▶ button (Run Python File)**
   Open `main.py` and click the ▶ button in the top-right corner. **`input.txt`** is used by default.

   **Option B: integrated terminal (the most flexible)**
   Open `Terminal → New Terminal` and type the commands from section 5.3.

4. 🌐 When it finishes, `resultado_automata.html` appears in the same folder and **opens by itself in your browser**.

### 6.3 ⌨️ From the terminal

Go to the project folder (`cd path\to\project`) and run:

```powershell
# 1) No arguments: uses the input.txt file in the current folder
python main.py

# 2) Naming the input file (recommended)
python main.py input.txt
python main.py casos_prueba.txt
```

**How do we tell the program which file to interpret?** By writing the file name right after `main.py`. That name reaches the program as its first argument (`sys.argv[1]`); the program opens it, reads it and hands it to the reader (`nfa_parser.py`).

Other ways of providing the input:

```powershell
# Windows PowerShell: pipe the file contents in
Get-Content casos_prueba.txt | python main.py
```

```bash
# CMD, Linux or macOS: input redirection
python main.py < casos_prueba.txt
```

```powershell
# Windows: if the "python" command does not respond, try the "py" launcher
py main.py casos_prueba.txt
```

> ⚠️ **PowerShell does not support `<`** (it raises an error). There, use `python main.py file.txt` or `Get-Content file.txt | python main.py`.
> 🐧 On Linux/macOS the command is usually `python3 main.py file.txt`.

### 6.4 🔀 Where does the program take its input from?

The program looks for the input **in this order**:

| Priority | Source | Example |
|:-:|---|---|
| 1️⃣ | The **file** given as an argument | `python main.py casos_prueba.txt` |
| 2️⃣ | Data arriving through **stdin** (pipe or redirection) | `python main.py < input.txt` |
| 3️⃣ | The **`input.txt`** file in the current folder | `python main.py` |

---

<a id="input"></a>

## 📥 7. How the input is read

### 7.1 📐 Format

```text
c                        ← number of cases (c > 0)
── for each case ──────────────────────────────────────
n                        ← number of states (1, 2, …, n)
S                        ← initial states, separated by blanks
Σ                        ← alphabet, symbols separated by blanks
F                        ← final states, separated by blanks
n rows                   ← one per state, in order: "state  cell_1 … cell_k"
```

Rules the program understands:

- ⭕ The **empty set ∅ is written `0`** (as the assignment requires). Since states go from 1 to n, `0` is never confused with a state.
- 🔤 The **alphabet** is made of lowercase letters from `a` to `z`, one per symbol.
- 🧾 Each **row** has the state and **one cell per symbol**, in the **same order** as the alphabet.
- 🧺 Each **cell** is `0` or a set between braces with the elements separated by blanks, for example `{1 5}`.
- 🧹 The reader tolerates **blank lines** between cases, Windows line endings (CRLF), files with a BOM, commas inside the braces (`{1, 5}`) and extra spaces (`{ 1 5 }`).

### 7.2 🔍 Annotated example (`input.txt`)

```text
1              ← 1 case
5              ← 5 states (1..5)
3 5            ← S = {3, 5}   (two initial states)
a b            ← Σ = {a, b}
1 4            ← F = {1, 4}
1 {1 5} 0      ← state 1: on 'a' goes to {1,5}; on 'b' goes to ∅
2 {1} 0        ← state 2: on 'a' goes to {1};   on 'b' goes to ∅
3 {2 4} 0      ← state 3: on 'a' goes to {2,4}; on 'b' goes to ∅
4 0 {5}        ← state 4: on 'a' goes to ∅;     on 'b' goes to {5}
5 {1 5} {4}    ← state 5: on 'a' goes to {1,5}; on 'b' goes to {4}
```

### 7.3 ⚙️ How the program interprets it

1. It reads **line by line**, skipping blank lines and **remembering each line number** (to give precise errors).
2. It turns the **initial** and **final** state lines into sets of numbers (a lone `0` means the empty set).
3. It validates the **alphabet** (letters `a–z`, no repeats).
4. Each **transition row** is split into "cells" with a regular expression that treats `{ ... }` as **a single cell**, even if it has spaces inside (that is why splitting on spaces is not enough). Each cell becomes a Python `set`.
5. It checks that every state is between `1` and `n`, that each row has the right number of cells and that no rows are missing.
6. With all that it creates one **`NFA`** object per case and hands it to the subset construction.

### 7.4 📄 Included example files

| File | Contents |
|---|---|
| 📌 `input.txt` | The **example from the assignment** (1 case, 5 states, two initial states). It is the file used by default. |
| 🧪 `casos_prueba.txt` | **3 different cases** to check that the program handles several cases at once (see table). |

| Case | What it shows | NFA → DFA | DFA final states |
|:-:|---|:-:|:-:|
| **1** | The assignment example: 2 initial states, alphabet `a b`, an ∅ state | 5 → 7 states | `2 3 4 5` |
| **2** | An NFA that accepts the strings that **end in `ab`** | 3 → 3 states | `3` |
| **3** | An alphabet of **3 symbols** (`a b c`), a state that is both initial and final, an ∅ state | 4 → 5 states | `1 4` |

---

<a id="console"></a>

## 🖥️ 8. What is printed to the console

For **each case** the program prints: the case number, the DFA's **initial state**, its **final states** and the **transition table**.

Output for `input.txt`:

```text
Case 1:
Initial state: 1
Final states: 2 3 4 5
DFA Transition Table:
State   a   b
1       2   3
2       4   5
3       6   7
4       4   3
5       4   5
6       6   6
7       4   3
```

| Line | What it means |
|---|---|
| `Case k:` | Case number |
| `Initial state:` | Initial state of the DFA (the subset S) |
| `Final states:` | Final states of the DFA, separated by spaces |
| `DFA Transition Table:` | Table title |
| `State  a  b …` | Header: the state and one column per symbol |
| `1  2  3 …` | One row per state: which state it goes to on each symbol |

0️⃣ If a DFA **has no final states**, `Final states: 0` is printed (the `0` is the assignment's notation for ∅).

<details>
<summary>📋 Expected output for <code>casos_prueba.txt</code> (cases 2 and 3)</summary>

```text
Case 2:
Initial state: 1
Final states: 3
DFA Transition Table:
State   a   b
1       2   1
2       2   3
3       2   1

Case 3:
Initial state: 1
Final states: 1 4
DFA Transition Table:
State   a   b   c
1       2   3   1
2       1   4   5
3       3   3   3
4       2   2   4
5       1   1   5
```

</details>

---

<a id="html"></a>

## 🌐 9. What the HTML shows

Every time the program runs, **`resultado_automata.html`** is generated in the current folder. If the program is run from a terminal, it **opens by itself in the browser**; otherwise, just double-click it.

It has a dark design in **indigo and pastel** tones, with the same information as the console and much more:

### 🧱 Page structure

| Part | Contents |
|---|---|
| 🚀 **Header** | Title, navigation bar and a button to jump to the results |
| 📘 **Overview** | A short explanation of the subset construction |
| 🎨 **Legend** | How to read the diagrams (initial, final, empty state, symbols) |
| 🗃️ **One card per case** | Summary, two diagrams and two tables (see below) |
| 👥 **Footer** | Authors and course |

### 🃏 What is inside each case

- 🏷️ **Case summary:** alphabet, initial (S) and final (F) states of the NFA, and the initial and final states of the DFA.
- 🔵 **NFA diagram** (*N — the input automaton*): the original automaton.
- 🟣 **DFA diagram** (*M — reachable subset states*): each state shows its number and, below it, the NFA subset it represents.
- 📋 **NFA transition table** and **DFA table**, the latter with an extra *NFA subset* column that says which set each state represents. Initial and final states carry a label (*start*, *final*).

### 🎨 How to read the diagrams

| Symbol | Meaning |
|:-:|---|
| ➡️ arrow entering the state | **Initial state** |
| 🟢 circle with a **double ring** | **Final state** |
| ⚪ plain circle | Regular state |
| ⭕ **dashed** circle with ∅ | Empty set (trap state) |
| 🏷️ small box on the arrow (`a, b`) | Symbols of the transition (several symbols between the same states are grouped into **a single** arrow) |

### 🕹️ Controls of each diagram

- ➕ / ➖ to zoom in or out, ↺ to go back to the initial view.
- ⤢ to **enlarge** the diagram to full width (automata with **more than 12 states** open this way automatically).
- 🖱️ Drag to move around, and `Ctrl + mouse wheel` to zoom.

### 🌍 Does it need internet?

The **diagrams** are drawn by the browser with **Graphviz** (`viz.js 3.11.0`, compiled to WebAssembly), which is downloaded from a CDN, and the fonts come from Google Fonts. **Without a connection** the diagrams are not drawn and a notice appears instead, but **the tables and all the other information remain visible**.

---

<a id="errors"></a>

## ⚠️ 10. Error handling

The program **does not crash with a traceback**: it checks the input and, if something is wrong, it shows a clear message in the terminal and exits with a non-zero exit code.

| Situation | Message |
|---|---|
| 📁 The given file does not exist | `Error: the input file 'no_existe.txt' does not exist.` |
| 📂 A folder was given instead of a file | `Error: 'tests' is not a file.` |
| 🔒 No read permission / invalid encoding | `Error: you do not have permission to read '…'.` · `Error: '…' is not a valid UTF-8 text file.` |
| ➕ Too many arguments | `Error: too many arguments. Usage: python main.py [input_file]` |
| 🚫 No input at all | `Error: no input provided. Use 'python main.py <input_file>', pipe the data through stdin, or create an input.txt file.` |
| 🔢 State out of range (1..n) | `Error: invalid input. Case 1: Line 7: state 9 in the transition of state 2 on 'a' is out of range (valid states: 1..2).` |
| 🔤 Invalid alphabet symbol | `Error: invalid input. Case 1: Line 4: invalid symbol 'ab'. Symbols must be single lowercase letters (a-z).` |
| 📏 Row with too many or too few cells | `Error: invalid input. Case 1: Line 6: expected 3 values (the state + one set per symbol of the alphabet), found 2.` |
| ✂️ Incomplete input | `Error: invalid input. Case 1: Unexpected end of input: expected transition row 2 of 2.` |
| 🧺 Badly written set (for example, an unclosed brace) | `Error: invalid input. Case 1: Line 6: the transition of state 1 on 'a' must be 0 or a set like {1 2}, got '{2'.` |

The invalid-input messages state the **case** and the **line number**, so the file can be fixed quickly.

There are also **warnings** (they do not stop the program):

- 📎 If lines are left over after the last announced case: `Warning: line N and the following lines are ignored (only c case(s) were announced).`
- 🌐 If the HTML could not be created or the browser could not be opened: `Warning: failed to create the HTML report: …` / `Warning: could not open the browser automatically. Open 'resultado_automata.html' manually.`

---
<a id="files"></a>

## 🗂️ 11. What each file does

### 🌳 Project structure

```text
📁 Subset Construction/
├── 🐍 main.py                  ← entry point
├── 🐍 nfa_parser.py            ← reads and validates the input
├── 🐍 models.py                ← NFA and DFA classes
├── 🐍 subset_builder.py        ← the algorithm
├── 🐍 html_generator.py        ← generates the HTML report
├── 📄 input.txt                ← example from the assignment
├── 📄 casos_prueba.txt         ← 3 test cases
├── 📝 README.md                ← this document
└── 🌐 resultado_automata.html  ← generated when the program runs
```

### 📚 Summary of each file

| File | What it does | Main pieces |
|---|---|---|
| 🐍 **`main.py`** | **Coordinates everything.** Decides where the input comes from, calls the reader and the construction, prints the table to the console, generates the HTML and opens it in the browser. It shows errors clearly. | `get_input_text()`, `read_input_file()`, `print_case()`, `open_in_browser()`, `fail()`, `main()` |
| 🐍 **`nfa_parser.py`** | **Reads and validates** the input text and turns it into `NFA` objects. It detects any format error and reports it with the line number. | `read_all_nfas_from_string()`, `InputFormatError`, validation helper functions |
| 🐍 **`models.py`** | Defines the **data**: what an NFA is and what a DFA is. | `NFA` class (states, initial, alphabet, final, `delta`, `get_transition()`) · `DFA` class (list of subsets, numbering, initial, final, `add_state()`, `set_transition()`) |
| 🐍 **`subset_builder.py`** | **Kozen's algorithm.** Takes an `NFA` and returns the `DFA`: it starts from S, uses a queue to visit only the reachable subsets and marks as final those that contain a final state of the NFA. | `SubsetConstructionBuilder.build_dfa()` |
| 🐍 **`html_generator.py`** | Creates `resultado_automata.html`. It prepares each case's data (nodes, grouped edges, tables) and inserts it into an HTML template with the design, the diagrams (Graphviz) and the zoom controls. | `HTMLReportGenerator.generate_html()`, `_nfa_data()`, `_dfa_data()`, `_merge_edges()` |
| 📄 **`input.txt`** | Example input: the assignment's case. Used by default. | |
| 📄 **`casos_prueba.txt`** | Example input with **3** different cases. | |
| 🌐 **`resultado_automata.html`** | **Generated automatically** when the program runs. It does not need to be edited. | |

---

<div align="center">

**Dilan Acevedo Rivera** · **Simón Santiago Soto Berrio**

🎓 SI2002 · Formal Languages · Professor **Sergio Ramírez Rico**

<sub>🌌 Subset Construction · EAFIT University</sub>

</div>
