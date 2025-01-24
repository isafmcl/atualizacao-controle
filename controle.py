from flask import Flask, request, jsonify
import pywhatkit as kit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_cors import CORS
import datetime
import os

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500"])  # vai permitir p mim apenas o dom c o front

analistas = {
    "Gerson": "+556185672288",
    "Victor": "+556198637534",
    "Estevam": "+556191833889",
    "Augusto": "+556185849179",
    "Gladystone": "+556192484268"
}


def enviar_whatsapp(numero, mensagem):
    try:
        kit.sendwhatmsg(numero, mensagem, 22, 38)  
        return "Mensagem enviada com sucesso!"
    except Exception as e:
        return f"Erro ao enviar mensagem: {e}"


def enviar_email():
    from_email = os.getenv('EMAIL_USER')  
    to_email = os.getenv('EMAIL_TO') 
    senha = os.getenv('EMAIL_PASSWORD')  

    
    agora = datetime.datetime.now()
    assunto = f"Resumo Diário - {agora.strftime('%d/%m/%Y')}"
    corpo_email = """
    Olá, boa tarde

    Esse é o resumo diário dos chamados pendentes:

    - Gerson: 3 chamados pendentes
    - Victor: 1 chamado pendente
    - Estevam: 5 chamados pendentes
    - Augusto: 2 chamados pendentes
    - Gladystone: 4 chamados pendentes

    Atenciosamente,
    Isabelle
    """

    # Configuração do e-mail
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo_email, 'plain'))

    try:
        # Conectar ao meu gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  
        server.login(from_email, senha)  
        server.sendmail(from_email, to_email, msg.as_string())  # Envia o email
        server.quit()  

        return "E-mail enviado com sucesso!"
    except Exception as e:
        return f"Erro ao enviar e-mail: {e}"

@app.route('/enviar_whatsapp', methods=['POST'])
def rota_whatsapp():
    analista = request.json['analista']
    mensagem = request.json['mensagem']
    numero = analistas.get(analista)

    if numero:
        resultado = enviar_whatsapp(numero, mensagem)
        return jsonify({"mensagem": resultado})
    else:
        return jsonify({"mensagem": "Analista não encontrado."}), 404

@app.route('/enviar_email', methods=['POST'])
def rota_email():
    resultado = enviar_email()
    return jsonify({"mensagem": resultado})

if __name__ == '__main__':
    app.run(debug=True)
