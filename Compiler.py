# TODO add logic gates, add graphs, add displays, and points,
import pyperclip, webbrowser, keyboard, time, math
class Compiler:
    def __init__(self):
        self.keyword_functions = {"let": self.define_variable, "when": self.conditional_argument}
        self.variables = {}
        self.variable_count = 0
        self.operators = "-+/*^%"
    def split_string(self, data: str, line):
        """Splits a string into a list, seperated by ' ', and parses numbers correctly too."""
        # defining variables
        output = [""]
        how_deep_in_equation = 0
        equation_start = 0
        for char in enumerate(data):
            if char[1] == "(":
                how_deep_in_equation += 1
                if how_deep_in_equation == 0:
                    equation_start = char[0] + 1
            elif char[1] == ")":
                how_deep_in_equation -= 1
                if how_deep_in_equation == 0:
                    equation_start = 0
            elif char[1] == " " and how_deep_in_equation == 0:
                output.append("")
            else:
                output[-1] += char[1]
            # checking for errors
        if equation_start != 0:
            raise Exception(f"Error on line {line}, character {equation_start}. Unmatched parentheses")
        return output
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
            ["graph", "num", "bool", "point", "color"].index(data[1])
        except:
            raise Exception(f"Error on line {line}. '{data[1]}' Is not a valid variable type.")
        # updating self.variables, self.functions for variable reassignment, and incrementing self.variable_count
        self.variables[data[2]] = (data[1], self.variable_count)
        self.variable_count += 1
        self.keyword_functions[data[1]] = self.reassign_variable
        # assigning the variable's value equal to the variable type's initial value
        if len(data) == 3:
            return f"v{self.variable_count - 1} = {["x", "0", "0", "(0, 0), (0, 0, 0)"][["graph", "num", "bool", "point", "color)"].index(data[1])]}"
        elif len(data) == 5:
            return f"v{self.variable_count - 1} = 0\n{self.reassign_variable(data[2:5], line)}"
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
        if self.variables.get(data[0]) == None:
            raise Exception(f"Error on line {line}. Cannot reassign a variable that has not been defined")
        else:
            var_type = self.variables.get(data[0])[0]
            if var_type == "bool":
                if data[2] == "true":
                    return f"{data[0]} = 1"
                elif data[2] == "false":
                    return f"{data[0]} = 0"
                else:
                    raise Exception(f"Error on line {line}. '{data[0]}' cannot be assigned to a bool type variable.")
                pass
            elif var_type == "num":
                try:
                    return f"{data[0]} = {int(data[2])}"
                except:
                    # checking if data[2] is a math equation
                    for num in data[2].split(" "):
                        # removing any parentheses
                        if num[0] == "(":
                            del num[0]
                        if num[-1] == ")":
                            del num[-1]
                        # checking if the number has any variables
                        try:
                            float(num)
                            continue
                        except:
                            # checking if the number is a math operator
                            if len(num) == 1 and self.operators.__contains__(num):
                                continue
                            if self.variables.get(num) == None:
                                raise Exception(f"Error on line {line}. \'{num}\' is not defined")
                            if self.variables.get(num)[0] != "num":
                                raise Exception(f"Error on line {line}. \'{num}\' type variables cannot be used when changing the value of a num type variable")
                    return  f"{data[0]} = {data[2]}"
            elif var_type == "graph":
                pass
            elif var_type == "point":
                pass
            else:
                raise Exception(f"Error on line {line}. A variable has been defined with a non-existing variable type")
    def compile_line(self, data: str, line: int):
        seperated_data = self.split_string(data, line)
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
            compiled_lines.append(self.compile_line(file[i], i + 1))
        # turning the list into a string
        for i in range(len(compiled_lines)):
            compiled_string += compiled_lines[i] + "\n"
        return compiled_string + "\"Made using Desmos Script (https://github.com/Rufis72/Desmos-script)"