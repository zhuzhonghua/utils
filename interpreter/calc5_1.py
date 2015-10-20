INTEGER='INTEGER'
ADD='ADD'
SUB='SUB'
MUL='MUL'
DIV='DIV'
EOF='EOF'

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token({type},{value})".format(type=self.type,value=self.value)

    def __expr__(self):
        return self.__str__()

class Interpreter:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[0]
        self.current_token = self.get_next_token()

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def integer(self):
        next_char = self.current_char
        self.advance()
        while self.current_char and self.current_char.isdigit():
            next_char += self.current_char
            self.advance()
        return int(next_char)

    def eat(self, type):
        if type == self.current_token.type:
            self.current_token = self.get_next_token()
        else:
            import pdb
            pdb.set_trace()
            raise Exception('error')

    def get_next_token(self):
        while self.current_char and self.current_char.isspace():
            self.advance()
            continue

        if self.current_char is None:
            return Token(EOF, None)

        if self.current_char.isdigit():
            return Token(INTEGER, self.integer())

        if self.current_char == '+':
            self.advance()
            return Token(ADD, '+')
        if self.current_char == '-':
            self.advance()
            return Token(SUB, '-')
        if self.current_char == '*':
            self.advance()
            return Token(MUL, '*')
        if self.current_char == '/':
            self.advance()
            return Token(DIV, '/')

    def factor(self):
        token = self.current_token
        self.eat(INTEGER)
        return token.value

    def term(self):
        result = self.factor()
        while self.current_token and self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
                result = result * self.factor()
            elif token.type == DIV:
                self.eat(DIV)
                result = result / self.factor()
        return result

    def expr(self):
        result = self.term()
        while self.current_token and self.current_token.type in (ADD, SUB):
            token = self.current_token
            if token.type == ADD:
                self.eat(ADD)
                result = result + self.term()
            elif token.type == SUB:
                self.eat(SUB)
                result = result - self.term()
        return result

if __name__ == "__main__":
    while True:
        text = raw_input('calc>')
        interp = Interpreter(text)
        result = interp.expr()
        print(result)
