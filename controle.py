from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
import pywhatkit as kit
import datetime
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500"])

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
        df = pd.read_excel(caminho_arquivo)
        return df
    except Exception as e:
        print(f"Erro ao ler o arquivo Excel: {e}")
        return None

# Função para extrair dados dos chamados
def extrair_dados_chamados(df):
    chamados = {}
    for index, row in df.iterrows():
        analista = row['Analista']
        total = row['Total Chamados']
        pendentes = row['Pendentes']
        chamados[analista] = {'total': total, 'pendentes': pendentes}
    return chamados

@app.route('/atualizar_chamados', methods=['POST'])
def atualizar_chamados():
    caminho_arquivo = r'C:\Users\isabe\OneDrive\Área de Trabalho\relatorio_chamados.xlsx'
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
    "Gladystone": "+556192484268"
}

def enviar_whatsapp(numero, mensagem):
    try:
        kit.sendwhatmsg_instantly(numero, mensagem, wait_time=10)
        return "Mensagem enviada com sucesso!"
    except Exception as e:
        return f"Erro ao enviar mensagem: {e}"

def enviar_email(to_email):
    from_email = app.config['MAIL_USERNAME']
    agora = datetime.datetime.now()
    assunto = f"Resumo Diário - {agora.strftime('%d/%m/%Y')}"
    corpo_email = """
    Olá, boa tarde,

    Este é o resumo diário dos chamados pendentes.

    Atenciosamente, Isabelle.
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
    to_email = "ellick.barreto@atacadaodiaadia.com.br"
    resultado = enviar_email(to_email)
    return jsonify({"mensagem": resultado})

if __name__ == '__main__':
    app.run(debug=True)


