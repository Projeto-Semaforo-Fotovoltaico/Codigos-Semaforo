import pyperclip

def formatar(string):
    formatado = ''

    for linha in string.split('\n'):
        temp = '\t' + 'txtHTML += "' + linha.strip() + '";'  + '\n'
        if 'txtHTML += ""' not in temp:
            formatado += temp
    
    print()
    print(formatado)
    pyperclip.copy(formatado)
    return formatado


string = """
<!DOCTYPE html>
<html lang='pt-br'>
<head>
    <meta charset='UTF-8'>
    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Exercício 3</title>

    <style>
        body{
            background-color: skyblue;
            font: normal 15pt Arial;
            text-align: center;
        }
        header{
            text-align: center;
            font: bold 18pt Arial;
            padding: 20px;

            width: 400px;
            height: 40px;
            line-height: 40px;
            margin: auto;

            color: black;
            background-color: yellow;
            border: 1px solid black;
            border-radius: 10px;
        }
        section{
            text-align: center;
            margin: auto;

            width: 750px;
            margin-top: 20px;
            padding: 20px;
            background-color: white;

            border: 1px solid black;
            border-radius: 10px;
        }
        footer{
            text-align: center;
            color: white;
            font: italic;
        }
        div{
            text-align: left;
            margin-bottom: -50px;
        }
        div#botoes{
            text-align: center;
        }
        input.botoes{
            margin: 50px;
            height:50px;
            width:200px;
        }
        p.emoji{
            display: inline-block;
        }
    </style>
</head>
<body>
    <header>
        SEMÁFORO PARA PEDESTRES
    </header>
    
    <section>
        <div class='info'>
            <p class='emoji' style='font-size: 20pt;'>&#128267;</p>           
            <p class='emoji'>Nível da Bateria:</p>
            <p class='emoji' style='color: blue;'>100%</p>


            <p class='emoji' style='font-size: 22pt; margin-left: 100px;'>&#128678;</p>
            <p class='emoji'>Estado do Semáforo: </p>
            <p class='emoji' style='color: red;'>VERMELHO</p>
        </div>

        <div id='botoes'>
            <input class='botoes' type='button' value='LIBERAR PASSAGEM' id='btnLigar' onclick='ativar()'>
            <input class='botoes' type='button' value='BARRAR PASSAGEM' id='btnDesligar' onclick='desativar()'>
        </div>

        <div class='info' style='text-align: center; margin-bottom: -45px;'>
            <p class='emoji' style='font-size: 20pt;'>&#128214;</p>          
            Histórico
        </div>
        <div id='historico' style='text-align: center; padding: 30px;'>
            <select name='lista' id='lisaHistorico' size='20' 
                style='width: 250px;  height: 200px; border: 1px solid black; margin-bottom: 40px;'>
                <option>DETECTADO</option>
                <option>NÃO DETECTADO</option>
                <option>DETECTADO</option>
                <option>NÃO DETECTADO</option>
                <option>DETECTADO</option>
                <option>NÃO DETECTADO</option>
                <option>DETECTADO</option>
                <option>NÃO DETECTADO</option>
                <option>DETECTADO</option>
                <option>NÃO DETECTADO</option>
                <option>DETECTADO</option>
                <option>NÃO DETECTADO</option>
                <option>DETECTADO</option>
                <option>NÃO DETECTADO</option>
                <option>DETECTADO</option>
                <option>NÃO DETECTADO</option>
                <option>DETECTADO</option>
                <option>NÃO DETECTADO</option>
                <option>DETECTADO</option>
                <option>NÃO DETECTADO</option>
            </select>
        </div>
    </section>

    <footer>
        <p> &copy; Projeto Semáforo </p>
    </footer>
    
    <script>
        function validar(){
            let user = window.prompt('digite o usuário: ')
            let password = window.prompt('digite a senha: ')

            if(user != 'projeto' || password != 'semaforo'){
                window.alert('usuário ou senha inválidos...')
                validar()
            }
                
        }

        function ativar(){
            fetch('http://192.168.4.1/ATIVAR')
            fetch('http://192.168.4.3/ATIVAR')
        }

        function desativar(){
            fetch('http://192.168.4.1/DESATIVAR')
            fetch('http://192.168.4.3/DESATIVAR')
        }

        validar()
    </script>
</body>
</html>
"""

string = formatar(string)