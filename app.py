from flask import Flask, render_template, request, session, redirect, url_for
import urllib.parse
import os

app = Flask(__name__)

# Configurações
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sua_chave_secreta_pode_ser_qualquer_coisa_se_estiver_em_dev')
NUMERO_WHATSAPP_LOJA = os.environ.get('WHATSAPP_NUMBER', "5594991569871")

# Menu de produtos
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

def encontrar_produto_por_id(produto_id):
    for categoria in MENU.values():
        for produto in categoria:
            if produto['id'] == produto_id:
                return produto
    return None

@app.route('/')
def mostrar_menu():
    return render_template('menu.html', menu=MENU, carrinho=session.get('carrinho', {}))

@app.route('/adicionar', methods=['POST'])
def adicionar_ao_carrinho():
    produto_id = int(request.form['produto_id'])
    
    if 'carrinho' not in session:
        session['carrinho'] = {}
        
    carrinho = session['carrinho']
    carrinho[str(produto_id)] = carrinho.get(str(produto_id), 0) + 1
    session.modified = True
    return redirect(url_for('mostrar_menu'))

@app.route('/remover/<int:produto_id>')
def remover_do_carrinho(produto_id):
    carrinho = session.get('carrinho', {})
    produto_str = str(produto_id)
    
    if produto_str in carrinho:
        if carrinho[produto_str] > 1:
            carrinho[produto_str] -= 1
        else:
            del carrinho[produto_str]
        session.modified = True
    
    return redirect(url_for('ver_carrinho'))

@app.route('/carrinho')
def ver_carrinho():
    carrinho = session.get('carrinho', {})
    itens_carrinho = []
    total_pedido = 0.0
    
    for produto_id, quantidade in carrinho.items():
        produto = encontrar_produto_por_id(int(produto_id))
        if produto:
            subtotal = produto['preco'] * quantidade
            total_pedido += subtotal
            itens_carrinho.append({
                'produto': produto,
                'quantidade': quantidade,
                'subtotal': subtotal
            })
    
    return render_template('carrinho.html', itens_carrinho=itens_carrinho, total_pedido=total_pedido)

@app.route('/finalizar', methods=['POST'])
def finalizar_pedido():
    nome_cliente = request.form['nome']
    endereco_cliente = request.form['endereco']
    carrinho = session.get('carrinho', {})
    
    if not carrinho:
        return redirect(url_for('mostrar_menu'))
    
    mensagem = f"*NOVO PEDIDO*\\n\\n*Cliente:* {nome_cliente}\\n*Endereço:* {endereco_cliente}\\n\\n*Itens:*\\n"
    total_pedido = 0
    
    for produto_id, quantidade in carrinho.items():
        produto = encontrar_produto_por_id(int(produto_id))
        if produto:
            subtotal = produto['preco'] * quantidade
            total_pedido += subtotal
            mensagem += f"- {produto['nome']} ({quantidade}x): R${subtotal:.2f}\\n"
    
    mensagem += f"\\n*TOTAL: R${total_pedido:.2f}*"
    mensagem_codificada = urllib.parse.quote(mensagem)
    
    session.pop('carrinho', None)
    link_whatsapp = f"https://wa.me/{NUMERO_WHATSAPP_LOJA}?text={mensagem_codificada}"
    return render_template('pedido_finalizado.html', link_whatsapp=link_whatsapp)

if __name__ == '__main__':
    app.run(debug=True)
