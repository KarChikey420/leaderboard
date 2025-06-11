import sqlite3

questions = [
    ("Python", "What is the output of: print(type([]))?", "list", "dict", "tuple", "set", 1),
    ("Python", "Which keyword is used for function in Python?", "def", "function", "fun", "lambda", 1),
    ("Python", "Which of the following is not a Python data type?", "list", "set", "tuple", "array", 4),
    ("Python", "Which operator is used for exponentiation in Python?", "^", "**", "//", "%%", 2),
    ("Python", "How do you start a comment in Python?", "#", "//", "--", "/*", 1),
    ("Python", "Which method is used to add an element in a list?", "add()", "append()", "insert()", "push()", 2),
    ("Python", "Which of the following is used to handle exceptions?", "try-catch", "try-except", "catch-try", "try-throw", 2),
    ("Python", "Which of these is a mutable type?", "tuple", "int", "list", "str", 3),
    ("Python", "What will `len('Hello')` return?", "4", "5", "6", "Error", 2),
    ("Python", "Which of the following converts a string to an integer?", "str()", "int()", "float()", "bool()", 2),

    ("Java", "Which keyword is used to inherit a class in Java?", "implement", "extends", "inherits", "interface", 2),
    ("Java", "Java is:", "Interpreted", "Compiled", "Both", "None", 3),
    ("Java", "What is JVM?", "Java Variable Machine", "Java Virtual Machine", "Java Verified Machine", "None", 2),
    ("Java", "Which method is the entry point in Java programs?", "start()", "main()", "init()", "run()", 2),
    ("Java", "What is the extension of Java bytecode files?", ".java", ".class", ".byte", ".jbc", 2),
    ("Java", "Which package contains Scanner class?", "java.io", "java.util", "java.lang", "java.scan", 2),
    ("Java", "What is the size of int in Java?", "2 bytes", "4 bytes", "8 bytes", "Depends on system", 2),
    ("Java", "Which keyword prevents inheritance?", "static", "final", "private", "super", 2),
    ("Java", "Which of these is not an access modifier?", "public", "private", "protected", "package", 4),
    ("Java", "What is used to create an object in Java?", "create", "new", "init", "obj", 2),

    ("C", "Which symbol is used to end a statement in C?", ".", ";", ":", "!", 2),
    ("C", "Which function is used to print in C?", "print()", "cout", "printf()", "echo()", 3),
    ("C", "Which header file is required for printf?", "conio.h", "stdlib.h", "stdio.h", "string.h", 3),
    ("C", "Which loop is guaranteed to run at least once?", "for", "while", "do-while", "None", 3),
    ("C", "Which is not a data type in C?", "int", "float", "bool", "char", 3),
    ("C", "Which keyword is used to define a constant?", "const", "define", "constant", "static", 1),
    ("C", "What is the value of uninitialized global variable?", "0", "garbage", "null", "none", 1),
    ("C", "Which operator is used to allocate memory?", "new", "malloc", "allocate", "init", 2),
    ("C", "Which of the following is not a loop?", "for", "do", "repeat", "while", 3),
    ("C", "What does sizeof() return?", "Length of variable", "Size in bytes", "Address", "None", 2)
]

def insert_questions():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO questions (section, question, option1, option2, option3, option4, answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, questions)
    conn.commit()
    conn.close()
    print("Questions inserted successfully.")

if __name__ == "__main__":
    insert_questions()
