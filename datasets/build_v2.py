import argparse, json, random
from pathlib import Path

def add(rows, q, a, category):
    rows.append({"instruction": q.strip(), "response": a.strip(), "category": category})

def build(seed=42):
    random.seed(seed)
    rows = []

    concepts = {
        "python": [
            ("What is Python?", "Python is a general-purpose programming language known for readable syntax and a large ecosystem of libraries."),
            ("How does a Python function work?", "A Python function groups reusable instructions. It can receive parameters and return a value."),
            ("What is a Python list?", "A list is an ordered, mutable collection that can hold multiple values."),
            ("What is a Python dictionary?", "A dictionary stores key-value pairs and lets a program retrieve values using keys."),
            ("What does len do in Python?", "len returns the number of items in a collection or the number of characters in a string."),
            ("What is a Python exception?", "An exception represents an abnormal condition during execution and can be handled with constructs such as try and except."),
            ("What is a class in Python?", "A class defines a structure from which objects can be created, including attributes and methods."),
            ("What does import do in Python?", "import makes code from another module available to the current Python program."),
        ],
        "lua_luau": [
            ("What is Lua?", "Lua is a lightweight scripting language designed to be embedded in applications and games."),
            ("What is a table in Lua?", "A Lua table is a flexible data structure that can represent sequences, maps, and other collections."),
            ("What does local mean in Lua?", "local declares a variable or function with limited lexical scope."),
            ("How do functions work in Lua?", "A Lua function is a reusable block of code that can accept arguments and return values."),
            ("What is Luau?", "Luau is Roblox's scripting language, derived from Lua and extended for game development."),
            ("What is Workspace in Roblox?", "Workspace is the Roblox service that contains objects representing the visible 3D world."),
            ("What is a Part in Roblox?", "A Part is a basic 3D building object that can be positioned, resized, and configured with properties."),
            ("What is a LocalScript?", "A LocalScript contains client-side Luau code and is used for behavior that should run on a player's client."),
        ],
        "javascript": [
            ("What is JavaScript?", "JavaScript is a programming language widely used for interactive web applications and also used on servers and other platforms."),
            ("What is a JavaScript Promise?", "A Promise represents the eventual completion or failure of an asynchronous operation."),
            ("What does const mean in JavaScript?", "const declares a block-scoped binding that cannot be reassigned."),
            ("What is an array in JavaScript?", "An array is an ordered collection that can store multiple values."),
            ("What is an object in JavaScript?", "An object is a collection of properties where each property associates a key with a value."),
        ],
        "typescript": [
            ("What is TypeScript?", "TypeScript is a language built on JavaScript that adds static type syntax and tooling before code is typically compiled to JavaScript."),
            ("What is an interface in TypeScript?", "An interface describes the expected structure of a value and can be used for static type checking."),
            ("What is a type alias?", "A type alias gives a reusable name to a type expression."),
            ("Why use TypeScript?", "TypeScript can catch many type-related mistakes before runtime and improve editor tooling on larger codebases."),
        ],
        "cpp": [
            ("What is C++?", "C++ is a compiled general-purpose programming language with support for procedural, object-oriented, and generic programming."),
            ("What is a pointer in C++?", "A pointer is an object that stores a memory address or another pointer-related value."),
            ("What is a class in C++?", "A class defines a user-defined type containing data members and member functions."),
            ("What is a vector in C++?", "std::vector is a dynamic sequence container provided by the C++ standard library."),
        ],
        "csharp": [
            ("What is C#?", "C# is a general-purpose programming language commonly used with the .NET platform."),
            ("What is a class in C#?", "A C# class defines a reference type that can contain fields, properties, methods, and other members."),
            ("What is LINQ?", "LINQ is a set of language and library features for querying data using expressive C# syntax."),
            ("What is async in C#?", "async marks a method that can use await to work with asynchronous operations."),
        ],
        "java": [
            ("What is Java?", "Java is a general-purpose programming language designed around classes and commonly executed on the Java Virtual Machine."),
            ("What is a Java class?", "A Java class defines the fields and methods that instances of that class can have."),
            ("What is an interface in Java?", "An interface defines a contract of methods and other members that implementing classes can provide."),
            ("What is the JVM?", "The Java Virtual Machine executes Java bytecode and provides a runtime environment for Java programs."),
        ],
        "go": [
            ("What is Go?", "Go is a compiled programming language designed for simplicity, efficient execution, and concurrent programming."),
            ("What is a goroutine?", "A goroutine is a lightweight concurrent function execution managed by the Go runtime."),
            ("What is a Go interface?", "A Go interface describes behavior through method signatures and is satisfied implicitly by compatible types."),
            ("What is a slice in Go?", "A slice is a flexible view over an underlying array and is commonly used for dynamic sequences."),
        ],
        "rust": [
            ("What is Rust?", "Rust is a systems programming language focused on performance and memory safety without requiring a garbage collector."),
            ("What is ownership in Rust?", "Ownership is Rust's system for determining which part of a program is responsible for a value and when that value is dropped."),
            ("What is borrowing in Rust?", "Borrowing lets code temporarily access a value through a reference without taking ownership of it."),
            ("What is Result in Rust?", "Result represents either a successful value or an error and is commonly used for recoverable failures."),
        ],
        "php": [
            ("What is PHP?", "PHP is a server-side scripting language widely used for web development."),
            ("What is an associative array in PHP?", "An associative array stores values using named keys rather than only numeric positions."),
            ("What does echo do in PHP?", "echo sends one or more values to the output."),
        ],
        "sql": [
            ("What is SQL?", "SQL is a language used to define, query, manipulate, and manage data in relational database systems."),
            ("What does SELECT do in SQL?", "SELECT retrieves data from one or more tables or query expressions."),
            ("What is a primary key?", "A primary key identifies rows uniquely within a relational table."),
            ("What is a JOIN?", "A JOIN combines rows from related tables according to a specified relationship or condition."),
        ],
        "bash": [
            ("What is Bash?", "Bash is a command-line shell commonly used on Unix-like systems for interactive commands and scripts."),
            ("What does cd do in Bash?", "cd changes the shell's current working directory."),
            ("What does grep do?", "grep searches text for lines matching a pattern."),
            ("What is a shell script?", "A shell script is a text file containing commands that a shell can execute in sequence."),
        ],
        "html_css": [
            ("What is HTML?", "HTML is the markup language used to structure content on the web."),
            ("What is CSS?", "CSS is a stylesheet language used to control the presentation and layout of documents such as web pages."),
            ("What is a div element?", "A div is a generic HTML container that can group content for structure, styling, or scripting."),
            ("What is a CSS class selector?", "A class selector targets HTML elements whose class attribute contains the selected class name."),
        ],
        "gdscript": [
            ("What is GDScript?", "GDScript is a scripting language designed for the Godot game engine and its scene-based workflow."),
            ("What is a Node in Godot?", "A Node is a fundamental building block in Godot's scene tree and can provide behavior or structure."),
            ("What is a scene in Godot?", "A scene is a reusable tree of nodes that can represent a level, object, interface, or other game component."),
        ],
    }

    prompt_forms = [
        "{q}", "{q} Explain it simply.", "{q} Give a beginner-friendly answer.",
        "{q} Why is this useful?", "{q} Keep the explanation concise.",
        "{q} Explain the main idea first.", "{q} Answer for someone learning programming."
    ]

    for category, items in concepts.items():
        for q, a in items:
            for form in prompt_forms:
                add(rows, form.format(q=q), a, category)

    general = [
        ("Apa itu algoritma?", "Algoritma adalah rangkaian langkah yang terstruktur untuk menyelesaikan masalah atau mencapai tujuan tertentu."),
        ("Apa itu API?", "API adalah antarmuka yang memungkinkan satu perangkat lunak berkomunikasi dengan perangkat lunak lain."),
        ("Apa itu database?", "Database adalah sistem terstruktur untuk menyimpan, mengatur, dan mengambil data."),
        ("Apa itu debugging?", "Debugging adalah proses mencari penyebab kesalahan dalam program lalu memperbaikinya."),
        ("Apa itu machine learning?", "Machine learning adalah pendekatan yang membuat model mempelajari pola dari data untuk menghasilkan prediksi atau keluaran."),
        ("What is an operating system?", "An operating system manages hardware resources and provides common services used by applications."),
        ("Why is documentation useful?", "Documentation helps people understand how software works, how to use it, and why important decisions were made."),
        ("What is version control?", "Version control records changes to files so developers can review history, compare versions, and collaborate."),
    ]
    for q, a in general:
        for form in prompt_forms[:5]:
            add(rows, form.format(q=q), a, "general")

    science = [
        ("Why is the sky blue?", "Atmospheric molecules scatter shorter wavelengths of sunlight more strongly, making blue light prominent in the daytime sky."),
        ("What is photosynthesis?", "Photosynthesis is a process in which plants, algae, and some microorganisms use light energy to produce chemical energy from carbon dioxide and water."),
        ("What is gravity?", "Gravity is the attractive interaction associated with mass; near Earth it causes objects to accelerate toward the ground."),
        ("What is DNA?", "DNA is a molecule that stores hereditary information used by living organisms and many viruses."),
        ("What is evaporation?", "Evaporation is the change of a liquid into a gas that occurs at its surface."),
        ("What is an ecosystem?", "An ecosystem is a community of organisms interacting with one another and with their physical environment."),
    ]
    for q, a in science:
        for form in prompt_forms[:5]:
            add(rows, form.format(q=q), a, "science")

    for _ in range(3500):
        a = random.randint(2,999)
        b = random.randint(2,99)
        kind = random.randrange(4)
        if kind == 0:
            add(rows, f"Calculate {a} + {b}.", f"{a} + {b} = {a+b}.", "math")
        elif kind == 1:
            add(rows, f"Calculate {a} - {b}.", f"{a} - {b} = {a-b}.", "math")
        elif kind == 2:
            add(rows, f"Calculate {a} × {b}.", f"{a} × {b} = {a*b}.", "math")
        else:
            start = a + b
            add(rows, f"A value is {start}. If {a} is removed, what remains?", f"{start} - {a} = {b}, so {b} remains.", "math")

    for _ in range(1600):
        x, y, z = [random.randint(1,40) for _ in range(3)]
        total = x + y + z
        add(rows, f"A box has {x} red items, {y} blue items, and {z} green items. How many items are there?",
            f"There are {x} + {y} + {z} = {total} items.", "reasoning")

    seen = set()
    clean = []
    for row in rows:
        key = (row["instruction"], row["response"])
        if key not in seen:
            seen.add(key)
            clean.append(row)
    random.shuffle(clean)
    return clean

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="datasets/train.jsonl")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rows = build(args.seed)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps({"instruction":row["instruction"],"response":row["response"]}, ensure_ascii=False) + "\n")
    from collections import Counter
    counts = Counter(r["category"] for r in rows)
    print(f"XEN Dataset v2: {len(rows)} examples")
    print(f"Unique instructions: {len(set(r['instruction'] for r in rows))}")
    print(f"Unique responses: {len(set(r['response'] for r in rows))}")
    for k, v in sorted(counts.items()):
        print(f"{k:14s}: {v}")
    print(f"Wrote: {path}")

if __name__ == "__main__":
    main()
