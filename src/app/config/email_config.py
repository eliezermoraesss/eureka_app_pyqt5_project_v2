import json
import logging


def read_email_params():
    path = (r"\\192.175.175.4\desenvolvimento\REPOSITORIOS\resources\application-properties"
            r"\GMAIL_SMTP_EMAIL_PARAMS.txt")
    try:
        with open(path, 'r') as file:
            string = file.read()
            email_params = json.loads(string)
            return email_params
    except FileNotFoundError as ex:
        logging.error(f"Arquivo não localizado: {ex}")
    except json.JSONDecodeError as ex:
        logging.error(f"O arquivo não está no formato JSON válido: {ex}")
    except Exception as ex:
        logging.error(f"Ocorreu um erro ao ler o arquivo: {ex}")
