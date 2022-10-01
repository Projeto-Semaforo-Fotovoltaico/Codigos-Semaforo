import pyperclip
import codecs


def formatar(string):
    formatado = ''

    for linha in string.split('\n'):
        temp = '\t' + '(*cl).println("' + linha.strip() + '");'  + '\n'
        if '(*cl).println("")' not in temp:
            formatado += temp
    
    print()
    print(formatado)
    pyperclip.copy(formatado)
    return formatado


f=codecs.open("ProjetoSemaforo.html", 'r', 'utf-8')
string = f.read()
string = formatar(string)