import os
import requests
from dotenv import load_dotenv
import time
import json

# Carrega as variáveis de ambiente
load_dotenv()

# Configura as credenciais do PagSeguro
PAGSEGURO_EMAIL = os.getenv('PAGSEGURO_EMAIL')
PAGSEGURO_TOKEN = os.getenv('PAGSEGURO_TOKEN')
PAGSEGURO_TERMINAL_ID = os.getenv('PAGSEGURO_TERMINAL_ID')

# URL base da API do PagSeguro
BASE_URL = "https://api.pagseguro.com"

# Lista de produtos
products = [
    {'name': 'Produto 1', 'price': 1000},  # Preço em centavos
    {'name': 'Produto 2', 'price': 2000},
    {'name': 'Produto 3', 'price': 3000}
]

def display_products():
    print("\nProdutos disponíveis:")
    for i, product in enumerate(products, 1):
        print(f"{i}. {product['name']} - R$ {product['price']/100:.2f}")

def get_product_choice():
    while True:
        try:
            choice = int(input("\nSelecione o produto (número): "))
            if 1 <= choice <= len(products):
                return products[choice - 1]
            print("Opção inválida!")
        except ValueError:
            print("Por favor, digite um número válido!")

def check_terminal_status():
    headers = {
        "Authorization": f"Bearer {PAGSEGURO_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/terminals/{PAGSEGURO_TERMINAL_ID}/status"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            status = response.json().get('status')
            return status == 'connected'
        return False
    except Exception as e:
        print(f"Erro ao verificar status do terminal: {str(e)}")
        return False

def process_payment(amount, description):
    try:
        print("\nIniciando pagamento na máquina...")
        print("Por favor, insira ou deslize o cartão no terminal.")
        
        # Cria uma transação na máquina física
        headers = {
            "Authorization": f"Bearer {PAGSEGURO_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "reference_id": f"order_{int(time.time())}",
            "amount": {
                "value": amount
            },
            "description": description,
            "payment_method": "credit_card",
            "capture_method": "manual",
            "terminal_id": PAGSEGURO_TERMINAL_ID
        }
        
        url = f"{BASE_URL}/transactions"
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            transaction = response.json()
            print(f"\nID da transação: {transaction['id']}")
            print("Aguardando processamento na máquina...")
            
            # Aguarda o processamento do pagamento
            while True:
                status_url = f"{BASE_URL}/transactions/{transaction['id']}"
                status_response = requests.get(status_url, headers=headers)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    
                    if status == 'approved':
                        print("\nPagamento aprovado!")
                        return True
                    elif status == 'rejected':
                        print("\nPagamento rejeitado.")
                        return False
                    elif status == 'cancelled':
                        print("\nPagamento cancelado.")
                        return False
                
                time.sleep(2)  # Aguarda 2 segundos antes de verificar novamente
        else:
            print(f"\nErro ao criar transação: {response.text}")
            return False
            
    except Exception as e:
        print(f"\nErro ao processar pagamento: {str(e)}")
        return False

def main():
    print("=== Terminal de Pagamento PagSeguro ===")
    
    # Verifica se o terminal está conectado
    if not check_terminal_status():
        print("\nERRO: Terminal não está conectado!")
        print("Por favor, verifique a conexão do terminal.")
        return
    
    print("\nTerminal conectado e pronto para uso!")
    
    while True:
        display_products()
        product = get_product_choice()
        
        print(f"\nProcessando pagamento para: {product['name']}")
        print(f"Valor: R$ {product['price']/100:.2f}")
        
        if process_payment(product['price'], product['name']):
            print("\nOperação concluída com sucesso!")
        else:
            print("\nOperação não concluída.")
        
        # Pergunta se deseja fazer outro pagamento
        again = input("\nDeseja processar outro pagamento? (s/n): ").lower()
        if again != 's':
            break
    
    print("\nObrigado por usar nosso terminal!")

if __name__ == '__main__':
    main() 