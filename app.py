from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import stripe
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import time
import qrcode
import io
import base64

# Carrega as variáveis de ambiente
load_dotenv()

# Configura as chaves do Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'chave-secreta-padrao')

# Lista de produtos (em um caso real, isso viria de um banco de dados)
produtos = [
    {
        'id': 1,
        'nome': 'X-Burger',
        'descricao': 'Hambúrguer com queijo, alface, tomate e molho especial',
        'preco': 25.90,
        'imagem': '/static/images/xburger.jpg'
    },
    {
        'id': 2,
        'nome': 'X-Bacon',
        'descricao': 'Hambúrguer com queijo, bacon, alface, tomate e molho especial',
        'preco': 28.90,
        'imagem': '/static/images/pizza.jpg'
    },
    {
        'id': 3,
        'nome': 'X-Tudo',
        'descricao': 'Hambúrguer com queijo, bacon, ovo, alface, tomate e molho especial',
        'preco': 32.90,
        'imagem': '/static/images/batata.jpg'
    }
]

def get_produto_por_id(produto_id):
    for produto in produtos:
        if produto['id'] == produto_id:
            return produto
    return None

def calcular_total():
    total = 0
    if 'carrinho' in session:
        for item in session['carrinho']:
            produto = get_produto_por_id(item['produto_id'])
            if produto:
                total += produto['preco'] * item['quantidade']
    return total

@app.route('/')
def index():
    produtos = [
        {
            'id': 1,
            'nome': 'X-Burger',
            'descricao': 'Hambúrguer com queijo, alface, tomate e molho especial',
            'preco': 25.90,
            'imagem': '/static/images/xburger.jpg'
        },
        {
            'id': 2,
            'nome': 'X-Bacon',
            'descricao': 'Hambúrguer com queijo, bacon, alface, tomate e molho especial',
            'preco': 28.90,
            'imagem': '/static/images/pizza.jpg'
        },
        {
            'id': 3,
            'nome': 'X-Tudo',
            'descricao': 'Hambúrguer com queijo, bacon, ovo, alface, tomate e molho especial',
            'preco': 32.90,
            'imagem': '/static/images/batata.jpg'
        }
    ]
    
    pedido_atual = session.get('pedido_atual', [])
    historico_pedidos = session.get('historico_pedidos', [])
    total = sum(item['preco_total'] for item in pedido_atual)
    
    return render_template('index.html', 
                         produtos=produtos, 
                         pedido_atual=pedido_atual,
                         historico_pedidos=historico_pedidos,
                         total=total)

@app.route('/produto/<int:produto_id>')
def detalhes_produto(produto_id):
    produto = get_produto_por_id(produto_id)
    if produto:
        return render_template('detalhes.html', produto=produto)
    return redirect(url_for('index'))

@app.route('/carrinho')
def carrinho():
    itens = session.get('pedido_atual', [])
    total = sum(item['preco_total'] for item in itens)
    return render_template('carrinho.html', itens=itens, total=total)

@app.route('/adicionar_ao_pedido', methods=['POST'])
def adicionar_ao_pedido():
    data = request.get_json()
    produto_id = data.get('produto_id')
    quantidade = data.get('quantidade', 1)
    extras = data.get('extras', [])

    # Encontra o produto no cardápio
    produto = next((p for p in produtos if p['id'] == produto_id), None)
    if not produto:
        return jsonify({'success': False, 'message': 'Produto não encontrado'})

    # Calcula o preço total incluindo extras
    preco_total = produto['preco']
    extras_precos = {
        'molho_especial': 2.00,
        'ketchup': 1.50,
        'maionese': 1.50
    }
    
    for extra in extras:
        if extra in extras_precos:
            preco_total += extras_precos[extra]

    # Adiciona ao pedido atual
    if 'pedido_atual' not in session:
        session['pedido_atual'] = []
    
    item = {
        'produto_id': produto_id,
        'nome': produto['nome'],
        'quantidade': quantidade,
        'preco_unitario': produto['preco'],
        'preco_total': preco_total,
        'extras': extras
    }
    
    session['pedido_atual'].append(item)
    session.modified = True
    
    return jsonify({'success': True})

@app.route('/atualizar_quantidade', methods=['POST'])
def atualizar_quantidade():
    data = request.get_json()
    produto_id = data.get('produto_id')
    delta = data.get('delta', 0)
    
    if not produto_id or 'carrinho' not in session:
        return jsonify({'success': False, 'message': 'Dados inválidos'})
    
    for item in session['carrinho']:
        if item['produto_id'] == produto_id:
            nova_quantidade = item['quantidade'] + delta
            if nova_quantidade > 0:
                item['quantidade'] = nova_quantidade
            else:
                session['carrinho'].remove(item)
            break
    
    session.modified = True
    return jsonify({'success': True})

@app.route('/remover_item', methods=['POST'])
def remover_item():
    data = request.get_json()
    produto_id = data.get('produto_id')
    
    if 'pedido_atual' in session:
        session['pedido_atual'] = [item for item in session['pedido_atual'] if item['produto_id'] != produto_id]
        session.modified = True
    
    return jsonify({'success': True})

@app.route('/finalizar_pedido', methods=['POST'])
def finalizar_pedido():
    if 'pedido_atual' not in session or not session['pedido_atual']:
        return jsonify({'success': False, 'message': 'Nenhum item no pedido'})
    
    # Cria uma cópia dos itens do pedido atual para o histórico
    itens_historico = []
    for item in session['pedido_atual']:
        produto = get_produto_por_id(item['produto_id'])
        if produto:
            item_historico = {
                'produto': produto,
                'quantidade': item['quantidade'],
                'extras': item['extras']
            }
            itens_historico.append(item_historico)
    
    # Cria um novo pedido para o histórico
    pedido = {
        'id': len(session.get('historico_pedidos', [])) + 1,
        'itens': itens_historico,
        'data': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'total': sum(item['preco_total'] for item in session['pedido_atual']),
        'status': 'Em preparação'
    }
    
    # Adiciona ao histórico
    if 'historico_pedidos' not in session:
        session['historico_pedidos'] = []
    session['historico_pedidos'].insert(0, pedido)  # Adiciona no início da lista
    
    # Limpa o pedido atual
    session['pedido_atual'] = []
    session.modified = True
    
    return jsonify({'success': True})

@app.route('/atualizar_status_pedido', methods=['POST'])
def atualizar_status_pedido():
    data = request.get_json()
    pedido_id = data.get('pedido_id')
    novo_status = data.get('status')
    
    if not pedido_id or not novo_status:
        return jsonify({'success': False, 'message': 'ID do pedido e status são obrigatórios'})
    
    historico_pedidos = session.get('historico_pedidos', [])
    
    for pedido in historico_pedidos:
        if pedido['id'] == pedido_id:
            pedido['status'] = novo_status
            session['historico_pedidos'] = historico_pedidos
            session.modified = True
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Pedido não encontrado'})

@app.route('/historico')
def historico():
    historico_pedidos = session.get('historico_pedidos', [])
    return render_template('historico.html', pedidos=historico_pedidos)

@app.route('/pagamento')
def pagamento():
    pedido_atual = session.get('pedido_atual', [])
    total = sum(item['preco_total'] for item in pedido_atual)
    return render_template('pagamento.html', pedido_atual=pedido_atual, total=total)

@app.route('/processar_pagamento', methods=['POST'])
def processar_pagamento():
    data = request.get_json()
    forma_pagamento = data.get('forma_pagamento')
    
    if not forma_pagamento:
        return jsonify({'success': False, 'message': 'Forma de pagamento não especificada'})
    
    try:
        if forma_pagamento == 'cartao':
            # Simula a integração com a máquina de cartão
            print("Aguardando aproximação do cartão...")
            # Simula o tempo de processamento
            time.sleep(3)
            print("Cartão detectado!")
            time.sleep(2)
            print("Processando pagamento...")
            time.sleep(2)
            print("Pagamento aprovado!")
            
            # Limpa o histórico de pedidos após pagamento bem-sucedido
            session['historico_pedidos'] = []
            session['pedido_atual'] = []
            session.modified = True
            
            return jsonify({
                'success': True,
                'message': 'Pagamento processado com sucesso!',
                'redirect': '/'
            })
            
        elif forma_pagamento == 'pix':
            # Gera um QR code único para o pedido
            # Cria um QR code com dados do pedido
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Dados do pedido para o QR code
            pedido_data = {
                'valor': sum(item['preco_total'] for item in session.get('pedido_atual', [])),
                'pedido_id': str(datetime.now().timestamp()),
                'timestamp': datetime.now().isoformat()
            }
            
            qr.add_data(json.dumps(pedido_data))
            qr.make(fit=True)
            
            # Cria a imagem do QR code
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converte a imagem para base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            return jsonify({
                'success': True,
                'qr_code': qr_code_base64,
                'message': 'QR Code gerado com sucesso!'
            })
        
        return jsonify({'success': False, 'message': 'Forma de pagamento não implementada'})
        
    except Exception as e:
        print(f"Erro no processamento do pagamento: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro ao processar pagamento'})

@app.route('/verificar_pagamento_pix', methods=['POST'])
def verificar_pagamento_pix():
    try:
        # Simula a verificação do pagamento PIX
        time.sleep(5)  # Simula o tempo de processamento
        
        # Limpa o histórico de pedidos após pagamento bem-sucedido
        session['historico_pedidos'] = []
        session['pedido_atual'] = []
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Pagamento PIX processado com sucesso!',
            'redirect': '/'
        })
    except Exception as e:
        print(f"Erro na verificação do pagamento PIX: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro ao verificar pagamento'})

if __name__ == '__main__':
    app.run(debug=True) 