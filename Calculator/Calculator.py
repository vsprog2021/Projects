import math
import sys

def prioritate(c):
    if c in "()":
        return 0
    if c in "-+":
        return 1
    if c in "*/":
        return 2
    if c in '^':
        return 3
    if c == 'r':
        return 4
    if c == 'n':
        return 5

def negative(x):
    return 0 - x

def putere(x, y):
    if x == y == 0:
        return "eroare"
    if x == 0:
        return 0
    if y == 0:
        return 1
    if y < 0:
        return 1 / x ** negative(y)
    return x ** y
    # return pow(x,y)

def plus(x, y):
    return x + y

def minus(x, y):
    return x - y

def inmultire(x, y):
    return x * y

def impartire(x, y):
    if y == 0:
        return "eroare"
    return x / y

def modul(x):
    if x < 0:
        return x * -1
    return x

def radical(x):
    if x < 0:
        return "eroare"
    return math.sqrt(x)

def verif(sir):
    pd = sir.count('(')
    pi = sir.count(')')
    if pi != pd:
        return False
    
    paranteze = []
    for chr in sir:
        if chr == '(':
            paranteze.append(chr)
        elif chr == ')':
            if not paranteze:
                return False
            paranteze.pop()

    if len(paranteze) != 0:
        return False    

    return True
        
def verifsintx(sir):
    i = 0
    while i < len(sir):
        if sir[i] == '(':
            if i >= len(sir) - 4 and len(sir) - 4 > 0:
                return False
            if sir[i + 1] == ')' or sir[i + 1] in "+-*/.":
                return False
            
        elif sir[i] == ')':
            if i < 3:
                return False
            if (i!= len(sir) - 1) and sir[i + 1] not in "*+/-^.)":
                return False
        
        elif sir[i] in "+-/*^":
            if i == 0 or i == len(sir) - 1:
                return False
            if sir[i + 1].isdigit() == False and sir[i + 1] not in "()rn" and sir[i + 1] in "+-/^*":
                return False
        
        elif sir[i].isdigit():
            if i != len(sir) - 1 and sir[i + 1].isdigit() == False and sir[i + 1] not in "+-/*^.)":
                return False

        elif sir[i] == '.':
            if i == 0 or i == len(sir) - 1:
                return False
            if sir[i - 1].isdigit() == False:
                return False
            j = i + 1
            while j < len(sir)-1 and sir[j].isdigit():
                j += 1
            if sir[j] == '.':
                return False
            
        elif sir[i] in "rn":
            if sir[i + 1].isdigit() == False and sir[i + 1] in ".+/-*)" and sir[i + 1] not in "rn(":
                return False
        else:
            return False
        
        i += 1
    return True

def calcul(operatori, operanzi):
    op = operatori.pop()
    rezultat = 0
    if op == 'r':
        x = operanzi.pop()
        rezultat = radical(x)
    elif op == 'n':
        x = operanzi.pop()
        rezultat = negative(x)
    else:
        y = operanzi.pop()
        x = operanzi.pop()
        if op == '+':
            rezultat = plus(x, y)
        elif op == '-':
            rezultat = minus(x, y)
        elif op == '*':
            rezultat = inmultire(x, y)
        elif op == '/':
            rezultat = impartire(x, y)
        elif op == '^':
            rezultat = putere(x, y)
    
    return rezultat

def valoare(ssir):
    operanzi = []
    operatori = []
    sir = ssir.replace(" ","")
    if len(sir) < 2:
        return "eroare len"
    if verif(sir) == False:
        return "eroare verif"
    if verifsintx(sir) == False:
        return "eroare sintx"
    print("Functia de calculat: " + sir)

    i = 0
    while i < len(sir):
        if sir[i].isdigit():
            numar = ""
            while i < len(sir) and (sir[i].isdigit() or sir[i] == '.'):
                numar += sir[i]
                i += 1
            operanzi.append(float(numar))
        elif sir[i] in "-+*/^nr":
            while (operatori and operanzi and prioritate(sir[i]) <= prioritate(operatori[-1])):
                rezultat = calcul(operatori, operanzi)
                if rezultat == "eroare":
                    return "eroare"
                operanzi.append(rezultat)
            operatori.append(sir[i])
            i += 1
        elif sir[i] == '(':
            operatori.append(sir[i])
            i += 1
        elif sir[i] == ')':
            while operatori and operatori[-1] != '(':
                rezultat = calcul(operatori, operanzi)
                if rezultat == "eroare":
                    return "eroare"
                operanzi.append(rezultat)
            operatori.pop()
            i += 1
    
    #print(operatori)
    #print(operanzi)

    while operatori:
        rezultat = calcul(operatori, operanzi)
        operanzi.append(rezultat)

    return operanzi[0]

def main(value):
    presetare1 = "20^(5-2)-(7000+999)"
    presetare2 = "2 + 3 * (4 - 1) ^ 2"
    presetare3 = "(12 * 3 + 4) * 2"
    presetare4 = "(5 + 2) * (3 - 1) ^ 2"
    presetare5 = "2 * (3 + 4 * (2 - 1)) + r25"
    presetare6 = "n5 * (2 + 3) - r16"
    presetare7 = "1 + 2 * (3 + 4 * (5 + 1)) / 2 - 1"
    presetare8 = "2 * (r9 - 3) + 4"
    presetare9 = "1 + 2^3 * 4 - r81"

    if value == "presetare1":
        sir = presetare1
    elif value == "presetare2":
        sir = presetare2
    elif value == "presetare3":
        sir = presetare3
    elif value == "presetare4":
        sir = presetare4
    elif value == "presetare5":
        sir = presetare5
    elif value == "presetare6":
        sir = presetare6
    elif value == "presetare7":
        sir = presetare7
    elif value == "presetare8":
        sir = presetare8
    elif value == "presetare9":
        sir = presetare9
    else:
        sir = str(value)

    rezultat = valoare(sir)
    print("Rezultatul: ", rezultat)


def main1():
    print("Ati apelat comanda help, aici sunt toate instructinile: ")
    print("x+y; x-y; x*y; x/y; x^y; rx -> radical x; nx -> negativ x.")
    print("Exista si exemple deja presetate. Folositi \"presetare i\", 0<i<10, fara spatiu.")

def main2():
    while(1):
        value = input("Scrieti functia: ")
        if value.lower() == "stop":
            break
        if value.lower() == "help":
            main1()
        else:
            main(value)
        print("")

main2()