# TODO add logic gates, add graphs, add displays, and points,
import pyperclip, webbrowser, keyboard, time
class Compiler:
    def __init__(self):
        self.keyword_functions = {"let": self.define_variable, "when": self.conditional_argument}
        self.variables = {}
        self.variable_count = 0
    def define_variable(self, data: tuple or list, line: int):
        """Returns a string based off the passed in data to define a variable, compiled into Desmos"""
        # checking if there is too little, or too much data passed in
        if len(data) < 3:
            raise Exception(f"Error on line {line}, missing variable definition arguments")
        if len(data) > 5:
            raise Exception(f"Error on line {line}, too many passed in arguments")
        # checking if the variable is either a builtin function, or a already defined variable
        if self.keyword_functions.get(data[1]) != None:
            if self.variables.get(data[1]) == None:
                raise Exception(f"Error on line {line}. You cannot define a variable with the name of a builtin function.")
            else:
                raise Exception(f"Error on line {line}. A variable with the name '{data[1]}' has already been defined.")
        # checking if the variable type is valid
        try:
            ["graph", "num", "bool", "point"].index(data[1])
            # updating self.variables, self.functions for variable reassignment, and incrementing self.variable_count
            self.variables[data[1]] = (data[0], self.variable_count)
            self.variable_count += 1
            self.keyword_functions[data[1]] = self.reasign_variable
            if len(data) == 3:
                return f"v{self.variable_count - 1} = 0"
            elif len(data) == 5:
                return f"v{self.variable_count - 1} = 0 \b{self.reasign_variable([data[2], data[4]], line)}"
        except:
            raise Exception(f"Error on line {line}. '{data[1]}' Is not a valid variable type.")
    def conditional_argument(self, data: list or tuple, line: int):
        """Returns a string based of the passed in data to only run code when something is true, compiled into Desmos"""
        try:
            ["let", "when"].index(data[1])
            raise Exception(f"Error on line {line}, cannot perform {data[1]} within when")
        except:
            if data[0][len(data[0]) - 1] != ":":
                raise Exception(f"Error on line {line}, expected ':' after {data[0]}")
            return self.compile_line(data[1: len(data) - 1], line) + "{" + data[0] + "}"
    def reassign_variable(self, data, line):
        pass
    def compile_line(self, data: str, line: int):
        seperated_data = data.split(" ")
        func = self.keyword_functions.get(seperated_data[0])
        if func == None:
            raise Exception(f"Error on line {line}. '{data[0]}' is not a keyword, nor defined")
        return func(seperated_data, line)
    def compile(self, file: str):
        """Compiles the passed in file"""
        # defining variables
        compiled_lines = []
        compiled_string = ""
        file = open(file).readlines()
        # reading and compiling each line
        for i in range(len(file)):
            compiled_lines.append(self.compile_line(file[i], i))
        # turning the list into a string
        compiled_string = compiled_lines[0]
        for i in range(len(compiled_lines) - 1):
            compiled_string += compiled_lines[i] + "\b"
        return compiled_string
print(Compiler().compile("testing compilation file"))
