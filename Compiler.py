# TODO add logic gates, add graphs / functions, add displays, add actual functions (func, vars there will be f1, f2, f3, etc), add 'for', add incrementing list of ___ to ___ (n = [n1...n2), add support for things like this: 'n = x(3) + n1 for n = [-499.499]', add append to lists, add strings
import unicodedata
class Compiler:
    def __init__(self):
        self.keyword_functions = {"let": self.define_variable, "when:": self.when, "raw": self.raw}
        self.variables = {}
        self.variable_count = 0
        self.operators = "-+/*^%"
        self.variable_types = ["function", "num", "bool", "point", "color", "array", "string"]


    def split_line(self, data: str, line):
        """Splits a string into a list, seperated by ' ', and parses numbers correctly too."""
        # defining variables
        output = [""]
        how_deep_in_equation = 0
        equation_start = 0
        how_deep_in_array = 0
        array_start = 0
        in_string = False
        string_start = 0
        string_starting_character = False # False = ', True = "
        for char in enumerate(data):
            if char[1] == "(":
                how_deep_in_equation += 1
                if how_deep_in_equation == 1:
                    equation_start = char[0] + 1
                output[-1] += "("
            elif char[1] == ")" and not in_string:
                how_deep_in_equation -= 1
                if how_deep_in_equation == 0:
                    equation_start = 0
                elif how_deep_in_equation == -1:
                    raise Exception(f"Error on line {line}, character {char[0]}. Unmatched parentheses.")
                output[-1] += ")"
            elif char[1] == " " and how_deep_in_equation == 0 and how_deep_in_array == 0 and not in_string:
                output.append("")
            elif char[1] == "[" and not in_string:
                how_deep_in_array += 1
                if how_deep_in_array == 1:
                    array_start = char[0] + 1
                output[-1] += "["
            elif char[1] == "]" and not in_string:
                how_deep_in_array -= 1
                if how_deep_in_array == 0:
                    array_start = 0
                elif how_deep_in_array == -1:
                    raise Exception(f"Error on line {line}, character {char[0]}. Unmatched parentheses.")
                output[-1] += "]"
            elif char[1] == "." and not in_string:
                output.append(".")
            elif char[1] == "\'":
                if in_string and string_starting_character:
                    output[-1] += "\'"
                elif in_string and not string_starting_character:
                    in_string = False
                    output[-1] += "\'"
                else:
                    output[-1] += "\'"
                    in_string = True
                    string_start = char[0] + 1
            elif char[1] == "\"":
                if in_string and not string_starting_character:
                    output[-1] += "\""
                elif in_string and string_starting_character:
                    in_string = False
                    output[-1] += "\""
                else:
                    output[-1] += "\""
                    in_string = True
                    string_start = char[0] + 1
            else:
                output[-1] += char[1]
        # checking for errors
        if how_deep_in_equation != 0:
            raise Exception(f"Error on line {line}, character {equation_start}. Unmatched parentheses")
        if how_deep_in_array != 0:
            raise Exception(f"Error on line {line}, character {array_start}. Unmatched parentheses")
        if in_string:
            raise Exception(f"Error on line {line}, character {string_start}. Unmatched quotes")
        return output


    def turn_string_into_array(self, data):
        """Turns a string into an array with character codes"""
        # defining variables
        output = []
        for char in data[1:-1]:
            output.append(str(ord(char)))
        return str(output)


    def raw(self, data: list, line: int, unseperated_line: str):
        """Returns any string after raw, intended to allow you to add pure desmos, if that's necessary"""
        # checking for errors
        if len(data) != 2:
            raise Exception(f"Error on line {line}. raw expected one argument, instead got {len(data)}")
        if data[1][0] != "'" and data[1][-1] != "\"":
            raise Exception(f"Error on line {line}. Expected a string after raw, instead got something else")
        return data[1][1:-1]


    def define_variable(self, data: tuple or list, line: int, unseparated_line):
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
            self.variable_types.index(data[1])
        except:
            raise Exception(f"Error on line {line}. '{data[1]}' Is not a valid variable type.")
        # updating self.variables, self.functions for variable reassignment, and incrementing self.variable_count
        self.variables[data[2]] = (data[1], self.variable_count)
        self.variable_count += 1
        # assigning the variable's value equal to the variable type's initial value
        if len(data) == 3:
            return f"v{self.variable_count - 1} = {["x", "0", "0", "(0, 0)", "(0, 0, 0)", "[]", "[]"][self.variable_types.index(data[1])]}"
        elif len(data) == 5:
            return f"v{self.variable_count - 1} = {["x", "0", "0", "(0, 0)", "(0, 0, 0)", "[]", "[]"][self.variable_types.index(data[1])]}\n{self.reassign_variable(data[2:5], line, unseparated_line)}"


    def when(self, data: list or tuple, line: int, unseparated_line: str):
        """Returns a string based of the passed in data to only run code when something is true, compiled into Desmos"""
        if data[2] == "let" or data[2] == "when:":
            raise Exception(f"Error on line {line}, cannot perform {data[2]} within when")
        if data[0][len(data[0]) - 1] != ":":
            raise Exception(f"Error on line {line}, expected ':' after {data[1]}")
        compiled_line = ""
        compiled_line = unseparated_line.split(" ")
        del compiled_line[0:2]
        return self.compile_line(compiled_line, line) + "{" + data[1] + "}"


    def builtin_class_method(self, data: list, line: int):
        """Performs a method, such as append, to a variable or builtin, such as an array type variable"""
        if self.variables.get(data[0]) == None:
            raise Exception(f"Error on line {line}. '{data[0]}' has not been defined")


    def reassign_variable(self, data: list, line: int, unseparated_line: str):
        """Reassigns a variable, also performs proper type checks, syntax, etc"""
        if self.variables.get(data[0]) == None:
            raise Exception(f"Error on line {line}. '{data[0]}' has not been defined")
        if (data[2][-1] == "'" or data[2][-1] == "\"") and self.variables.get(data[0])[0] != "string":
            raise Exception(f"Error on line {line}. A string cannot be assigned to a(n) {self.variables.get(data[0])[0]} type variable")
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
            # checking if the new value is just a number
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
                        # checking if a variable has not been defined
                        if self.variables.get(num) == None:
                            raise Exception(f"Error on line {line}. '{num}' is not defined")
                        # checking if a variable is of an illegal type for nums
                        if self.variables.get(num)[0] != "num":
                            raise Exception(f"Error on line {line}. '{num}' type variables cannot be used when changing the value of a num type variable")
                return  f"{data[0]} = {data[2]}"
        elif var_type == "function":
            return data[0] + " = " + data[2]
        elif var_type == "point":
                # checking if there are parentheses
                # checking the correct amount of numbers was passed in
                if data[2].count(",") != 1:
                    raise Exception(f"Error on line {line}. Expected two numbers within within parentheses, instead got {data[2].count(",") + 1}")
                # checking if every number is a valid number
                for num in enumerate(data[2].split(",")):
                    # checking if you can float the number
                    try:
                        float(num[1])
                        continue
                    except:
                        raise Exception(f"Error on line {line}. '{num[1].replace(" ", "")}' is not a valid number")
                return f"{data[0]} = ({data[2]})"
        elif var_type == "string":
            return data[0] + " = " + self.turn_string_into_array(data[2])
        elif var_type == "array":
            # checking for errors
            if data[2][0] != "[":
                raise Exception(f"Error on line {line}. Expected '[' before {data[1:]}")
            if data[2][-1] != ']':
                raise Exception(f"Error on line {line}. Expected ']' after {data[0:-1]}")
            # returning the string
            return data[0] + " = " + data[2]
        else:
            raise Exception(f"Error on line {line}. A variable has been defined with a non-existing variable type")


    def compile_line(self, data: str, line: int):
        seperated_data = self.split_line(data, line)
        func = self.keyword_functions.get(seperated_data[0])
        if func == None:
            if self.variables.get(seperated_data[0]) != None:
                return self.reassign_variable(seperated_data, line, data)
            else:
                raise Exception(f"Error on line {line}. '{seperated_data[0]}' is not defined")
        return func(seperated_data, line, data)


    def compile(self, file: str):
        """Compiles the passed in file"""
        # defining variables
        compiled_lines = []
        compiled_string = ""
        file = open(file).readlines()
        # reading and compiling each line
        for i in range(len(file)):
            compiled_lines.append(self.compile_line(file[i].replace("\n", ""), i + 1))
        # turning the list into a string
        for i in range(len(compiled_lines)):
            compiled_string += compiled_lines[i] + "\n"
        return compiled_string + "\"Made using Desmos Script (https://github.com/Rufis72/Desmos-script)"
