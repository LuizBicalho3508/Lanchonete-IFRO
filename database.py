# Em database.py, substitua a função criar_tabelas

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
    
    # Inserir usuário admin padrão com e-mail se não existir
    cursor.execute("SELECT * FROM usuarios WHERE role = 'admin'")
    if not cursor.fetchone():
        # Usuário admin padrão agora é um e-mail
        admin_email = 'admin@ifro.edu.br'
        admin_pass_hash = hash_password('admin123')
        cursor.execute("INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)", 
                       (admin_email, admin_pass_hash, 'admin'))

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
