import os
import sqlite3
import uuid

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
    send_from_directory,
    render_template_string
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename


# ============================================================
# MARKETCLASS
# Marketplace escolar
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "marketclass-secret-key-2026"
)

DATABASE = "marketclass.db"
UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# CONFIGURAÇÕES DO ADMINISTRADOR
# ============================================================

ADMIN_EMAIL = os.environ.get(
    "ADMIN_EMAIL",
    "admin@marketclass.com"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "admin123"
)

WHATSAPP_ADMIN = "5584999502071"


# ============================================================
# BANCO DE DADOS
# ============================================================

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():

    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            contato TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'comprador',
            aprovado INTEGER NOT NULL DEFAULT 0,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            conservacao TEXT NOT NULL,
            tamanho TEXT,
            descricao TEXT,
            imagem TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    db.commit()
    db.close()


init_db()


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def usuario_logado():
    return "usuario_id" in session


def admin_logado():
    return session.get("admin") is True


def exigir_login():

    if not usuario_logado():
        flash("Você precisa entrar na sua conta.")
        return False

    return True


def exigir_admin():

    if not admin_logado():
        flash("Acesso exclusivo do administrador.")
        return False

    return True


def usuario_aprovado():

    if not usuario_logado():
        return False

    db = get_db()

    usuario = db.execute(
        """
        SELECT *
        FROM usuarios
        WHERE id = ?
        """,
        (session["usuario_id"],)
    ).fetchone()

    db.close()

    if not usuario:
        return False

    return (
        usuario["tipo"] == "vendedor"
        and
        usuario["aprovado"] == 1
    )


# ============================================================
# CSS
# ============================================================

CSS = """

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #f7f5fa;
    color: #202124;
}

a {
    text-decoration: none;
    color: inherit;
}

header {
    background: white;
    border-bottom: 1px solid #e5e0ea;
    position: sticky;
    top: 0;
    z-index: 100;
}

.navbar {
    max-width: 1200px;
    margin: auto;
    min-height: 70px;
    padding: 10px 20px;
    display: flex;
    align-items: center;
    gap: 20px;
}

.logo {
    font-size: 28px;
    font-weight: 900;
    color: #6f2dbd;
}

.logo span {
    color: #ff8500;
}

.school {
    color: #777;
    font-size: 13px;
    margin-right: auto;
}

nav {
    display: flex;
    align-items: center;
    gap: 5px;
}

nav a {
    padding: 9px 10px;
    font-size: 14px;
}

.btn {
    display: inline-block;
    background: #6f2dbd;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 11px 16px;
    font-weight: bold;
    cursor: pointer;
}

.btn:hover {
    opacity: .9;
}

.orange {
    background: #ff8500;
}

.red {
    background: #d63031;
}

.green {
    background: #159447;
}

.gray {
    background: #666;
}

.purple {
    color: #6f2dbd;
    font-weight: bold;
}

.hero {
    background: linear-gradient(
        135deg,
        #4b168a,
        #6f2dbd
    );

    color: white;
    padding: 65px 20px;
}

.hero-content {
    max-width: 1000px;
    margin: auto;
}

.hero h1 {
    font-size: 45px;
    margin: 0 0 15px;
}

.hero p {
    max-width: 750px;
    font-size: 18px;
    line-height: 1.6;
}

.search {
    max-width: 900px;
    background: white;
    padding: 7px;
    border-radius: 12px;
    display: flex;
    gap: 7px;
    margin-top: 25px;
}

.search input,
.search select {
    flex: 1;
    min-width: 0;
    padding: 13px;
    border: none;
    outline: none;
    font-size: 15px;
}

.search button {
    background: #ff8500;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 0 20px;
    font-weight: bold;
    cursor: pointer;
}

main {
    max-width: 1200px;
    margin: auto;
    padding: 35px 20px 70px;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.products {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
}

.product {
    background: white;
    border: 1px solid #e5e0ea;
    border-radius: 16px;
    overflow: hidden;
    transition: transform .2s;
}

.product:hover {
    transform: translateY(-3px);
}

.product-image {
    width: 100%;
    height: 190px;
    object-fit: cover;
}

.product-placeholder {
    height: 190px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #f1e8ff;
    font-size: 60px;
}

.product-content {
    padding: 16px;
}

.category {
    color: #6f2dbd;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
}

.product h3 {
    min-height: 42px;
}

.price {
    color: #6f2dbd;
    font-size: 21px;
    font-weight: 900;
}

.info {
    color: #777;
    font-size: 13px;
}

.form-card {
    max-width: 650px;
    margin: 20px auto;
    padding: 30px;
    background: white;
    border: 1px solid #e5e0ea;
    border-radius: 18px;
}

.form {
    display: grid;
    gap: 16px;
}

.form label {
    font-weight: bold;
}

.form input,
.form select,
.form textarea {
    width: 100%;
    margin-top: 6px;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 9px;
    font-size: 15px;
    font-family: inherit;
}

.detail {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 45px;
}

.detail-image {
    width: 100%;
    max-height: 550px;
    object-fit: contain;
    background: #f1e8ff;
    border-radius: 18px;
}

.detail-placeholder {
    width: 100%;
    height: 450px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #f1e8ff;
    border-radius: 18px;
    font-size: 100px;
}

.detail h1 {
    font-size: 38px;
}

.detail-price {
    color: #6f2dbd;
    font-size: 34px;
    font-weight: 900;
}

.seller {
    margin-top: 25px;
    padding: 20px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 15px;
}

.profile {
    max-width: 900px;
    margin: auto;
}

.profile-box {
    background: white;
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #ddd;
    margin-bottom: 25px;
}

.my-product {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
    background: white;
    padding: 15px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 12px;
}

.delete {
    border: none;
    background: #d63031;
    color: white;
    padding: 9px 12px;
    border-radius: 8px;
    cursor: pointer;
}

.messages {
    max-width: 1000px;
    margin: 15px auto;
    padding: 0 15px;
}

.message {
    background: #e9f8ee;
    color: #17652c;
    padding: 13px;
    border-radius: 10px;
}

.empty {
    text-align: center;
    background: white;
    border-radius: 15px;
    padding: 50px;
    grid-column: 1 / -1;
}

.admin-card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 15px;
}

.status {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 12px;
}

.pending {
    background: #fff3cd;
    color: #856404;
}

.approved {
    background: #d4edda;
    color: #155724;
}

.rejected {
    background: #f8d7da;
    color: #721c24;
}

.tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.tab {
    flex: 1;
    text-align: center;
    padding: 14px;
    background: #eee;
    border-radius: 10px;
    font-weight: bold;
}

.tab.active {
    background: #6f2dbd;
    color: white;
}

footer {
    background: #24113b;
    color: white;
    text-align: center;
    padding: 35px 20px;
}

@media (max-width: 950px) {

    .products {
        grid-template-columns: repeat(2, 1fr);
    }

    .detail {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 650px) {

    .navbar {
        flex-wrap: wrap;
    }

    .school {
        display: none;
    }

    nav {
        width: 100%;
        justify-content: center;
        flex-wrap: wrap;
    }

    .hero h1 {
        font-size: 32px;
    }

    .search {
        flex-direction: column;
    }

    .search button {
        padding: 13px;
    }

    .products {
        grid-template-columns: 1fr;
    }

    .section-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }

    .detail h1 {
        font-size: 30px;
    }

    .my-product {
        flex-direction: column;
        align-items: flex-start;
    }

    .tabs {
        flex-direction: column;
    }
}
"""


# ============================================================
# HTML BASE
# ============================================================

BASE = """

<!DOCTYPE html>

<html lang="pt-BR">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width, initial-scale=1.0"
>

<title>{{ titulo }}</title>

<style>
{{ css }}
</style>

</head>

<body>

<header>

<div class="navbar">

<a
href="{{ url_for('index') }}"
class="logo"
>
Market<span>Class</span>
</a>

<div class="school">
EEEP Jeová Costa Lima
</div>

<nav>

<a href="{{ url_for('index') }}">
Início
</a>

{% if session.get("usuario_id") %}

<a href="{{ url_for('perfil') }}">
Minha conta
</a>

{% if session.get("tipo") == "vendedor" %}

<a href="{{ url_for('vender') }}">
Vender
</a>

{% endif %}

<a href="{{ url_for('logout') }}">
Sair
</a>

{% else %}

<a href="{{ url_for('login') }}">
Entrar
</a>

<a
href="{{ url_for('cadastro') }}"
class="btn"
>
Criar conta
</a>

{% endif %}

{% if session.get("admin") %}

<a
href="{{ url_for('admin') }}"
class="btn orange"
>
Admin
</a>

<a href="{{ url_for('admin_logout') }}">
Sair Admin
</a>

{% endif %}

</nav>

</div>

</header>

{% with messages = get_flashed_messages() %}

{% if messages %}

<div class="messages">

{% for message in messages %}

<div class="message">
{{ message }}
</div>

{% endfor %}

</div>

{% endif %}

{% endwith %}

{{ conteudo | safe }}

<footer>

<h3>
MarketClass
</h3>

<p>
Marketplace da EEEP Jeová Costa Lima
</p>

<p>
Fardamentos, livros e materiais escolares.
</p>

</footer>

</body>

</html>
"""


def pagina(conteudo, titulo="MarketClass"):

    return render_template_string(
        BASE,
        conteudo=conteudo,
        titulo=titulo,
        css=CSS
    )


# ============================================================
# INÍCIO
# ============================================================

@app.route("/")
def index():

    busca = request.args.get(
        "busca",
        ""
    ).strip()

    categoria = request.args.get(
        "categoria",
        ""
    ).strip()

    db = get_db()

    query = """

        SELECT
            produtos.*,
            usuarios.nome AS vendedor
        FROM produtos
        JOIN usuarios
            ON produtos.usuario_id = usuarios.id
        WHERE usuarios.aprovado = 1
        AND usuarios.tipo = 'vendedor'

    """

    params = []

    if busca:

        query += """
            AND (
                produtos.nome LIKE ?
                OR produtos.descricao LIKE ?
            )
        """

        params.extend([
            f"%{busca}%",
            f"%{busca}%"
        ])

    if categoria:

        query += """
            AND produtos.categoria = ?
        """

        params.append(categoria)

    query += """
        ORDER BY produtos.id DESC
    """

    produtos = db.execute(
        query,
        params
    ).fetchall()

    db.close()

    cards = ""

    for produto in produtos:

        if produto["imagem"]:

            imagem = f"""
            <img
                src="/uploads/{produto['imagem']}"
                class="product-image"
            >
            """

        else:

            imagem = """
            <div class="product-placeholder">
                📦
            </div>
            """

        preco = (
            f"{produto['preco']:.2f}"
            .replace(".", ",")
        )

        tamanho = ""

        if produto["tamanho"]:

            tamanho = (
                f" • Tamanho "
                f"{produto['tamanho']}"
            )

        cards += f"""

        <div class="product">

            {imagem}

            <div class="product-content">

                <span class="category">
                    {produto['categoria']}
                </span>

                <h3>
                    {produto['nome']}
                </h3>

                <div class="price">
                    R$ {preco}
                </div>

                <p class="info">
                    {produto['conservacao']}
                    {tamanho}
                </p>

                <p class="info">
                    Vendedor:
                    {produto['vendedor']}
                </p>

                <a
                    href="/produto/{produto['id']}"
                    class="btn"
                >
                    Ver detalhes
                </a>

            </div>

        </div>
        """

    if not cards:

        cards = """

        <div class="empty">

            <h3>
                Nenhum produto encontrado.
            </h3>

            <p>
                Ainda não existem anúncios disponíveis.
            </p>

        </div>

        """

    conteudo = f"""

    <section class="hero">

        <div class="hero-content">

            <h1>
                Compre e venda
                na sua escola.
            </h1>

            <p>
                Encontre fardamentos,
                livros e materiais escolares
                por preços acessíveis.
            </p>

            <form
                class="search"
                method="GET"
            >

                <input
                    type="text"
                    name="busca"
                    placeholder="O que você procura?"
                    value="{busca}"
                >

                <select name="categoria">

                    <option value="">
                        Todas as categorias
                    </option>

                    <option value="Fardamento">
                        Fardamento
                    </option>

                    <option value="Livro">
                        Livro
                    </option>

                    <option value="Material escolar">
                        Material escolar
                    </option>

                    <option value="Mochila">
                        Mochila
                    </option>

                    <option value="Calçado">
                        Calçado
                    </option>

                    <option value="Outros">
                        Outros
                    </option>

                </select>

                <button>
                    Pesquisar
                </button>

            </form>

        </div>

    </section>

    <main>

        <div class="section-header">

            <h2>
                Produtos disponíveis
            </h2>

            {% if session.get("tipo") == "vendedor" %}

            <a
                class="btn orange"
                href="/vender"
            >
                + Anunciar produto
            </a>

            {% endif %}

        </div>

        <div class="products">

            {cards}

        </div>

    </main>

    """

    return pagina(
        conteudo,
        "MarketClass — EEEP Jeová Costa Lima"
    )


# ============================================================
# CADASTRO
# ============================================================

@app.route(
    "/cadastro",
    methods=["GET", "POST"]
)
def cadastro():

    tipo = request.args.get(
        "tipo",
        "comprador"
    )

    if tipo not in [
        "comprador",
        "vendedor"
    ]:
        tipo = "comprador"

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        contato = request.form.get(
            "contato",
            ""
        ).strip()

        senha = request.form.get(
            "senha",
            ""
        )

        tipo = request.form.get(
            "tipo",
            "comprador"
        )

        if tipo not in [
            "comprador",
            "vendedor"
        ]:

            tipo = "comprador"

        if not all([
            nome,
            email,
            contato,
            senha
        ]):

            flash(
                "Preencha todos os campos."
            )

            return redirect(
                url_for(
                    "cadastro",
                    tipo=tipo
                )
            )

        if len(senha) < 6:

            flash(
                "A senha precisa ter pelo menos 6 caracteres."
            )

            return redirect(
                url_for(
                    "cadastro",
                    tipo=tipo
                )
            )

        aprovado = 0

        if tipo == "comprador":
            aprovado = 1

        db = get_db()

        try:

            db.execute(
                """
                INSERT INTO usuarios
                (
                    nome,
                    email,
                    senha,
                    contato,
                    tipo,
                    aprovado
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    nome,
                    email,
                    generate_password_hash(senha),
                    contato,
                    tipo,
                    aprovado
                )
            )

            db.commit()

        except sqlite3.IntegrityError:

            db.close()

            flash(
                "Este e-mail já está cadastrado."
            )

            return redirect(
                url_for(
                    "cadastro",
                    tipo=tipo
                )
            )

        usuario = db.execute(
            """
            SELECT *
            FROM usuarios
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        db.close()

        session["usuario_id"] = usuario["id"]
        session["usuario_nome"] = usuario["nome"]
        session["tipo"] = usuario["tipo"]

        if tipo == "vendedor":

            flash(
                "Cadastro realizado! Aguarde a aprovação do administrador antes de anunciar."
            )

        else:

            flash(
                "Conta de comprador criada com sucesso!"
            )

        return redirect(
            url_for("index")
        )

    vendedor_ativo = (
        "active"
        if tipo == "vendedor"
        else ""
    )

    comprador_ativo = (
        "active"
        if tipo == "comprador"
        else ""
    )

    mensagem_vendedor = ""

    if tipo == "vendedor":

        mensagem_vendedor = """

        <div class="admin-card">

            <strong>
                Atenção:
            </strong>

            <p>
                Depois do cadastro, seu perfil
                será analisado pelo administrador.
                Você só poderá publicar anúncios
                depois de ser aprovado.
            </p>

        </div>

        """

    conteudo = f"""

    <main>

        <div class="form-card">

            <h1>
                Criar conta
            </h1>

            <div class="tabs">

                <a
                    href="/cadastro?tipo=comprador"
                    class="tab {comprador_ativo}"
                >
                    🛒 Comprador
                </a>

                <a
                    href="/cadastro?tipo=vendedor"
                    class="tab {vendedor_ativo}"
                >
                    🏪 Vendedor
                </a>

            </div>

            {mensagem_vendedor}

            <form
                method="POST"
                class="form"
            >

                <input
                    type="hidden"
                    name="tipo"
                    value="{tipo}"
                >

                <label>

                    Nome completo

                    <input
                        type="text"
                        name="nome"
                        required
                    >

                </label>

                <label>

                    E-mail

                    <input
                        type="email"
                        name="email"
                        required
                    >

                </label>

                <label>

                    WhatsApp / contato

                    <input
                        type="text"
                        name="contato"
                        placeholder="84999999999"
                        required
                    >

                </label>

                <label>

                    Senha

                    <input
                        type="password"
                        name="senha"
                        minlength="6"
                        required
                    >

                </label>

                <button
                    class="btn orange"
                    type="submit"
                >
                    Criar conta
                </button>

            </form>

            <p>

                Já possui uma conta?

                <a
                    href="/login"
                    class="purple"
                >
                    Entrar
                </a>

            </p>

        </div>

    </main>

    """

    return pagina(
        conteudo,
        "Criar conta — MarketClass"
    )


# ============================================================
# LOGIN USUÁRIO
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        senha = request.form.get(
            "senha",
            ""
        )

        db = get_db()

        usuario = db.execute(
            """
            SELECT *
            FROM usuarios
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        db.close()

        if (
            usuario
            and
            check_password_hash(
                usuario["senha"],
                senha
            )
        ):

            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["tipo"] = usuario["tipo"]

            flash(
                "Login realizado com sucesso!"
            )

            return redirect(
                url_for("index")
            )

        flash(
            "E-mail ou senha incorretos."
        )

    conteudo = """

    <main>

        <div class="form-card">

            <h1>
                Entrar
            </h1>

            <form
                method="POST"
                class="form"
            >

                <label>

                    E-mail

                    <input
                        type="email"
                        name="email"
                        required
                    >

                </label>

                <label>

                    Senha

                    <input
                        type="password"
                        name="senha"
                        required
                    >

                </label>

                <button
                    class="btn"
                    type="submit"
                >
                    Entrar
                </button>

            </form>

            <p>

                Não possui conta?

                <a
                    href="/cadastro"
                    class="purple"
                >
                    Criar conta
                </a>

            </p>

            <hr>

            <p>
                Administrador?
            </p>

            <a
                href="/admin/login"
                class="btn orange"
            >
                Entrar como administrador
            </a>

        </div>

    </main>

    """

    return pagina(
        conteudo,
        "Entrar — MarketClass"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.pop("usuario_id", None)
    session.pop("usuario_nome", None)
    session.pop("tipo", None)

    return redirect(
        url_for("index")
    )


# ============================================================
# VENDER
# ============================================================

@app.route(
    "/vender",
    methods=["GET", "POST"]
)
def vender():

    if not exigir_login():

        return redirect(
            url_for("login")
        )

    if session.get("tipo") != "vendedor":

        flash(
            "Somente vendedores podem anunciar."
        )

        return redirect(
            url_for("index")
        )

    if not usuario_aprovado():

        flash(
            "Seu cadastro de vendedor ainda não foi aprovado."
        )

        return redirect(
            url_for("perfil")
        )

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        categoria = request.form.get(
            "categoria",
            ""
        ).strip()

        preco_texto = request.form.get(
            "preco",
            ""
        ).strip()

        conservacao = request.form.get(
            "conservacao",
            ""
        ).strip()

        tamanho = request.form.get(
            "tamanho",
            ""
        ).strip()

        descricao = request.form.get(
            "descricao",
            ""
        ).strip()

        if not nome or not categoria or not preco_texto:

            flash(
                "Preencha os campos obrigatórios."
            )

            return redirect(
                url_for("vender")
            )

        try:

            preco = float(
                preco_texto.replace(
                    ",",
                    "."
                )
            )

        except ValueError:

            flash(
                "Digite um preço válido."
            )

            return redirect(
                url_for("vender")
            )

        if preco < 0:

            flash(
                "O preço não pode ser negativo."
            )

            return redirect(
                url_for("vender")
            )

        imagem = None

        arquivo = request.files.get(
            "imagem"
        )

        if arquivo and arquivo.filename:

            if not allowed_file(
                arquivo.filename
            ):

                flash(
                    "Formato de imagem não permitido."
                )

                return redirect(
                    url_for("vender")
                )

            nome_original = secure_filename(
                arquivo.filename
            )

            extensao = (
                nome_original
                .rsplit(".", 1)[1]
                .lower()
            )

            imagem = (
                str(uuid.uuid4())
                + "."
                + extensao
            )

            caminho = os.path.join(
                UPLOAD_FOLDER,
                imagem
            )

            arquivo.save(caminho)

        db = get_db()

        db.execute(
            """
            INSERT INTO produtos
            (
                usuario_id,
                nome,
                categoria,
                preco,
                conservacao,
                tamanho,
                descricao,
                imagem
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["usuario_id"],
                nome,
                categoria,
                preco,
                conservacao,
                tamanho,
                descricao,
                imagem
            )
        )

        db.commit()
        db.close()

        flash(
            "Produto anunciado com sucesso!"
        )

        return redirect(
            url_for("index")
        )

    conteudo = """

    <main>

        <div class="form-card">

            <h1>
                Anunciar produto
            </h1>

            <p>
                Seu anúncio ficará visível
                para os outros usuários.
            </p>

            <form
                method="POST"
                enctype="multipart/form-data"
                class="form"
            >

                <label>

                    Nome do produto

                    <input
                        type="text"
                        name="nome"
                        placeholder="Ex.: Camisa do fardamento"
                        required
                    >

                </label>

                <label>

                    Categoria

                    <select
                        name="categoria"
                        required
                    >

                        <option>
                            Fardamento
                        </option>

                        <option>
                            Livro
                        </option>

                        <option>
                            Material escolar
                        </option>

                        <option>
                            Mochila
                        </option>

                        <option>
                            Calçado
                        </option>

                        <option>
                            Outros
                        </option>

                    </select>

                </label>

                <label>

                    Preço

                    <input
                        type="number"
                        name="preco"
                        step="0.01"
                        min="0"
                        placeholder="25.00"
                        required
                    >

                </label>

                <label>

                    Estado de conservação

                    <select
                        name="conservacao"
                        required
                    >

                        <option>
                            Novo
                        </option>

                        <option>
                            Como novo
                        </option>

                        <option>
                            Bom estado
                        </option>

                        <option>
                            Usado
                        </option>

                    </select>

                </label>

                <label>

                    Tamanho

                    <input
                        type="text"
                        name="tamanho"
                        placeholder="Ex.: M"
                    >

                </label>

                <label>

                    Descrição

                    <textarea
                        name="descricao"
                        rows="5"
                        placeholder="Descreva o produto..."
                    ></textarea>

                </label>

                <label>

                    Foto

                    <input
                        type="file"
                        name="imagem"
                        accept="image/png,image/jpeg,image/webp"
                    >

                </label>

                <button
                    class="btn orange"
                    type="submit"
                >
                    Publicar anúncio
                </button>

            </form>

        </div>

    </main>

    """

    return pagina(
        conteudo,
        "Vender — MarketClass"
    )


# ============================================================
# PRODUTO
# ============================================================

@app.route(
    "/produto/<int:produto_id>"
)
def produto(produto_id):

    db = get_db()

    produto = db.execute(
        """
        SELECT
            produtos.*,
            usuarios.nome AS vendedor,
            usuarios.contato
        FROM produtos
        JOIN usuarios
            ON produtos.usuario_id = usuarios.id
        WHERE produtos.id = ?
        AND usuarios.aprovado = 1
        """,
        (produto_id,)
    ).fetchone()

    db.close()

    if not produto:
        abort(404)

    preco = (
        f"{produto['preco']:.2f}"
        .replace(".", ",")
    )

    if produto["imagem"]:

        imagem = f"""
        <img
            src="/uploads/{produto['imagem']}"
            class="detail-image"
        >
        """

    else:

        imagem = """
        <div class="detail-placeholder">
            📦
        </div>
        """

    tamanho = ""

    if produto["tamanho"]:

        tamanho = f"""
        <p>
            <strong>
                Tamanho:
            </strong>
            {produto['tamanho']}
        </p>
        """

    contato = (
        produto["contato"]
        .replace(" ", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
    )

    conteudo = f"""

    <main>

        <div class="detail">

            <div>
                {imagem}
            </div>

            <div>

                <span class="category">
                    {produto['categoria']}
                </span>

                <h1>
                    {produto['nome']}
                </h1>

                <div class="detail-price">
                    R$ {preco}
                </div>

                <p>
                    <strong>
                        Estado:
                    </strong>
                    {produto['conservacao']}
                </p>

                {tamanho}

                <p>
                    <strong>
                        Descrição:
                    </strong>
                </p>

                <p>
                    {produto['descricao']
                    or
                    'Nenhuma descrição informada.'}
                </p>

                <div class="seller">

                    <h3>
                        Vendedor
                    </h3>

                    <p>
                        <strong>
                            {produto['vendedor']}
                        </strong>
                    </p>

                    <p>
                        Contato:
                        {produto['contato']}
                    </p>

                    <a
                        class="btn orange"
                        target="_blank"
                        href="https://wa.me/55{contato}"
                    >
                        Conversar pelo WhatsApp
                    </a>

                </div>

            </div>

        </div>

    </main>

    """

    return pagina(
        conteudo,
        f"{produto['nome']} — MarketClass"
    )


# ============================================================
# PERFIL
# ============================================================

@app.route("/perfil")
def perfil():

    if not exigir_login():

        return redirect(
            url_for("login")
        )

    db = get_db()

    usuario = db.execute(
        """
        SELECT *
        FROM usuarios
        WHERE id = ?
        """,
        (session["usuario_id"],)
    ).fetchone()

    produtos = db.execute(
        """
        SELECT *
        FROM produtos
        WHERE usuario_id = ?
        ORDER BY id DESC
        """,
        (session["usuario_id"],)
    ).fetchall()

    db.close()

    anuncios = ""

    for produto in produtos:

        preco = (
            f"{produto['preco']:.2f}"
            .replace(".", ",")
        )

        anuncios += f"""

        <div class="my-product">

            <div>

                <strong>
                    {produto['nome']}
                </strong>

                <p class="info">
                    {produto['categoria']}
                </p>

                <div class="price">
                    R$ {preco}
                </div>

            </div>

            <div>

                <a
                    href="/produto/{produto['id']}"
                    class="btn"
                >
                    Ver
                </a>

                <form
                    method="POST"
                    action="/excluir/{produto['id']}"
                    style="display:inline"
                >

                    <button
                        type="submit"
                        class="delete"
                        onclick="return confirm('Excluir este anúncio?')"
                    >
                        Excluir
                    </button>

                </form>

            </div>

        </div>

        """

    if not anuncios:

        anuncios = """

        <div class="profile-box">

            <p>
                Você ainda não possui anúncios.
            </p>

            <a
                href="/vender"
                class="btn orange"
            >
                Criar anúncio
            </a>

        </div>

        """

    status = ""

    if usuario["tipo"] == "vendedor":

        if usuario["aprovado"] == 1:

            status = """
            <span class="status approved">
                Vendedor aprovado
            </span>
            """

        else:

            status = """
            <span class="status pending">
                Aguardando aprovação
            </span>
            """

    conteudo = f"""

    <main>

        <div class="profile">

            <div class="profile-box">

                <h1>
                    Olá, {usuario['nome']} 👋
                </h1>

                <p>
                    <strong>
                        Tipo:
                    </strong>
                    {usuario['tipo'].capitalize()}
                </p>

                {status}

                <p>
                    <strong>
                        E-mail:
                    </strong>
                    {usuario['email']}
                </p>

                <p>
                    <strong>
                        Contato:
                    </strong>
                    {usuario['contato']}
                </p>

                {"<a href='/vender' class='btn orange'>+ Novo anúncio</a>"
                if usuario["tipo"] == "vendedor"
                and usuario["aprovado"] == 1
                else ""}

            </div>

            <h2>
                Meus anúncios
            </h2>

            {anuncios}

        </div>

    </main>

    """

    return pagina(
        conteudo,
        "Minha conta — MarketClass"
    )


# ============================================================
# EXCLUIR PRODUTO
# ============================================================

@app.route(
    "/excluir/<int:produto_id>",
    methods=["POST"]
)
def excluir(produto_id):

    if not exigir_login():

        return redirect(
            url_for("login")
        )

    db = get_db()

    produto = db.execute(
        """
        SELECT *
        FROM produtos
        WHERE id = ?
        AND usuario_id = ?
        """,
        (
            produto_id,
            session["usuario_id"]
        )
    ).fetchone()

    if produto:

        if produto["imagem"]:

            caminho = os.path.join(
                UPLOAD_FOLDER,
                produto["imagem"]
            )

            if os.path.exists(caminho):
                os.remove(caminho)

        db.execute(
            """
            DELETE FROM produtos
            WHERE id = ?
            """,
            (produto_id,)
        )

        db.commit()

        flash(
            "Produto excluído."
        )

    db.close()

    return redirect(
        url_for("perfil")
    )


# ============================================================
# LOGIN ADMINISTRADOR
# ============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        senha = request.form.get(
            "senha",
            ""
        )

        if (
            email == ADMIN_EMAIL.lower()
            and
            senha == ADMIN_PASSWORD
        ):

            session["admin"] = True

            flash(
                "Login de administrador realizado."
            )

            return redirect(
                url_for("admin")
            )

        flash(
            "E-mail ou senha de administrador incorretos."
        )

    conteudo = """

    <main>

        <div class="form-card">

            <h1>
                🔐 Administrador
            </h1>

            <p>
                Área exclusiva para administrar
                vendedores do MarketClass.
            </p>

            <form
                method="POST"
                class="form"
            >

                <label>

                    E-mail

                    <input
                        type="email"
                        name="email"
                        required
                    >

                </label>

                <label>

                    Senha

                    <input
                        type="password"
                        name="senha"
                        required
                    >

                </label>

                <button
                    class="btn orange"
                    type="submit"
                >
                    Entrar
                </button>

            </form>

        </div>

    </main>

    """

    return pagina(
        conteudo,
        "Administrador — MarketClass"
    )


# ============================================================
# PAINEL ADMIN
# ============================================================

@app.route("/admin")
def admin():

    if not exigir_admin():

        return redirect(
            url_for("admin_login")
        )

    db = get_db()

    vendedores = db.execute(
        """
        SELECT *
        FROM usuarios
        WHERE tipo = 'vendedor'
        ORDER BY aprovado ASC, id DESC
        """
    ).fetchall()

    db.close()

    cards = ""

    for vendedor in vendedores:

        if vendedor["aprovado"] == 1:

            status = """
            <span class="status approved">
                APROVADO
            </span>
            """

            botoes = f"""

            <form
                method="POST"
                action="/admin/rejeitar/{vendedor['id']}"
                style="display:inline"
            >

                <button
                    class="btn red"
                    type="submit"
                >
                    Rejeitar
                </button>

            </form>

            """

        else:

            status = """
            <span class="status pending">
                PENDENTE
            </span>
            """

            botoes = f"""

            <form
                method="POST"
                action="/admin/aprovar/{vendedor['id']}"
                style="display:inline"
            >

                <button
                    class="btn green"
                    type="submit"
                >
                    Aprovar vendedor
                </button>

            </form>

            """

        contato = (
            vendedor["contato"]
            .replace(" ", "")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
        )

        whatsapp_vendedor = (
            "55" + contato
        )

        cards += f"""

        <div class="admin-card">

            <h2>
                {vendedor['nome']}
            </h2>

            {status}

            <p>
                <strong>
                    E-mail:
                </strong>
                {vendedor['email']}
            </p>

            <p>
                <strong>
                    WhatsApp:
                </strong>
                {vendedor['contato']}
            </p>

            <p>
                <strong>
                    Cadastrado em:
                </strong>
                {vendedor['criado_em']}
            </p>

            <a
                class="btn orange"
                target="_blank"
                href="https://wa.me/{whatsapp_vendedor}?text=Olá%20{vendedor['nome']},%20sou%20o%20administrador%20do%20MarketClass.%20Gostaria%20de%20verificar%20seu%20cadastro%20de%20vendedor."
            >
                Verificar vendedor pelo WhatsApp
            </a>

            <br><br>

            {botoes}

        </div>

        """

    if not cards:

        cards = """

        <div class="admin-card">

            <h3>
                Nenhum vendedor cadastrado.
            </h3>

        </div>

        """

    conteudo = f"""

    <main>

        <div class="profile">

            <div class="profile-box">

                <h1>
                    🛡️ Painel administrativo
                </h1>

                <p>
                    Aqui você pode verificar
                    e aprovar os vendedores.
                </p>

                <a
                    href="/admin/logout"
                    class="btn red"
                >
                    Sair do administrador
                </a>

            </div>

            <h2>
                Vendedores
            </h2>

            {cards}

        </div>

    </main>

    """

    return pagina(
        conteudo,
        "Painel Admin — MarketClass"
    )


# ============================================================
# APROVAR VENDEDOR
# ============================================================

@app.route(
    "/admin/aprovar/<int:usuario_id>",
    methods=["POST"]
)
def aprovar_vendedor(usuario_id):

    if not exigir_admin():

        return redirect(
            url_for("admin_login")
        )

    db = get_db()

    db.execute(
        """
        UPDATE usuarios
        SET aprovado = 1
        WHERE id = ?
        AND tipo = 'vendedor'
        """,
        (usuario_id,)
    )

    db.commit()
    db.close()

    flash(
        "Vendedor aprovado com sucesso!"
    )

    return redirect(
        url_for("admin")
    )


# ============================================================
# REJEITAR VENDEDOR
# ============================================================

@app.route(
    "/admin/rejeitar/<int:usuario_id>",
    methods=["POST"]
)
def rejeitar_vendedor(usuario_id):

    if not exigir_admin():

        return redirect(
            url_for("admin_login")
        )

    db = get_db()

    db.execute(
        """
        UPDATE usuarios
        SET aprovado = 0
        WHERE id = ?
        AND tipo = 'vendedor'
        """,
        (usuario_id,)
    )

    db.commit()
    db.close()

    flash(
        "Vendedor rejeitado."
    )

    return redirect(
        url_for("admin")
    )


# ============================================================
# LOGOUT ADMIN
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(
        url_for("index")
    )


# ============================================================
# UPLOADS
# ============================================================

@app.route(
    "/uploads/<filename>"
)
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
