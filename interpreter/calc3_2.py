INTEGER='INTEGER'
PLUS='PLUS'
MINUS='MINUS'
EOF='EOF'

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "TOKEN({type},{value})".format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

class Interpreter:
    def __init__(self, text):
        self.text = text
        self.pos = 0

        self.current_char = ''
        self.current_token = None

    def skip_whitespace(self):
        text = self.text
        if self.pos < len(text) and text[self.pos].isspace():
            self.pos += 1

    def advance(self):
        self.pos += 1
        self.skip_whitespace()
        if self.pos < len(self.text):
            self.current_char = text[self.pos]
        else:
            self.current_char = None

    def get_next_token(self):
        if self.current_char.isdigit():
            next_char = self.current_char
            self.advance()
            if self.current_char and self.current_char.isdigit():
                next_char += self.current_char
                self.advance()

            return Token(INTEGER, int(next_char))

        if self.current_char == '+':
            self.advance()
            return Token(PLUS, '+')

        if self.current_char == '-':
            self.advance()
            return Token(MINUS, '-')

    def integer(self):
        self.current_token = self.get_next_token()

    def term(self):
        self.integer()
        value = self.current_token.value
        self.current_token = self.get_next_token()
        return value

    def expr(self):
        result = self.term()
        while self.current_token and self.current_token.type in (PLUS, MINUS):
            if self.current_token.type == PLUS:
                result = result + self.term()
            else:
                result = result - self.term()
        return result

if __name__ == "__main__":
    while True:
        text = raw_input("calc >")
        inte = Interpreter(text)
        result = inte.expr()
        print(result)
