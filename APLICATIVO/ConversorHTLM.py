import pyperclip

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


string = """
<!DOCTYPE html>
<html lang='pt-br'>
<head>
    <meta charset='UTF-8'>
    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Site Semáforo</title>

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
            height: 50px;
            width:  200px;
        }
        .alinhado{
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
            <p class='alinhado' style='font-size: 20pt;'>&#128267;</p>           
            <p class='alinhado'>Nível da Bateria:</p>
            <p class='alinhado'id='NivelBateria' class='emoji' style='color: blue;'>100%</p>

            <p class='alinhado' style='font-size: 22pt; margin-left: 70px;'>&#128678;</p>
            <p class='alinhado'>Estado do Semáforo: </p>
            <p class='alinhado'id ='EstadoSemaforo' class='emoji' style='color: red;'>VERMELHO</p>
        </div>

        <div id='botoes'>
            <input class='botoes' type='button' value='LIBERAR PASSAGEM' id='btnLigar' onclick='ativar()'>
            <input class='botoes' type='button' value='BARRAR PASSAGEM' id='btnDesligar' onclick='desativar()'>
        </div>

        <div class='info' style='text-align: center; margin-bottom: 30px;'>
            <p class='alinhado' style='font-size: 20pt;'>&#128214;</p>          
            <p class='alinhado'>Informações</p> 

            <p style='margin-bottom: -40px;'></p>

            <div class='alinhado' style='text-align: left; margin-right: 50px;'>
                <p class='alinhado'>Tempo Vermelhos: </p>
                <p class='alinhado' id='tempoVermelhos'>10 segundos</p>
                
                <p style='margin-top: -40px;'></p>
    
                <p class='alinhado'>Tempo Resto: </p>
                <p class='alinhado' id='tempoResto'>10 segundos</p>
            </div>

            <div class='alinhado' style='text-align: left;'>
                <p class='alinhado'>Modo Sinal: </p>
                <p class='alinhado' id='modo'>SÍNCRONO</p>
                
                <p style='margin-top: -40px;'></p>
    
                <p class='alinhado'>Estado: </p>
                <p class='alinhado' id='func'>FUNCIONANDO</p>
            </div>
        </div>
    </section>

    <footer>
        <p> &copy; Projeto Semáforo </p>
    </footer>
    
    <script>
        function validarUsuario(usuario, senha){
            let user = window.prompt('digite o usuário: ')
            let password = window.prompt('digite a senha: ')

            if(user != usuario || password != senha){
                window.alert('usuário ou senha inválidos...')
                validarUsuario()
            }
        }


        function validarEstado(estadoSemaforo){
            txt = document.getElementById('EstadoSemaforo')

            if(estadoSemaforo){
                txt.innerHTML = 'VERMELHO'
                txt.style.color = 'red'
                return true
            }
            
            txt.innerHTML = 'NÃO VERMELHO'
            txt.style.color = 'blue'
            return false
        }


        function validarBateria(nivelBateria){
            txt = document.getElementById('NivelBateria')
            txt.innerHTML = nivelBateria + '%'
        }
        

        function validarTempos(tempoVermelhos, tempoResto){
            txt1 = document.getElementById('tempoVermelhos')
            txt2 = document.getElementById('tempoResto')

            txt1.innerText = tempoVermelhos/1000 + ' segundos'
            txt2.innerText = tempoResto/1000 + ' segundos'
        }

        
        function validarModo(modo){
            txt = document.getElementById('modo')
            
            if(modo){
                txt.innerHTML = 'SÍNCRONO'
                txt.style.color = 'blue'
                return true
            }

            txt.innerHTML = 'DETECTANDO'
            txt.style.color = 'red'
            return false
        }


        function validarFuncionamento(funcionamento){
            txt = document.getElementById('func')

            if(funcionamento){
                txt.innerHTML = 'NORMAL'
                txt.style.color = 'blue'
                return true
            }

            txt.innerHTML = 'FALHA'
            txt.style.color = 'red'
            return false
        }


        function ativar(){
            fetch('http://192.168.4.1/ATIVAR')
            fetch('http://192.168.4.3/ATIVAR')
        }


        function desativar(){
            fetch('http://192.168.4.1/DESATIVAR')
            fetch('http://192.168.4.3/DESATIVAR')
        }


        validarUsuario('projeto', 'semaforo')
        validarEstado(0)
        validarBateria(50)
        validarTempos(10500, 15080)
        validarModo(0)
        validarFuncionamento(0)
    </script>
</body>
</html>
"""

string = formatar(string)