qualifiers = ['integer','boolean','real']
operators = ['-','+','/','*']
relops = ['==', '!=' ,'>' ,'<' ,'<=' ,'=>']

class parser:
    def __init__(self,lex):
        self.tokens = lex
        self.globcount = 0
        self.fpoint = 0
        self.spoint = 0
    def GetOptFuncDef(self,count):
        if self.tokens[count]['token'] == 'function':
            new = '<Opt Function Definitions> -> <Function Definitions>'
            self.tokens[count]['productions'].append(new)
            count = self.FuncDef(count)
        elif self.tokens[count]['token'] == '#':
            new = '<Opt Function Definitions> -> <Empty>'
            self.tokens[count]['productions'].append(new)
        else:
            line = self.tokens[count]['line']
            print(f'Syntax error at line {line} (Maybe missing #)')
            quit()
        return count

    def FuncDef(self,count):
        try:
            while self.tokens[count]['token'] != '#':
                tempcount = count + 1
                new = '<Function Definitions> -> <Function>'
                while self.tokens[tempcount]['token'] != '#':
                    if self.tokens[tempcount]['token'] == 'function':
                        new = '<Function Definitions> -> <Function> <Function Definitions>'
                    tempcount += 1
                if self.tokens[count]['token'] == 'function':
                    self.tokens[count]['productions'].append(new)
                    new = '<Function> -> function  <Identifier> (<Opt Parameter List>) <Opt Declaration List> <Body>'
                    self.tokens[count]['productions'].append(new)
                    count = self.Func(count)
                count += 1
        except:
            line = self.tokens[count]['line']
            print(f'Syntax error at line {line} (Maybe missing #)')
            quit()
        count = tempcount
        return count

    def Func(self,count):
        tempcount = count + 1
        if self.tokens[tempcount]['lexeme'] == 'identifier':
            new = '<Function> -> <Identifier>'
            self.tokens[count]['productions'].append(new)
            new = '<Identifier>'
            self.tokens[tempcount]['productions'].append(new)
            tempcount += 1
        else:
            line = self.tokens[tempcount]['line']
            print(f'Syntax error at line {line} (Maybe missing function identifier)')
            quit()
        if self.tokens[tempcount]['token'] != '(':
            line = self.tokens[tempcount]['line']
            print(f'Syntax error at line {line} (Maybe missing separator)')
            quit()
        tempcount += 1
        new = '<Function> -> <Opt Parameter List>'
        self.tokens[count]['productions'].append(new)
        if self.tokens[tempcount]['lexeme'] == 'identifier':
            new = '<Opt Parameter List> -> <Parameter List>'
            self.tokens[count]['productions'].append(new)
            while True:
                tempcount = self.Param(tempcount)
                if self.tokens[tempcount]['token'] == ',' and self.tokens[tempcount+1]['lexeme'] == 'identifier':
                    new = '<Parameter List> -> <Parameter>,<Parameter List>'
                    self.tokens[count]['productions'].append(new)
                    tempcount = self.Param(tempcount)
                elif self.tokens[tempcount]['token'] == ')':
                    new = '<Parameter List> -> <Parameter>'
                    self.tokens[count]['productions'].append(new)
                    tempcount += 1
                    break
                else:
                    line = self.tokens[tempcount]['line']
                    print(f'Syntax error at line {line} (Invalid parameter list, Possible fix : (missing separators))')
                    quit()
        elif self.tokens[tempcount]['token'] == ')':
            new = '<Opt Parameter List> -> <Empty>'
            self.tokens[count]['productions'].append(new)
            tempcount += 1
        else:
            line = self.tokens[tempcount]['line']
            print(f'Syntax error at line {line} (Invalid parameter list Possible fix : (invalid parameters))')
            quit()


        new = '<Function> -> <Opt Declaration List>'
        self.tokens[count]['productions'].append(new)
        if self.tokens[tempcount]['token'] in qualifiers and self.tokens[tempcount+1]['lexeme'] == 'identifier':
            tempcount += 2
            new = '<Opt Declaration List> -> <Declaration List>'
            self.tokens[count]['productions'].append(new)
            while True:
                if self.tokens[tempcount-1]['lexeme'] == 'identifier' and self.tokens[tempcount-2]['token'] in qualifiers:
                    self.Dec(tempcount-2)
                if self.tokens[tempcount]['token'] == ',' and self.tokens[tempcount-1]['lexeme'] == 'identifier':
                    tempcount += 2
                elif self.tokens[tempcount]['token'] == ';':
                    if self.tokens[tempcount+1]['token'] == '{':
                        new = '<Declaration List> -> <Declaration>'
                        self.tokens[count]['productions'].append(new)
                        tempcount += 2
                        break
                    else:
                        new = '<Declaration List> -> <Declaration>;<Declaration List>'
                        self.tokens[count]['productions'].append(new)
                        tempcount += 3
                else:
                    line = self.tokens[tempcount]['line']
                    print(f'Syntax error at line {line} (Invalid declaration list, Possible fix : (missing separators))')
                    quit()
        elif self.tokens[tempcount]['token'] == '{':
            new = '<Opt Declaration List> -> <Empty>'
            self.tokens[count]['productions'].append(new)
            tempcount += 1
        else:
            line = self.tokens[tempcount]['line']
            print(f'Syntax error at line {line} (Invalid declaration list Possible fix : (incorect declaration format))')
            quit()
        try:
            new = '<Function> -> <Body>'
            self.tokens[count]['productions'].append(new)
            self.GetStateList(count,tempcount,'}')
            tempcount = self.spoint
        except:
            line = self.tokens[tempcount-1]['line']
            print(f'Syntax error at line {line} (Invalid function (maybe missing end separator))')
            quit()
        count = tempcount
        return count

    def Param(self,count):
        new = '<Parameter> -> <IDs> <Qualifier>'
        self.tokens[count]['productions'].append(new)
        new = '<Parameter> -> <IDs>'
        self.tokens[count]['productions'].append(new)
        count = self.IDs(count)
        new = '<Parameter> -> <Qualifier>'
        self.tokens[count]['productions'].append(new)
        new = '<Parameter> -> <Qualifier>'
        self.tokens[count]['productions'].append(new)
        count = self.Qual(count)
        return count

    def IDs(self,count):
        count += 1
        while True:
            if self.tokens[count]['token'] == ',' and self.tokens[count+1]['lexeme'] == 'identifier':
                new = '<IDs> -> <Identifier> , <IDs>'
                self.tokens[count-1]['productions'].append(new)
                count += 2
            else:
                new = '<IDs> -> <Identifier>'
                self.tokens[count-1]['productions'].append(new)
                break
        return count

    def Qual(self,count):
        for qualifier in qualifiers:
            if qualifier == self.tokens[count]['token']:
                new = f'<Qualifier> -> {qualifier}'
                self.tokens[count]['productions'].append(new)
                count += 1
        return count

    def Dec(self,count):
        new = '<Declaration> -> <Qualifier > <IDs>'
        self.tokens[count]['productions'].append(new)
        new = '<Declaration> -> <Qualifier>'
        self.tokens[count]['productions'].append(new)
        self.Qual(count)
        count += 1
        new = '<Declaration> -> <IDs>'
        self.tokens[count]['productions'].append(new)
        self.IDs(count)
        return count

    def GetOptDecList(self,count):
        tempcount = count + 1
        if self.tokens[tempcount]['token'] in qualifiers and self.tokens[tempcount+1]['lexeme'] == 'identifier':
            tempcount += 2
            new = '<Opt Declaration List> -> <Declaration List>'
            self.tokens[count]['productions'].append(new)
            while True:
                if self.tokens[tempcount-1]['lexeme'] == 'identifier' and self.tokens[tempcount-2]['token'] in qualifiers:
                    self.Dec(tempcount-2)
                if self.tokens[tempcount]['token'] == ',' and self.tokens[tempcount-1]['lexeme'] == 'identifier':
                    tempcount += 2
                elif self.tokens[tempcount]['token'] == ';':
                    if self.tokens[tempcount+1]['token'] not in qualifiers:
                        new = '<Declaration List> -> <Declaration>'
                        self.tokens[count]['productions'].append(new)
                        tempcount += 1
                        break
                    else:
                        new = '<Declaration List> -> <Declaration>;<Declaration List>'
                        self.tokens[count]['productions'].append(new)
                        tempcount += 3
                else:
                    line = self.tokens[tempcount]['line']
                    print(f'Syntax error at line {line} (Invalid declaration list, Possible fix : (missing separators))')
                    quit()
        else:
            new = '<Opt Declaration List> -> <Empty>'
            self.tokens[count]['productions'].append(new)
        count = tempcount
        return count

    def GetStateList(self,functionpoint,startpoint,endchar):
        tempcount = startpoint
        count = functionpoint
        First = True
        while True:
            if endchar == 'none' and not First:
                self.fpoint = count
                self.spoint = tempcount
                break
            First = False
            #check for compound
            if self.tokens[tempcount]['token'] == '{':
                new = '<Statement List> -> <Statement> <Statement List>'
                self.tokens[count]['productions'].append(new)
                new = '<Statement> -> <Compound>'
                self.tokens[count]['productions'].append(new)
                new = '<Compound> -> {  <Statement List>  }'
                self.tokens[tempcount]['productions'].append(new)
                new = '<Compound> -> {'
                self.tokens[tempcount]['productions'].append(new)
                try:
                    self.GetStateList(count,tempcount+1,'}')
                    tempcount = self.spoint
                    new = '<Compound> -> }'
                    self.tokens[tempcount]['productions'].append(new)
                except:
                    line = self.tokens[tempcount-1]['line']
                    print(f'Syntax error at line {line} (Invalid compound (maybe missing end separator))')
                    quit()
            #check for assign
            elif self.tokens[tempcount]['lexeme'] == 'identifier' and self.tokens[tempcount+1]['token'] == '=':
                new = '<Statement List> -> <Statement> <Statement List>'
                self.tokens[count]['productions'].append(new)
                new = '<Statement> -> <Assign>'
                self.tokens[count]['productions'].append(new)
                new = '<Assign> -> <Identifier> = <Expression>;'
                self.tokens[tempcount]['productions'].append(new)
                new = '<Assign> -> <Identifier>'
                self.tokens[tempcount]['productions'].append(new)
                tempcount += 2
                try:
                    self.tokens[tempcount]['productions'] += self.Expression(tempcount)
                    self.Primary(tempcount)
                    tempcount = self.globcount
                except:
                    line = self.tokens[tempcount-1]['line']
                    print(f'Syntax error at line {line} (Invalid assign (maybe missing separator))')
                    quit()
                while True:
                    if self.tokens[tempcount]['token'] == ';':
                        break
                    else:
                        try:
                            self.tokens[tempcount+1]['productions'] += self.Expression(tempcount+1)
                            self.Primary(tempcount+1)
                        except:
                            line = self.tokens[tempcount-1]['line']
                            print(f'Syntax error at line {line} (Invalid assign (maybe missing separator))')
                            quit()
                        tempcount = self.globcount

            #check for if
            elif self.tokens[tempcount]['token'] == 'if' and self.tokens[tempcount+1]['token'] == '(':
                functionp = tempcount
                new = '<Statement List> -> <Statement> <Statement List>'
                self.tokens[count]['productions'].append(new)
                new = '<Statement> -> <If>'
                self.tokens[count]['productions'].append(new)
                new = '<If> -> if  (<Condition>) <Statement> endif | if (<Condition>) <Statement>   else  <Statement>  endif '
                self.tokens[tempcount]['productions'].append(new)
                tempcount += 2
                try:
                    self.tokens[tempcount]['productions'] += self.Expression(tempcount)
                    self.Primary(tempcount)
                    tempcount = self.globcount
                except:
                    line = self.tokens[tempcount-1]['line']
                    print(f'Syntax error at line {line} (Invalid print (maybe missing separator))')
                    quit()

                while True:
                    if self.tokens[tempcount]['token'] + self.tokens[tempcount+1]['token'] in relops:
                        lop = self.tokens[tempcount]['token'] + self.tokens[tempcount+1]['token']
                        new = f'<Relop> -> {lop}'
                        self.tokens[tempcount]['productions'].append(new)
                        new = f'<Relop> -> {lop}'
                        self.tokens[tempcount+1]['productions'].append(new)
                        tempcount += 2
                        break
                    elif self.tokens[tempcount]['token'] in relops:
                        lop = self.tokens[tempcount]['token']
                        new = f'<Relop> -> {lop}'
                        self.tokens[tempcount]['productions'].append(new)
                        tempcount += 1
                        break
                    else:
                        try:
                            self.tokens[tempcount+1]['productions'] += self.Expression(tempcount+1)
                            self.Primary(tempcount+1)
                        except:
                            line = self.tokens[tempcount-1]['line']
                            print(f'Syntax error at line {line} (Invalid if (maybe missing separator))')
                            quit()
                        tempcount = self.globcount

                try:
                    self.tokens[tempcount]['productions'] += self.Expression(tempcount)
                    self.Primary(tempcount)
                    tempcount = self.globcount
                except:
                    line = self.tokens[tempcount-1]['line']
                    print(f'Syntax error at line {line} (Invalid print (maybe missing separator))')
                    quit()

                while True:
                    if self.tokens[tempcount]['token'] == ')':
                        break
                    else:
                        try:
                            self.tokens[tempcount+1]['productions'] += self.Expression(tempcount+1)
                            self.Primary(tempcount+1)
                        except:
                            line = self.tokens[tempcount-1]['line']
                            print(f'Syntax error at line {line} (Invalid if (maybe missing separator))')
                            quit()
                        tempcount = self.globcount

                try:
                    self.GetStateList(functionp,tempcount+1,'endif')
                    tempcount = self.spoint
                except:
                    line = self.tokens[tempcount-1]['line']
                    print(f'Syntax error at line {line} (Invalid compound (maybe missing end separator))')
                    quit()


            #check for else
            elif self.tokens[tempcount]['token'] == 'else':
                new = '<If> -> if (<Condition>) <Statement> else <Statement> endif'
                self.tokens[count]['productions'].append(new)

            #check for return
            elif self.tokens[tempcount]['token'] == 'return':
                new = '<Statement List> -> <Statement> <Statement List>'
                self.tokens[count]['productions'].append(new)
                new = '<Statement> -> <Return>'
                self.tokens[count]['productions'].append(new)
                new = '<Return> -> return; | return <Expression>;'
                self.tokens[tempcount]['productions'].append(new)
                if self.tokens[tempcount+1]['token'] == ';':
                    new = '<Return> -> return;'
                    self.tokens[tempcount]['productions'].append(new)
                    tempcount += 1
                else:
                    new = '<Return> -> return <Expression>;'
                    self.tokens[tempcount]['productions'].append(new)
                    while True:
                        if self.tokens[tempcount]['token'] == ';':
                            break
                        else:
                            try:
                                self.tokens[tempcount+1]['productions'] += self.Expression(tempcount+1)
                                self.Primary(tempcount+1)
                            except:
                                line = self.tokens[tempcount-1]['line']
                                print(f'Syntax error at line {line} (Invalid return (maybe missing separator))')
                                quit()
                            tempcount = self.globcount

            #check for print
            elif self.tokens[tempcount]['token'] == 'put' and self.tokens[tempcount+1]['token'] == '(':
                new = '<Statement List> -> <Statement> <Statement List>'
                self.tokens[count]['productions'].append(new)
                new = '<Statement> -> <Print>'
                self.tokens[count]['productions'].append(new)
                new = '<Print> -> put (<Expression>);'
                self.tokens[tempcount]['productions'].append(new)
                new = '<Print> -> put'
                self.tokens[tempcount]['productions'].append(new)
                tempcount += 2
                try:
                    self.tokens[tempcount]['productions'] += self.Expression(tempcount)
                    self.Primary(tempcount)
                    tempcount = self.globcount
                except:
                    line = self.tokens[tempcount-1]['line']
                    print(f'Syntax error at line {line} (Invalid print (maybe missing separator))')
                    quit()
                while True:
                    if self.tokens[tempcount]['token'] == ')' and self.tokens[tempcount+1]['token'] == ';':
                        tempcount += 1
                        break
                    else:
                        try:
                            self.tokens[tempcount+1]['productions'] += self.Expression(tempcount+1)
                            self.Primary(tempcount+1)
                        except:
                            line = self.tokens[tempcount-1]['line']
                            print(f'Syntax error at line {line} (Invalid print (maybe missing separator))')
                            quit()
                        tempcount = self.globcount
            #check for scan
            elif self.tokens[tempcount]['token'] == 'get' and self.tokens[tempcount+1]['token'] == '(':
                new = '<Statement List> -> <Statement> <Statement List>'
                self.tokens[count]['productions'].append(new)
                new = '<Statement> -> <Scan>'
                self.tokens[count]['productions'].append(new)
                new = '<Scan> -> get (<IDs>);'
                self.tokens[tempcount]['productions'].append(new)
                new = '<Scan> -> get'
                self.tokens[tempcount]['productions'].append(new)
                tempcount += 2
                try:
                    tempcount = self.IDs(tempcount)
                    if self.tokens[tempcount]['token'] != ')' or self.tokens[tempcount+1]['token'] != ';':
                        line = self.tokens[tempcount-1]['line']
                        print(f'Syntax error at line {line} (Invalid scan (maybe missing separator))')
                        quit()
                    tempcount += 1
                except:
                    line = self.tokens[tempcount-1]['line']
                    print(f'Syntax error at line {line} (Invalid scan (maybe missing separator))')
                    quit()



            #check for while
            elif self.tokens[tempcount]['token'] == 'while' and self.tokens[tempcount+1]['token'] == '(':
                functionp = tempcount
                new = '<Statement List> -> <Statement> <Statement List>'
                self.tokens[count]['productions'].append(new)
                new = '<Statement> -> <While>'
                self.tokens[count]['productions'].append(new)
                new = '<While> -> while (<Condition>) <Statement>'
                self.tokens[tempcount]['productions'].append(new)
                tempcount += 2
                try:
                    self.tokens[tempcount]['productions'] += self.Expression(tempcount)
                    self.Primary(tempcount)
                    tempcount = self.globcount
                except:
                    line = self.tokens[tempcount-1]['line']
                    print(f'Syntax error at line {line} (Invalid print (maybe missing separator))')
                    quit()

                while True:
                    if self.tokens[tempcount]['token'] + self.tokens[tempcount+1]['token'] in relops:
                        lop = self.tokens[tempcount]['token'] + self.tokens[tempcount+1]['token']
                        new = f'<Relop> -> {lop}'
                        self.tokens[tempcount]['productions'].append(new)
                        new = f'<Relop> -> {lop}'
                        self.tokens[tempcount+1]['productions'].append(new)
                        tempcount += 2
                        break
                    elif self.tokens[tempcount]['token'] in relops:
                        lop = self.tokens[tempcount]['token']
                        new = f'<Relop> -> {lop}'
                        self.tokens[tempcount]['productions'].append(new)
                        tempcount += 1
                        break
                    else:
                        try:
                            self.tokens[tempcount+1]['productions'] += self.Expression(tempcount+1)
                            self.Primary(tempcount+1)
                        except:
                            line = self.tokens[tempcount-1]['line']
                            print(f'Syntax error at line {line} (Invalid if (maybe missing separator))')
                            quit()
                        tempcount = self.globcount

                try:
                    self.tokens[tempcount]['productions'] += self.Expression(tempcount)
                    self.Primary(tempcount)
                    tempcount = self.globcount
                except:
                    line = self.tokens[tempcount-1]['line']
                    print(f'Syntax error at line {line} (Invalid print (maybe missing separator))')
                    quit()

                while True:
                    if self.tokens[tempcount]['token'] == ')':
                        break
                    else:
                        try:
                            self.tokens[tempcount+1]['productions'] += self.Expression(tempcount+1)
                            self.Primary(tempcount+1)
                        except:
                            line = self.tokens[tempcount-1]['line']
                            print(f'Syntax error at line {line} (Invalid if (maybe missing separator))')
                            quit()
                        tempcount = self.globcount
                tempcount += 1
                if self.tokens[tempcount]['token'] == '{':
                    try:
                        self.GetStateList(functionp,tempcount+1,'}')
                        tempcount = self.spoint
                    except:
                        line = self.tokens[tempcount-1]['line']
                        print(f'Syntax error at line {line} (Invalid compound (maybe missing end separator))')
                        quit()
                else:
                    try:
                        self.GetStateList(functionp,tempcount,'none')
                        tempcount = self.spoint - 1
                    except:
                        line = self.tokens[tempcount-1]['line']
                        print(f'Syntax error at line {line} (Invalid compound (maybe missing end separator))')
                        quit()


            #check for end character

            elif self.tokens[tempcount]['token'] == endchar:
                self.fpoint = count
                self.spoint = tempcount
                break
            else:
                line = self.tokens[tempcount+1]['line']
                print(f'Syntax error at line {line} (Invalid statement)')
                quit()
            tempcount += 1

        self.tokens[count]['productions'][len(self.tokens[count]['productions']) - 2] = '<Statement List> -> <Statement>'

    def Relop(self,count):
        if self.tokens[count]['token'] == '=' and self.tokens[count+1]['token'] == '=':
            new = '<Relop> -> =='
            self.tokens[count]['productions'].append(new)
            new = '<Relop> -> =='
            self.tokens[count+1]['productions'].append(new)
            count += 2
        elif self.tokens[count]['token'] == '!' and self.tokens[count+1]['token'] == '=':
            new = '<Relop> -> !='
            self.tokens[count]['productions'].append(new)
            new = '<Relop> -> !='
            self.tokens[count+1]['productions'].append(new)
            count += 2
        elif self.tokens[count]['token'] == '<' and self.tokens[count+1]['token'] == '=':
            new = '<Relop> -> <='
            self.tokens[count]['productions'].append(new)
            new = '<Relop> -> <='
            self.tokens[count+1]['productions'].append(new)
            count += 2
        elif self.tokens[count]['token'] == '=' and self.tokens[count+1]['token'] == '>':
            new = '<Relop> -> =>'
            self.tokens[count]['productions'].append(new)
            new = '<Relop> -> =>'
            self.tokens[count+1]['productions'].append(new)
            count += 2
        elif self.tokens[count]['token'] == '>':
            new = '<Relop> -> >'
            self.tokens[count]['productions'].append(new)
            count += 1
        elif self.tokens[count]['token'] == '<':
            new = '<Relop> -> <'
            self.tokens[count]['productions'].append(new)
            count += 1
        else:
            line = self.tokens[count]['line']
            print(f'Syntax error at line {line} (Invalid Relop)')
            quit()
        return count

    def Expression(self,count):
        productions = []
        tempcount = count + 1
        while True:
            if self.tokens[tempcount]['token'] == '+':
                new = '<Expression> -> <Expression> + <Factor>'
                productions.append(new)
                tempcount += 2
            elif self.tokens[tempcount]['token'] == '-':
                new = '<Expression> -> <Expression> - <Term>'
                productions.append(new)
                tempcount += 2
            else:
                new = '<Expression> -> <Term>'
                productions.append(new)
                pro = self.Primary(tempcount-1)
                if pro == []:
                    productions = []
                else:
                    productions = productions + self.Term(tempcount-1)
                break
        self.globcount = tempcount
        return(productions)

    def Term(self,count):
        productions = []
        tempcount = count + 1
        while True:
            if self.tokens[tempcount]['token'] == '*':
                new = '<Term> -> <Term> * <Factor>'
                productions.append(new)
                tempcount += 2
            elif self.tokens[tempcount]['token'] == '/':
                new = '<Term> -> <Term> / <Factor>'
                productions.append(new)
                tempcount += 2
            else:
                new = '<Term> -> <Factor>'
                productions.append(new)
                pro = self.Primary(tempcount-1)
                if pro == []:
                    productions = []
                else:
                    productions = productions + self.Primary(tempcount-1)
                break
        self.globcount = tempcount
        return(productions)

    def Primary(self,count):
        productions = []
        if self.tokens[count]['lexeme'] == 'identifier' and self.tokens[count+1]['token'] == '(':
            tempcount = count+3
            new = '<Factor> -> <Primary>'
            productions.append(new)
            new = '<Primary> -> <IDs>'
            productions.append(new)
            while True:
                new = '<IDs> -> <Identifier>'
                if new not in self.tokens[tempcount-1]['productions']:
                    self.tokens[tempcount-1]['productions'].append(new)
                if self.tokens[tempcount-1]['lexeme'] != 'identifier':
                    line = self.tokens[tempcount]['line']
                    print(f'Syntax error at line {line} (Identfier not found)')
                    quit()
                if self.tokens[tempcount]['token'] == ',' and self.tokens[tempcount+1]['lexeme'] == 'identifier':
                    new = '<IDs> -> <Identifier> , <IDs>'
                    productions.append(new)
                else:
                    new = '<IDs> -> <Identifier>'
                    productions.append(new)
                    if self.tokens[tempcount]['token'] != ')':
                        line = self.tokens[tempcount]['line']
                        print(f'Syntax error at line {line} (End separator not found)')
                        quit()
                    self.globcount = tempcount + 1
                    break
                tempcount += 2
        elif self.tokens[count]['token'] == 'true':
            new = '<Factor> -> <Primary>'
            productions.append(new)
            new = '<Primary> -> true'
            productions.append(new)
            self.globcount = count + 1
        elif self.tokens[count]['token'] == 'false':
            new = '<Factor> -> <Primary>'
            productions.append(new)
            new = '<Primary> -> false'
            productions.append(new)
            self.globcount = count + 1
        elif self.tokens[count]['lexeme'] == 'identifier':
            new = '<Factor> -> <Primary>'
            productions.append(new)
            new = '<Primary> -> <Identifier>'
            productions.append(new)
            self.globcount = count + 1
        elif self.tokens[count]['lexeme'] == 'int':
            new = '<Factor> -> <Primary>'
            productions.append(new)
            new = '<Primary> -> <Integer>'
            productions.append(new)
            self.globcount = count + 1
        elif self.tokens[count]['lexeme'] == 'real':
            new = '<Factor> -> <Primary>'
            productions.append(new)
            new = '<Primary> -> <Real>'
            productions.append(new)
            self.globcount = count + 1
        elif self.tokens[count]['token'] == '(':
            while True:
                if self.tokens[self.globcount]['token'] == ')':
                    self.globcount += 1
                    break
                try:
                    self.tokens[count+1]['productions'] = self.Expression(count+1)
                    self.Primary(count+1)
                    self.globcount = self.globcount
                    count = self.globcount
                except:
                    line = self.tokens[tempcount]['line']
                    print(f'Syntax error at line {line} (Invalid expresion)')
                    quit()
        else:
            line = self.tokens[count]['line']
            print(f'Syntax error at line {line} (Invalid Primary)')
            quit()
        return productions

    def parse(self):
        for item in self.tokens:
            item['productions'] = []
        count = 0
        count = self.GetOptFuncDef(count)
        new = '<Rat23F> -> <Opt Declaration List>'
        self.tokens[count]['productions'].append(new)
        count = self.GetOptDecList(count)
        functionpoint = 0
        for item in self.tokens:
            if item['token'] == '#':
                break
            functionpoint += 1
        if self.tokens[len(self.tokens) - 1]['token'] != '#' :
                line = self.tokens[len(self.tokens) - 1]['line']
                print(f'Syntax error at line {line} (Maybe missing # or Code outside of bounds)')
                quit()
        new = '<Rat23F> -> <Statement List>'
        self.tokens[functionpoint]['productions'].append(new)
        count = self.GetStateList(functionpoint,count,'#')
