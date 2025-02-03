from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
import pywhatkit as kit
import datetime
from flask_cors import CORS
from datetime import datetime
import pandas as pd
from flask import Flask, render_template
import requests
import openpyxl
import time
app = Flask(__name__)
CORS(app)




# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "isabelle.oliveira@atacadaodiaadia.com.br"
app.config['MAIL_PASSWORD'] = "dcks hcqd jxct pngv"
mail = Mail(app)


# Função para ler o relatório Excel
def ler_relatorio_excel(caminho_arquivo):
    try:
        # Lê o arquivo Excel
        df = pd.read_excel(caminho_arquivo)

        # Converter a coluna Abertura para datetime
        if 'Abertura' in df.columns:
            df['Abertura'] = pd.to_datetime(df['Abertura'], errors='coerce')

        # Garantir que valores inválidos sejam tratados
        df['Abertura'] = df['Abertura'].fillna(pd.Timestamp('1970-01-01'))

        # Formatar novamente como string eh opcional 
        df['Abertura'] = df['Abertura'].dt.strftime('%d/%m/%Y %H:%M')




        



        return df
    except Exception as e:
        print(f"Erro ao ler o arquivo Excel: {e}")
        return None



# Simulação de dados que vao ser extraidos do excel 
dados = [
    {"Código": "B2M000161220", "Abertura": "13/1/2025 09:41"},
    {"Código": "B2M000161769", "Abertura": "17/1/2025 13:45"},
    {"Código": "B2M000162599", "Abertura": "27/1/2025 14:39"},
    {"Código": "B2M000162786", "Abertura": "28/1/2025 18:17"},
    {"Código": "CDJK00161777", "Abertura": "17/1/2025 14:38"},
    {"Código": "B2M000162844", "Abertura": "29/1/2025 10:04"},
]

# Converter dados para data, pois esta dando erro pq contem numereros na tabela 
df = pd.DataFrame(dados)

# Converter a coluna "Abertura" para formato de data
df["Abertura"] = pd.to_datetime(df["Abertura"], format="%d/%m/%Y %H:%M")

# Definir a data atual (substitua por datetime.now() para uso real)
data_atual = datetime(2025, 1, 29)  # Simulando a data de hoje

# Calcular diferença em dias
df["Dias Abertos"] = (data_atual - df["Abertura"]).dt.days

# Filtrar chamados que estao abertos a mais de 3 dias 
chamados_pendentes = df[df["Dias Abertos"] > 3]

# Exibir resultado
print(chamados_pendentes)


# Função para extrair dados dos chamados
def extrair_dados_chamados(df):
    chamados = {}
    for index, row in df.iterrows():
        try:
            analista = row['Responsável']
            total = chamados.get(analista, {'total': 0, 'pendentes': 0 })  # Inicializa se não existir
 
            total['total'] += 1  # Incrementa o total de chamados
            pendentes = row.get('SLAcham.', 0)
            print(pendentes)
           
            
            total['pendentes'] += pendentes  # Vai fazer a soma dos chamados pendentes 
            chamados[analista] = total
        except Exception as e:
            print('Este é o erro:',e)
    print('Esse é o chamados',chamados)

    
    return chamados



@app.route('/atualizar_chamados', methods=['GET'])
def atualizar_chamados():
    caminho_arquivo = r'C:\Users\isabelle.oliveira\Downloads\RelatorioChamados.xlsx'
    df = ler_relatorio_excel(caminho_arquivo)
    if df is not None:
        chamados = extrair_dados_chamados(df)
        return jsonify({"mensagem": "Dados atualizados com sucesso!", "dados": chamados})
    else:
        return jsonify({"mensagem": "Erro ao atualizar os dados."}), 500

analistas = {
    "Gerson": "+556185672288",
    "Victor": "+556198637534",
    "Estevam": "+556191833889",
    "Augusto": "+556185849179",
    "ellick": "+556199063627",
}

def enviar_whatsapp(numero, mensagem):
    try:
        kit.sendwhatmsg_instantly(numero, mensagem, wait_time=20)
        return "Mensagem enviada com sucesso!"
    except Exception as e:
        return f"Erro ao enviar mensagem: {e}"

def enviar_email(to_email):
    from_email = app.config['MAIL_USERNAME']
    agora = datetime.datetime.now()
    assunto = f"Resumo Diário dos Chamados Pendentes - {agora.strftime('%d/%m/%Y')}"
    corpo_email = """
   Olá, boa tarde,

   Segue o resumo diário dos chamados pendentes:

   Chamados na fila de atendimento: 
   Chamados com SLA estourado: 
   Chamados abertos há mais de 3 dias: 
   Quantidade por Analista x Status:

   Em espera: 
   Respondido pelo usuário: 
   Pendente de resposta do usuário: 
   Atenciosamente,
   Isabelle
      """

    msg = Message(subject=assunto, sender=from_email, recipients=[to_email])
    msg.body = corpo_email

    try:
        mail.send(msg)
        return "E-mail enviado com sucesso!"
    except Exception as e:
        return f"Erro ao enviar e-mail: {e}"

@app.route('/enviar_whatsapp', methods=['POST'])
def rota_whatsapp():
    try:
        analistas_selecionados = request.json.get('analistas', [])
        chamados = request.json.get('chamados', {})

        if not analistas_selecionados:
            return jsonify({"mensagem": "Nenhum analista selecionado"}), 400

        resultados = []

        for analista in analistas_selecionados:
            numero = analistas.get(analista)
            if numero:
                mensagem = f"Olá {analista}, você tem chamados pendentes! Por favor, verifique o sistema."
                resultado = enviar_whatsapp(numero, mensagem)
                resultados.append(f"Mensagem para {analista}: {resultado}")
            else:
                resultados.append(f"Analista {analista} não encontrado.")

        return jsonify({"mensagem": "Mensagens enviadas com sucesso!", "resultados": resultados})
    except Exception as e:
        return jsonify({"mensagem": f"Erro na requisição: {e}"}), 500

@app.route('/enviar_email', methods=['POST'])
def rota_email():
    to_email = "ellick.barreto@atacadaodiaadia.com.br/raionny.fernandes@atacadaodiaadia.com.br"
    resultado = enviar_email(to_email)
    return jsonify({"mensagem": resultado})

if __name__ == '__main__':
    app.run(debug=True)


