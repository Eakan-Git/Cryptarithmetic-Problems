from os import close
import time
import re

# https://github.com/mb6386/Cryptarithmetic-Solver
# https://www.geeksforgeeks.org/expression-evaluation/


class CSP:
    def __init__(self, letters, domains, operators, lines):
        self.letters = letters
        self.domains = domains
        self.operators = operators
        self.lines = lines
        self.constraints = {}

        for letter in self.letters:
            self.constraints[letter] = []

    def addConstraint(self, constraint):
        for letter in constraint.letters:
            self.constraints[letter].append(constraint)

    def checkConstraints(self, variable, assignment):
        for constraint in self.constraints[variable]:
            if len(self.operators) == 1:
                if self.operators[0] == '+':
                    if not constraint.satisfiedLevel1_2Plus(assignment):
                        return False
                elif self.operators[0] == '-':
                    if not constraint.satisfiedLevel1_2Substract(assignment):
                        return False
                elif self.operators[0] == '*':
                    if not constraint.satisfiedPara(assignment, self.operators, self.lines):
                        return False
            else:
                if not constraint.satisfiedPara(assignment, self.operators, self.lines):
                    return False
        return True

    def backtrackingSearch(self, assignment={}):
        if len(assignment) == len(self.letters):
            return assignment

        unassigned = []
        for variable in self.letters:
            if variable not in assignment:
                unassigned.append(variable)

        MRV_letter = str()
        MRV = 10
        for letter in unassigned:
            if len(self.domains[letter]) <= MRV:
                MRV = len(self.domains[letter])
                MRV_letter = letter

        for value in self.domains[MRV_letter]:
            local_assignment = assignment.copy()
            local_assignment[MRV_letter] = value

            if self.checkConstraints(MRV_letter, local_assignment):
                result = self.backtrackingSearch(local_assignment)
                if result is not None:
                    return result
        return None


def precedence(op):
    if op == '+' or op == '-':
        return 1
    if op == '*':
        return 2
    return 0


def applyOp(a, b, op):
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b


def evaluate(tokens):
    values = []

    ops = []
    i = 0

    while i < len(tokens):
        if tokens[i] == '(':
            ops.append(tokens[i])
        elif tokens[i].isdigit():
            val = 0
            while (i < len(tokens) and
                    tokens[i].isdigit()):
                val = (val * 10) + int(tokens[i])
                i += 1
            values.append(val)
            i -= 1

        elif tokens[i] == ')':
            while len(ops) != 0 and ops[-1] != '(':
                val2 = values.pop()
                val1 = values.pop()
                op = ops.pop()
                values.append(applyOp(val1, val2, op))
            ops.pop()
        else:
            while (len(ops) != 0 and
                    precedence(ops[-1]) >=
                    precedence(tokens[i])):
                val2 = values.pop()
                val1 = values.pop()
                op = ops.pop()

                values.append(applyOp(val1, val2, op))
            ops.append(tokens[i])
        i += 1

    while len(ops) != 0:
        val2 = values.pop()
        val1 = values.pop()
        op = ops.pop()

        values.append(applyOp(val1, val2, op))
    return values[-1]


class CryptarithmeticSolver:
    def __init__(self, letters, words):
        self.letters = letters
        self.words = words

    def satisfiedLevel1_2Plus(self, assignment):
        if len(set(assignment.values())) < len(assignment):
            return False

        if len(assignment) == len(self.letters):
            solution = 0
            carry = len(self.words[-1])
            for letter in self.words[-1]:
                solution += assignment[letter] * (10 ** carry)
                carry -= 1

            single = 0
            sumAll = 0
            for i in range(len(self.words) - 1):
                carry = len(self.words[i])
                for letter in self.words[i]:
                    single += assignment[letter] * (10 ** carry)
                    carry -= 1
                sumAll += single
                single = 0

            return sumAll == solution

        return True

    def satisfiedLevel1_2Substract(self, assignment):
        if len(set(assignment.values())) < len(assignment):
            return False

        if len(assignment) == len(self.letters):
            solution = 0
            carry = len(self.words[-1])
            for letter in self.words[-1]:
                solution += assignment[letter] * (10 ** carry)
                carry -= 1

            single = 0
            substractAll = -1
            for i in range(len(self.words) - 1):
                carry = len(self.words[i])
                for letter in self.words[i]:
                    single += assignment[letter] * (10 ** carry)
                    carry -= 1
                if substractAll == -1:
                    substractAll = single
                else:
                    substractAll -= single
                single = 0

            return substractAll == solution

        return True

    def satisfiedLevel3Multiple(self, assignment, operators):
        if len(set(assignment.values())) < len(assignment):
            return False

        if len(assignment) == len(self.letters):
            solution = 0
            carry = len(self.words[-1])
            for letter in self.words[-1]:
                solution += assignment[letter] * (10 ** carry)
                carry -= 1

            single = 0
            totalAll = -1
            for i in range(len(self.words) - 1):
                carry = len(self.words[i])
                for letter in self.words[i]:
                    single += assignment[letter] * (10 ** carry)
                    carry -= 1
                if i >= 1:
                    if operators[i - 1] == '-':
                        if totalAll == -1:
                            totalAll = single
                        else:
                            totalAll -= single
                    else:
                        if totalAll == -1:
                            totalAll = single
                        else:
                            totalAll += single
                else:
                    totalAll = single
                single = 0

            return totalAll == solution

        return True

    def satisfiedPara(self, assignment, operators, lines):
        if len(set(assignment.values())) < len(assignment):
            return False

        if len(assignment) == len(self.letters):
            solution = 0
            carry = len(self.words[-1]) - 1
            for letter in self.words[-1]:
                solution += assignment[letter] * (10 ** carry)
                carry -= 1

            lines_number = []
            equalSign = lines.split('=')[0]
            for charac in equalSign:
                if charac not in operators:
                    charac = str(assignment[charac])
                lines_number.append(charac)
            elements = ''.join(map(str, lines_number))
            # print(elements)
            totalAll = evaluate(elements)
            # print(self.words[-1], totalAll, solution)
            return totalAll == solution
        return True

#SEND+MORE=MONEY
#['SEND', 'MORE', 'MONEY'] ['+'] ['SEND+MORE=MONEY']
def readFile(filename):
    with open(filename, 'r') as file:
        lines = file.readline()
        lines = lines.replace(' ', '')
        file.close()
        operators = re.findall('[+-/*()]', lines)
        words = list()
        if len(list(set(operators))) == 1:
            operators = list(set(operators))
            words = lines.split(operators[0])
            pop_out = words.pop(-1)
            words.append(pop_out.split('=')[0])
            words.append(pop_out.split('=')[1])
        else:
            words = re.findall(r"[\w']+", lines)
        print(lines)
        return words, operators, lines

#return unique letters
#AAABCC -> ABC
def getLetters(words):
    letters = []
    for word in words:
        for letter in word:
            if letter.upper() not in letters:
                letters.append(letter.upper())
    return letters


def initialAnalysis(values, words, letters):
    for letter in letters:
        values[letter] = list(range(0, 10))
    for word in words:
        values[word[0]] = list(range(1, 10))

    if len(words) == 3:
        if len(words[0]) == len(words[1]) and len(words[2]) > len(words[0]):
            values[words[2][0]] = [1]
        if words[0][-1] == words[1][-1]:
            values[words[2][-1]] = list(range(0, 10, 2))
    return values


def writeFile(filename, answer):
    file = open(filename, "w")
    answer = dict(sorted(answer.items()))
    print("Result: ", end="")
    for value in answer.values():
        print(value, end="")
        file.write(str(value))
    file.close()


if __name__ == "__main__":
    FILE_NAME_IN = input("Enter file name: ")
    words, operators, lines = readFile(FILE_NAME_IN)
    print("Please wait...")
    letters = getLetters(words)
    values = {}
    values = initialAnalysis(values, words, letters)
    csp = CSP(letters, values, operators, lines)
    solver = CryptarithmeticSolver(letters, words)
    csp.addConstraint(solver)
    t2 = time.time()
    answer = csp.backtrackingSearch()
    t1 = time.time()
    if answer is None:
        print("\nNo solution exists")
    else:
        FILE_NAME_OUT = "output.txt"
        writeFile(FILE_NAME_OUT, answer)
        print("\nThe result is written in " + FILE_NAME_OUT)
    print('Running time:', round(t1 - t2, 8), 'seconds')