from flask import Flask, render_template, request, session, redirect, url_for
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis de ambiente

app = Flask(__name__)

# Configurações
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_123')
NUMERO_WHATSAPP_LOJA = os.environ.get('WHATSAPP_NUMBER', "5594991569871")

# Menu de produtos (estrutura otimizada)
MENU = {
    'cervejas': [
        {'id': 1, 'nome': 'Brahma Duplo Malte 350ml', 'preco': 3.50},
        {'id': 2, 'nome': 'Heineken 330ml', 'preco': 5.50},
        {'id': 3, 'nome': 'Stella Artois 275ml', 'preco': 4.80},
    ],
    'refrigerantes': [
        {'id': 4, 'nome': 'Coca-Cola 2L', 'preco': 10.00},
        {'id': 5, 'nome': 'Guaraná Antarctica 2L', 'preco': 9.00},
        {'id': 6, 'nome': 'Fanta Laranja 350ml', 'preco': 4.00},
    ],
    'lanches': [
        {'id': 7, 'nome': 'X-Burger Clássico', 'preco': 15.00},
        {'id': 8, 'nome': 'Porção de Batata Frita (M)', 'preco': 12.50},
    ]
}

# Cache de produtos para busca rápida
PRODUTOS = {prod['id']: prod for categoria in MENU.values() for prod in categoria}

@app.route('/')
def mostrar_menu():
    return render_template('menu.html', menu=MENU, carrinho=session.get('carrinho', {}))

@app.route('/adicionar', methods=['POST'])
def adicionar_ao_carrinho():
    produto_id = int(request.form['produto_id'])
    
    carrinho = session.get('carrinho', {})
    chave = str(produto_id)
    
    # Atualiza quantidade
    carrinho[chave] = carrinho.get(chave, 0) + 1
    session['carrinho'] = carrinho
    
    return redirect(url_for('mostrar_menu'))

@app.route('/remover/<int:produto_id>')
def remover_do_carrinho(produto_id):
    carrinho = session.get('carrinho', {})
    chave = str(produto_id)
    
    if chave in carrinho:
        if carrinho[chave] > 1:
            carrinho[chave] -= 1
        else:
            del carrinho[chave]
        
        session['carrinho'] = carrinho
    
    return redirect(url_for('ver_carrinho'))

@app.route('/carrinho')
def ver_carrinho():
    carrinho = session.get('carrinho', {})
    itens_carrinho = []
    total_pedido = 0.0
    
    for produto_id, quantidade in carrinho.items():
        produto = PRODUTOS.get(int(produto_id))
        if produto:
            subtotal = produto['preco'] * quantidade
            total_pedido += subtotal
            itens_carrinho.append({
                'produto': produto,
                'quantidade': quantidade,
                'subtotal': subtotal
            })
    
    return render_template('carrinho.html', 
                           itens_carrinho=itens_carrinho, 
                           total_pedido=total_pedido)

@app.route('/finalizar', methods=['POST'])
def finalizar_pedido():
    nome_cliente = request.form['nome'].strip()
    endereco_cliente = request.form['endereco'].strip()
    carrinho = session.get('carrinho', {})
    
    if not carrinho or not nome_cliente or not endereco_cliente:
        return redirect(url_for('mostrar_menu'))
    
    # Formata mensagem para WhatsApp
    mensagem = (
        f"*NOVO PEDIDO*\n\n"
        f"*Cliente:* {nome_cliente}\n"
        f"*Endereço:* {endereco_cliente}\n\n"
        f"*Itens:*\n"
    )
    
    total_pedido = 0.0
    for produto_id, quantidade in carrinho.items():
        produto = PRODUTOS.get(int(produto_id))
        if produto:
            subtotal = produto['preco'] * quantidade
            total_pedido += subtotal
            mensagem += f"- {produto['nome']} ({quantidade}x): R${subtotal:.2f}\n"
    
    mensagem += f"\n*TOTAL: R${total_pedido:.2f}*"
    mensagem_codificada = urllib.parse.quote(mensagem)
    
    # Limpa carrinho após finalização
    session.pop('carrinho', None)
    link_whatsapp = f"https://wa.me/{NUMERO_WHATSAPP_LOJA}?text={mensagem_codificada}"
    
    return render_template('pedido_finalizado.html', link_whatsapp=link_whatsapp)

if __name__ == '__main__':
    app.run(debug=True)
