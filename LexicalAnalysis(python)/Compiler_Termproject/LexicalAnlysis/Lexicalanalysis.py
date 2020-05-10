
import yaml
nextchar = ""
Numofline = 1
outputfile = open('test.out','w')

#Character 종류들을 dict형식으로 저장.
character = {
    "letter":["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"
    ,"A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"],
    "digit":["0","1","2","3","4","5","6","7","8","9"],
    "digitwnonzero":["1","2","3","4","5","6","7","8","9"],
    "zero":["0"],
    "white_space":[" ","\t", "\n"],
    "symbol":['+','-','/','*','!','(',')','{','}',',','=',";","<",">","==","!=","<=",">=",">>","<<","&","|","_","."]
}

#Keyword를 dict형식으로 저장.
keyword = {
    "INT":["int", "INT"], "CHAR":["char", "CHAR"],
    "TRUE":["TRUE","true"],"FALSE":["FALSE","false"],
    "IF":["if", "IF"], "ELSE":["else", "ELSE"], "WHILE":["while", "WHILE"], "FOR":["for","FOR"], "RETURN":["return", "RETURN"],
}

#DFA transition table
dfa_table = {
    #각 state에서 input값을 읽으면 정의한 token을 인식해 다른 state로 transition.
    "INT0":{"digitwnonzero":"INT2","digit":"INT4"},
    "INT1":{"digitwnonzero":"INT3"},
    "INT2":{"digit":"INT4"},
    "INT3":{"digit":"INT4"},
    "INT4":{"digit":"INT4"},
    "FLOAT0":{"zero":"FLOAT3","digit":"FLOAT2" },
    "FLOAT2":{"zero":"FLOAT2","digit":"FLOAT2",".":"FLOAT4" },
    "FLOAT3":{".":"FLOAT4"},
    "FLOAT4":{"zero":"FLOAT6" ,"digit":"FLOAT5"},
    "FLOAT5":{"digit":"FLOAT5","zero":"FLOAT6"},
    "FLOAT6":{"zero":"FLOAT6","digit":"FLOAT5"},
    "ID0":{"_":"ID1","letter":"ID2"},
    "ID1":{"_":"ID3","letter":"ID4","digit":"ID5"},
    "ID2":{"_":"ID3","letter":"ID4","digit":"ID5"},
    "ID3":{"_":"ID3","letter":"ID4","digit":"ID5"},
    "ID4":{"_":"ID3","letter":"ID4","digit":"ID5"},
    "ID5":{"_":"ID3","letter":"ID4","digit":"ID5"},
    "STRING":{"\"" : "STRING0"},
    "STRING0":{"\"":"STRING7","digit":"STRING1","letter":"STRING2","white_space":"STRING3"},
    "STRING1":{"\"":"STRING7","digit":"STRING4","letter":"STRING5","white_space":"STRING6"},
    "STRING2":{"\"":"STRING7","digit":"STRING4","letter":"STRING5","white_space":"STRING6"},
    "STRING3":{"\"":"STRING7","digit":"STRING4","letter":"STRING5","white_space":"STRING6"},
    "STRING4":{"\"":"STRING7","digit":"STRING4","letter":"STRING5","white_space":"STRING6"},
    "STRING5":{"\"":"STRING7","digit":"STRING4","letter":"STRING5","white_space":"STRING6"},
    "STRING6":{"\"":"STRING7","digit":"STRING4","letter":"STRING5","white_space":"STRING6"},
}


#DFA 정의한 class.
class DFA:
    def __init__(self,s):
        self.MakeState(s)    
    def MakeState(self,s):
        self.state = s
    #dfa_table에 state가 존재하고 그 state에서 a의 타입을 받는다면 accept한다는 의미인 True를 반환.
    #reject한다면 False 반환.
    def Accept(self, a):
        if self.state in dfa_table: 
            if getType(a) in dfa_table[self.state]:
                return True
        return False

    #DFA transition
    #transition을 하는 기능.
    def transition(self,a):
        self.state = dfa_table[self.state][getType(a)]

#Error class
class inputerror(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return self.value

#현재 문자를 nowchar에 넣고 다음 문자를 global변수인 nextchar에 초기화 한 후 현재 문자 반환
def getChar():
    global nextchar
    nowchar = nextchar
    nextchar = text.read(1)
    return nowchar
    
#a의 type 정해주기
def getType(a):
    if a in character['letter']:
        return "letter"
    if a in character['digit']:
        return "digit"
    if a in character['digitwnonzero']:
        return "digitwnonzero"
    if a in character['white_space']:
        return "white_space"
    if a in character['symbol']:
        return a
    if not a:
        return ''
    #어떠한 type에도 속하지 않으면 오류 발생.
    raise inputerror("invaild character " + a)



#ID, String, Int, Float DFA 진행
def Id(a):
    global nextchar
    value = a 
    state = DFA("ID0") #ID0 STATE 생성
    while True:
        if(state.Accept(nextchar)): #Accept 할 경우
            a = getChar()
            state.transition(a) #다음 state 진행 
            value += a #이어붙이기
        else: #Reject 할 경우
            break 

    #keyword들의 key값이 INT,FLOAT,CHAR일 경우 변수로 묶고, TRUE,FALSE일 경우 불리안변수로 묶는다.
    for key in list(keyword.keys()):
        if value in keyword[key] : 
            if key == 'INT' or key == 'CHAR' or key =='FLOAT' :
                return {'TokenName': 'VariableType', 'value':value}
            elif key =='TRUE' or key =='FALSE':
                return {'TokenName': 'BooleanType', 'value':value}
            return {'TokenName': key.upper(), 'value':value}  
    return {'TokenName':'ID', 'value':value}

def string(a):
    global nextchar
    value = a
    state = DFA("STRING")
    while True:
        if(state.Accept(nextchar)):
            a = getChar()
            state.transition(a)
            value += a
        else:
            if a != '\"':
                raise inputerror(str(a))
            break
    return {'TokenName':'LITERAL', 'value':value}

def integertoken(a):
    global nextchar
    value = a
    state = DFA("INT0")
    #nextchar에서 .이 나올경우 inttofloat를 통해 floattoken으로 변경
    if(nextchar == '.'):
        return floattoken(a)
    while True:
        if(state.Accept(nextchar)):
            a = getChar()
            state.transition(a)
            prevalue = value
            value += a
            if(nextchar == '.'):
                return inttofloat(a,prevalue)
        else:
            if(nextchar in character['letter']):
                raise inputerror(str(a))
            break
    return {"TokenName":"INT", "value":value}

def floattoken(a):
    global nextchar
    value = a
    state = DFA("FLOAT0")
    state.transition(a)
    while True:
        if(state.Accept(nextchar)):
            a = getChar()
            state.transition(a)
            value += str(a)
        else:
            if(nextchar in character['letter']):
                raise inputerror(str(a))
            break
    return {'TokenName':'FLOAT', 'value':value}

def inttofloat(a,prevalue):
    global nextchar
    value = prevalue + a
    state = DFA("FLOAT4")
    state.transition(a)
    while True:
        if(state.Accept(nextchar)):
            a = getChar()
            state.transition(a)
            value += str(a)
        else:
            if(nextchar in character['letter']):
                raise inputerror(str(a))
            elif(nextchar == '.'):
                raise inputerror(str(a))
            break
    return {'TokenName':'FLOAT', 'value':value}    

#위의 함수를 이용해 현재 문자의 DFA를 만들고 토큰 정보를 가져와 입력 문자의 토큰을 반환.
def tokeninfor():
    global nextchar, Numofline
    try:
        #빈칸 제거
        a = getChar()
        while(a in character['white_space']):
            if a == '\n':
                Numofline = Numofline + 1
            a = getChar()
        #EOF
        if not a:
            return {'TokenName':"EOF",'value':''}

        if a in character['letter']:
            token = Id(a)

        elif a in character['digitwnonzero']:
            token = integertoken(a)

        elif a =='0' :
            if(nextchar == '.'):
                token = floattoken(a)
            else:
                token = integertoken(a)        

        elif a == "\"":
            token = string(a)

        elif a == '(':
            token = {'TokenName':'LPAREN','value':'('}

        elif a == ')':
            token = {'TokenName':'RPAREN','value':')'}

        elif a == '{':
            token = {'TokenName':'LBRACE','value':'{'}

        elif a == '}':
            token = {'TokenName':'RBRACE','value':'}'}

        elif a == '+':
            token = {'TokenName':'ADD','value':'+'}

        elif a == '-':
            token = {'TokenName':'SUB','value':'-'}

        elif a == '*':
            token = {'TokenName':'MUL','value':'*'}

        elif a == '/':
            token = {'TokenName':'DIV','value':'/'}

        elif a == ';':
            token = {'TokenName':'SEMI','value':';'}

        elif a == '&':
            token = {'TokenName':'BITAND','value':'&'}

        elif a == '|':
            token = {'TokenName':'BITOR','value':'|'}

        elif a == ',':
            token = {'TokenName':'COMMA','value':','}

        elif a == '=':
            if nextchar == '=':
                a = getChar()
                token = {'TokenName':'EQUAL', 'value':'=='} # ==
            else:
                token = {'TokenName':'ASSIGN', 'value':'='}

        elif a == '>':
            if nextchar == "=":
                a = getChar()
                token = {'TokenName':'GREATEREQUAL', 'value':'>='} # >=]
            elif nextchar == ">":
                token = {'TokenName':'LEFTSHIFT', 'value':'>>'}
            else:
                token = {'TokenName':'GREATER', 'value':'>'} 

        elif a == '<':
            if nextchar == "=":
                a = getChar()
                token = {'TokenName':'LESSEQUAL', 'value':'<='} # <=
            elif nextchar == ">":
                token = {'TokenName':'RIGHTSHIFT', 'value':'<<'}    
            else:
                token = {'TokenName':'LESS','value':'<'}
        elif a == '!':
            if nextchar == "=":
                a = getChar()
                token = {'TokenName':"NOTEQUAL", 'value':'!='} # !=
            else:   
                raise inputerror('ERROR - Invalid symbol : !')
        else:
            raise inputerror(str(a))
        return token
    except inputerror as e:
        #오류가 생길경우 outputfile에 오류 발견된 문자와 오류가 발생하는 input파일의 위치를 알려준다.
        outputfile.write("Error value at : " + e.value + "\nError line of input : " + str(Numofline))

#파일을 읽는 어휘분석함수.
def Lexicalanalysis(inputfilename):
    global Numofline,text,nextchar
    Numofline = 1
    text = open(inputfilename)
    nextchar = text.read(1)
    #tokenname과 value값의 dict형식을 symboltable에 리스트로 저장한다.
    symboltable = []
    
    minusflag = False
    try:
        while True:
            token = tokeninfor() # token의 dict형식 {'TokenName(key)': , 'value': }
            print(token)
            #operator '-'와 minus의 '-'를 구분하기 위한 if문.
            if minusflag:
                minusflag = False
                #minus의 '-'일 경우 value앞에 -를 붙인다.
                token['value'] = '-' + token['value']
            if token['TokenName'] == 'EOF':
                break
            if token['value'] == '-':
                if not symboltable:
                    minusflag =True
                else :
                    previous = symboltable[len(symboltable)-1]
                    #-앞의 token이 int나 float가 있다면 operator의 "-" 로 생각.
                    if previous['TokenName'] != ('INT' or 'FLOAT'):
                        minusflag = True
                    else:
                        symboltable.append(token)
            else:
                symboltable.append(token)
        symboltable.append({'TokenName':'EOF','value':'EOF'} )
        return symboltable
    except : # 에러가 발생한 줄번호 
        print("Error LineNumber :  " + str(Numofline)) # 에러가 발생한 줄번호
        exit()

#symbol table 파일에 저장.
if __name__== "__main__":
    symbol = Lexicalanalysis('test.c')

    outputfile = open('test.out','w')
    #yaml.dump의 정렬형식을 사용해서 입력.
    #사용하기 위해서는 cmd에서 pip install pyymal을 쳐서 다운받아야한다.
    outputfile.write(yaml.dump(symbol))
    outputfile.close()

