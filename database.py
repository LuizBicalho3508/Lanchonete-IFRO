# database.py

import sqlite3
import hashlib

def hash_password(password):
    """Cria um hash SHA-256 para a senha fornecida."""
    return hashlib.sha256(password.encode()).hexdigest()

def conectar_bd():
    """Cria uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect('lanchonete_ifro.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    """Cria as tabelas 'produtos', 'pedidos' e 'usuarios'."""
    conn = conectar_bd()
    cursor = conn.cursor()
    
    # Tabela de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'cliente'))
        )
    ''')
    
    # Tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL
        )
    ''')
    
    # Tabela de pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_username TEXT NOT NULL,
            itens TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'Recebido',
            data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_username) REFERENCES usuarios (username)
        )
    ''')
    
    # Inserir usuário admin padrão se não existir
    cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
    if not cursor.fetchone():
        admin_pass_hash = hash_password('admin123')
        cursor.execute("INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)", 
                       ('admin', admin_pass_hash, 'admin'))

    # Inserir produtos iniciais se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        produtos_iniciais = [
            ('Pão de Queijo', 'Salgados', 4.50), ('Misto Quente', 'Salgados', 7.00),
            ('Coxinha', 'Salgados', 6.50), ('Bolo de Chocolate', 'Doces', 8.00),
            ('Brigadeiro', 'Doces', 3.00), ('Refrigerante Lata', 'Bebidas', 5.00),
            ('Suco Natural', 'Bebidas', 6.00)
        ]
        cursor.executemany('INSERT INTO produtos (nome, categoria, preco) VALUES (?, ?, ?)', produtos_iniciais)
    
    conn.commit()
    conn.close()

# --- Funções de Usuário ---
def add_user(username, password, role='cliente'):
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
                       (username, hash_password(password), role))
        conn.commit()
        return True
    except sqlite3.IntegrityError: # Username já existe
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role FROM usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and user['password_hash'] == hash_password(password):
        return user['role']
    return None

# --- Funções de Produto (Admin) ---
def add_produto(nome, categoria, preco):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, categoria, preco) VALUES (?, ?, ?)", (nome, categoria, preco))
    conn.commit()
    conn.close()

def update_produto(id, nome, categoria, preco):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("UPDATE produtos SET nome = ?, categoria = ?, preco = ? WHERE id = ?", (nome, categoria, preco, id))
    conn.commit()
    conn.close()

def delete_produto(id):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def get_produtos():
    conn = conectar_bd()
    produtos = conn.execute('SELECT * FROM produtos ORDER BY categoria, nome').fetchall()
    conn.close()
    return produtos

# --- Funções de Pedido ---
def salvar_pedido(cliente_username, itens, total):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO pedidos (cliente_username, itens, total) VALUES (?, ?, ?)',
        (cliente_username, str(itens), total)
    )
    conn.commit()
    conn.close()

def get_all_pedidos():
    conn = conectar_bd()
    pedidos = conn.execute('SELECT * FROM pedidos ORDER BY data_pedido DESC').fetchall()
    conn.close()
    return pedidos

# Adicione estas funções ao seu arquivo database.py

# --- Funções de Usuário (novas funções para admin) ---

def get_all_users():
    """Busca todos os usuários cadastrados."""
    conn = conectar_bd()
    users = conn.execute('SELECT id, username, role FROM usuarios').fetchall()
    conn.close()
    return users

def get_user_by_id(user_id):
    """Busca um usuário específico pelo seu ID."""
    conn = conectar_bd()
    user = conn.execute('SELECT id, username, role FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def update_user_by_admin(user_id, username, role):
    """Atualiza o username e o role de um usuário."""
    conn = conectar_bd()
    try:
        conn.execute('UPDATE usuarios SET username = ?, role = ? WHERE id = ?', (username, role, user_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Acontece se o novo username já existir
    finally:
        conn.close()

def reset_user_password(user_id, new_password):
    """Reseta a senha de um usuário."""
    conn = conectar_bd()
    conn.execute('UPDATE usuarios SET password_hash = ? WHERE id = ?', (hash_password(new_password), user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    """Exclui um usuário do banco de dados."""
    conn = conectar_bd()
    conn.execute('DELETE FROM usuarios WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
