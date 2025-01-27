from flask import Flask, request, jsonify
import pywhatkit as kit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_cors import CORS
import datetime
import os
import schedule
import time


from flask_cors import CORS
app = Flask(__name__)
CORS(app)


analistas = {
    "Gerson": "+556185672288",
    "Victor": "+556198637534",
    "Estevam": "+556191833889",
    "Augusto": "+556185849179",
    "Gladystone": "+556192484268"
}



def enviar_whatsapp(numero, mensagem):
    try:
        kit.sendwhatmsg_instantly(numero, mensagem, wait_time=10)  # Envia na hora
        return "Mensagem enviada com sucesso!"
    except Exception as e:
        return f"Erro ao enviar mensagem: {e}"

def enviar_mensagens_para_analistas(analistas_selecionados, chamados):
    resultados = []

    for analista in analistas_selecionados:
        numero = analistas.get(analista)

        if not numero:
            resultados.append(f"Analista {analista} não encontrado.")
            continue

        total = chamados.get(analista, {}).get('total', 0)
        pendentes = chamados.get(analista, {}).get('pendentes', 0)
        sla_estourado = 'Sim' if pendentes > 3 else 'Não'

        mensagem = (
            f"Olá {analista},\n\n"
            f"Você tem {total} chamados no total, e {pendentes} chamados pendentes.\n"
            f"SLA Estourado: {sla_estourado}\nPor favor, tome as ações necessárias.\n\nAtenciosamente," 
        )

        resultado = enviar_whatsapp(numero, mensagem)
        resultados.append(f"Mensagem para {analista}: {resultado}")

    return resultados
#informacoes pedidas pelo raoinny

def enviar_email():
    from_email = "isabelle.oliveira@atacadaodiaadia.com.br"  
    to_email = ["ellick.barreto@atacadaodiaadia.com.br"]  
    senha = os.getenv('Isinha009@estudante')  # A senha foi tirada da variavel de ambiente 
    agora = datetime.datetime.now()
    assunto = f"Resumo Diário - {agora.strftime('%d/%m/%Y')}"



    fila_atendimento = {
        "Gerson": 6,
        "Victor": 1,
        "Estevam": 2,
        "Augusto": 3,
        "Gladystone": 0
    }

    sla_estourados = {
        "Gerson": 1,
        "Victor": 0,
        "Estevam": 0,
        "Augusto": 0,
        "Gladystone": 0
    }

    abertos_mais_3_dias = {
        "Gerson": 2,
        "Victor": 1,
        "Estevam": 1,
        "Augusto": 1,
        "Gladystone": 0
    }

    qtdade_por_status = {
        "Em espera": 10,
        "Respondido pelo usuário": 5,
        "Em análise": 4,
        "Análise agendada": 3,
        "Pendente fornecedor": 2,
        "Pendente usuário": 7
    }

    corpo_email = f"""
    Olá, boa tarde,

    Este é o resumo diário dos chamados pendentes:

    Fila em atendimento:
    - Gerson: {fila_atendimento['Gerson']}
    - Estevam: {fila_atendimento['Estevam']}
    - Victor: {fila_atendimento['Victor']}
    - Augusto: {fila_atendimento['Augusto']}
    - Gladystone: {fila_atendimento['Gladystone']}

    SLA Estourados:
    - Gerson: {sla_estourados['Gerson']}
    - Estevam: {sla_estourados['Estevam']}
    - Victor: {sla_estourados['Victor']}
    - Augusto: {sla_estourados['Augusto']}
    - Gladystone: {sla_estourados['Gladystone']}

    Abertos a mais de 3 dias:
    - Gerson: {abertos_mais_3_dias['Gerson']}
    - Estevam: {abertos_mais_3_dias['Estevam']}
    - Victor: {abertos_mais_3_dias['Victor']}
    - Augusto: {abertos_mais_3_dias['Augusto']}
    - Gladystone: {abertos_mais_3_dias['Gladystone']}

    Qtdade por Analista x Status:
    - Em espera: {qtdade_por_status['Em espera']}
    - Respondido pelo usuário: {qtdade_por_status['Respondido pelo usuário']}
    - Em análise: {qtdade_por_status['Em análise']}
    - Análise agendada: {qtdade_por_status['Análise agendada']}
    - Pendente fornecedor: {qtdade_por_status['Pendente fornecedor']}
    - Pendente usuário: {qtdade_por_status['Pendente usuário']}

    Atenciosamente, Isabelle.
    """

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ", ".join(to_email)
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo_email, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 527)
        server.starttls()
        server.login(from_email, senha)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        return "E-mail enviado com sucesso!"
    except Exception as e:
        return f"Erro ao enviar e-mail: {e}"

def agendar_envio_email():
    schedule.every().monday.at("17:00").do(enviar_email)
    schedule.every().tuesday.at("17:00").do(enviar_email)
    schedule.every().wednesday.at("17:00").do(enviar_email)
    schedule.every().thursday.at("17:00").do(enviar_email)
    schedule.every().friday.at("17:00").do(enviar_email)

    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/enviar_whatsapp', methods=['POST'])
def rota_whatsapp():
    try:
        analistas_selecionados = request.json.get('analistas', [])  
        chamados = request.json.get('chamados', {})

        if not analistas_selecionados:
            return jsonify({"mensagem": "Nenhum analista selecionado"}), 400

        resultados = enviar_mensagens_para_analistas(analistas_selecionados, chamados)
        return jsonify({"mensagem": "Mensagens enviadas com sucesso!", "resultados": resultados})
    except Exception as e:
        return jsonify({"mensagem": f"Erro na requisição: {e}"}), 500

@app.route('/enviar_email', methods=['GET'])
def rota_email():
    try:
        resultado = enviar_email()
        return jsonify({"mensagem": resultado})
    except Exception as e:
        return jsonify({"mensagem": f"Erro ao enviar e-mail: {e}"}), 500

if __name__ == '__main__':
    from threading import Thread
    email_thread = Thread(target=agendar_envio_email)
    email_thread.daemon = True
    email_thread.start()

    app.run(debug=True)


