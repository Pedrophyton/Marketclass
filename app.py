import os
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
    render_template_string,
    Response
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================
# MARKETCLASS
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "marketclass-secret-key-2026"
)


# ============================================================
# BANCO DE DADOS
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:

    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )

    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

else:

    DATABASE_URL = "sqlite:///marketclass.db"


app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


db = SQLAlchemy(app)


# ============================================================
# USUÁRIOS
# ============================================================

class Usuario(db.Model):

    __tablename__ = "usuarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(180),
        unique=True,
        nullable=False
    )

    senha = db.Column(
        db.String(255),
        nullable=False
    )

    contato = db.Column(
        db.String(50),
        nullable=False
    )


# ============================================================
# PRODUTOS
# ============================================================

class Produto(db.Model):

    __tablename__ = "produtos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    nome = db.Column(
        db.String(180),
        nullable=False
    )

    categoria = db.Column(
        db.String(100),
        nullable=False
    )

    preco = db.Column(
        db.Float,
        nullable=False
    )

    conservacao = db.Column(
        db.String(100),
        nullable=False
    )

    tamanho = db.Column(
        db.String(50)
    )

    descricao = db.Column(
        db.Text
    )

    imagem = db.Column(
        db.LargeBinary
    )

    imagem_tipo = db.Column(
        db.String(50)
    )

    criado_em = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )


# ============================================================
# CRIAR TABELAS AUTOMATICAMENTE
# ============================================================

with app.app_context():

    db.create_all()


# ============================================================
# FUNÇÕES
# ============================================================

def logado():

    return "usuario_id" in session


def exigir_login():

    if not logado():

        flash(
            "Faça login para continuar."
        )

        return False

    return True


def preco_formatado(preco):

    return (
        f"{preco:.2f}"
        .replace(".", ",")
    )


def imagem_permitida(nome):

    if not nome:
        return False

    extensao = nome.lower().split(".")[-1]

    return extensao in [
        "jpg",
        "jpeg",
        "png",
        "webp"
    ]


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

.orange {
    background: #ff8500;
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
}

.search button {
    background: #ff8500;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 0 20px;
    font-weight: bold;
}

main {
    max-width: 1200px;
    margin: auto;
    padding: 35px 20px 70px;
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
    max-width: 800px;
    margin: auto;
}

.profile-box,
.my-product {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #ddd;
    margin-bottom: 15px;
}

.my-product {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.delete {
    border: none;
    background: #d63031;
    color: white;
    padding: 9px 12px;
    border-radius: 8px;
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

    .my-product {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }
}

"""


# ============================================================
# BASE HTML
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
href="/"
class="logo"
>
Market<span>Class</span>
</a>

<div class="school">
EEEP Jeová Costa Lima
</div>

<nav>

<a href="/">
Início
</a>

{% if session.get("usuario_id") %}

<a href="/vender">
Vender
</a>

<a href="/perfil">
Minha conta
</a>

<a href="/logout">
Sair
</a>

{% else %}

<a href="/login">
Entrar
</a>

<a
href="/cadastro"
class="btn"
>
Criar conta
</a>

{% endif %}

</nav>

</div>

</header>


{% with mensagens = get_flashed_messages() %}

{% if mensagens %}

<div class="messages">

{% for mensagem in mensagens %}

<div class="message">
{{ mensagem }}
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
Fardamentos, livros e materiais escolares
com preços acessíveis.
</p>

</footer>

</body>

</html>

"""


def pagina(conteudo, titulo):

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


    query = Produto.query


    if busca:

        termo = f"%{busca}%"

        query = query.filter(
            db.or_(
                Produto.nome.ilike(termo),
                Produto.descricao.ilike(termo)
            )
        )


    if categoria:

        query = query.filter(
            Produto.categoria == categoria
        )


    produtos = query.order_by(
        Produto.id.desc()
    ).all()


    cards = ""


    for produto in produtos:

        if produto.imagem:

            imagem = f"""
            <img
                src="/imagem/{produto.id}"
                class="product-image"
            >
            """

        else:

            imagem = """
            <div class="product-placeholder">
                📦
            </div>
            """


        tamanho = ""

        if produto.tamanho:

            tamanho = (
                f" • Tamanho "
                f"{produto.tamanho}"
            )


        cards += f"""

        <div class="product">

            {imagem}

            <div class="product-content">

                <span class="category">
                    {produto.categoria}
                </span>

                <h3>
                    {produto.nome}
                </h3>

                <div class="price">
                    R$ {preco_formatado(produto.preco)}
                </div>

                <p class="info">
                    {produto.conservacao}
                    {tamanho}
                </p>

                <a
                    href="/produto/{produto.id}"
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
                Seja o primeiro a anunciar!
            </p>

            <a
                href="/vender"
                class="btn orange"
            >
                Anunciar produto
            </a>

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
                Fardamentos do Estado do Ceará,
                livros e materiais escolares usados
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

            <a
                class="btn orange"
                href="/vender"
            >
                + Anunciar produto
            </a>

        </div>

        <div class="products">

            {cards}

        </div>

    </main>

    """


    return pagina(
        conteudo,
        "MarketClass"
    )


# ============================================================
# CADASTRO
# ============================================================

@app.route(
    "/cadastro",
    methods=["GET", "POST"]
)
def cadastro():

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


        if not nome or not email or not contato or not senha:

            flash(
                "Preencha todos os campos."
            )

            return redirect("/cadastro")


        if len(senha) < 6:

            flash(
                "A senha precisa ter pelo menos 6 caracteres."
            )

            return redirect("/cadastro")


        existente = Usuario.query.filter_by(
            email=email
        ).first()


        if existente:

            flash(
                "Este e-mail já está cadastrado."
            )

            return redirect("/cadastro")


        usuario = Usuario(

            nome=nome,

            email=email,

            senha=generate_password_hash(
                senha
            ),

            contato=contato

        )


        db.session.add(
            usuario
        )

        db.session.commit()


        session["usuario_id"] = usuario.id

        session["usuario_nome"] = usuario.nome


        flash(
            "Conta criada com sucesso!"
        )


        return redirect("/")


    conteudo = """

    <main>

        <div class="form-card">

            <h1>
                Criar conta
            </h1>

            <p>
                Cadastre-se para comprar
                e vender no MarketClass.
            </p>

            <form
                method="POST"
                class="form"
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
                    style="color:#6f2dbd;font-weight:bold"
                >
                    Entrar
                </a>
            </p>

        </div>

    </main>

    """


    return pagina(
        conteudo,
        "Criar conta"
    )


# ============================================================
# LOGIN
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


        usuario = Usuario.query.filter_by(
            email=email
        ).first()


        if usuario and check_password_hash(
            usuario.senha,
            senha
        ):

            session["usuario_id"] = usuario.id

            session["usuario_nome"] = usuario.nome


            flash(
                "Login realizado com sucesso!"
            )


            return redirect("/")


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
                Ainda não possui uma conta?
                <a
                    href="/cadastro"
                    style="color:#6f2dbd;font-weight:bold"
                >
                    Criar conta
                </a>
            </p>

        </div>

    </main>

    """


    return pagina(
        conteudo,
        "Entrar"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ============================================================
# VENDER
# ============================================================

@app.route(
    "/vender",
    methods=["GET", "POST"]
)
def vender():

    if not exigir_login():

        return redirect("/login")


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

            return redirect("/vender")


        if not nome or not categoria:

            flash(
                "Preencha os campos obrigatórios."
            )

            return redirect("/vender")


        if preco < 0:

            flash(
                "O preço não pode ser negativo."
            )

            return redirect("/vender")


        imagem = None

        imagem_tipo = None


        arquivo = request.files.get(
            "imagem"
        )


        if arquivo and arquivo.filename:

            if not imagem_permitida(
                arquivo.filename
            ):

                flash(
                    "Use JPG, JPEG, PNG ou WEBP."
                )

                return redirect("/vender")


            imagem = arquivo.read()

            extensao = (
                arquivo.filename
                .lower()
                .split(".")[-1]
            )


            if extensao == "jpg":
                imagem_tipo = "image/jpeg"

            elif extensao == "jpeg":
                imagem_tipo = "image/jpeg"

            elif extensao == "png":
                imagem_tipo = "image/png"

            else:
                imagem_tipo = "image/webp"


        produto = Produto(

            usuario_id=session["usuario_id"],

            nome=nome,

            categoria=categoria,

            preco=preco,

            conservacao=conservacao,

            tamanho=tamanho,

            descricao=descricao,

            imagem=imagem,

            imagem_tipo=imagem_tipo

        )


        db.session.add(
            produto
        )

        db.session.commit()


        flash(
            "Produto publicado com sucesso!"
        )


        return redirect("/")


    conteudo = """

    <main>

        <div class="form-card">

            <h1>
                Anunciar produto
            </h1>

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
                </label>

                <label>
                    Preço

                    <input
                        type="number"
                        name="preco"
                        step="0.01"
                        min="0"
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
                    >
                </label>

                <label>
                    Descrição

                    <textarea
                        name="descricao"
                        rows="5"
                    ></textarea>
                </label>

                <label>
                    Foto

                    <input
                        type="file"
                        name="imagem"
                        accept=".jpg,.jpeg,.png,.webp"
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
        "Vender"
    )


# ============================================================
# MOSTRAR IMAGEM
# ============================================================

@app.route(
    "/imagem/<int:produto_id>"
)
def imagem(produto_id):

    produto = db.session.get(
        Produto,
        produto_id
    )


    if not produto or not produto.imagem:

        abort(404)


    return Response(
        produto.imagem,
        mimetype=produto.imagem_tipo
    )


# ============================================================
# DETALHES DO PRODUTO
# ============================================================

@app.route(
    "/produto/<int:produto_id>"
)
def detalhes(produto_id):

    produto = db.session.get(
        Produto,
        produto_id
    )


    if not produto:

        abort(404)


    usuario = db.session.get(
        Usuario,
        produto.usuario_id
    )


    if produto.imagem:

        imagem = f"""
        <img
            src="/imagem/{produto.id}"
            class="detail-image"
        >
        """

    else:

        imagem = """
        <div class="detail-placeholder">
            📦
        </div>
        """


    contato = (
        usuario.contato
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
                    {produto.categoria}
                </span>

                <h1>
                    {produto.nome}
                </h1>

                <div class="detail-price">
                    R$ {preco_formatado(produto.preco)}
                </div>

                <p>
                    <strong>
                        Estado:
                    </strong>

                    {produto.conservacao}
                </p>

                <p>
                    <strong>
                        Tamanho:
                    </strong>

                    {produto.tamanho or "Não informado"}
                </p>

                <p>
                    <strong>
                        Descrição:
                    </strong>
                </p>

                <p>
                    {produto.descricao or "Sem descrição."}
                </p>

                <div class="seller">

                    <h3>
                        Vendedor
                    </h3>

                    <p>
                        <strong>
                            {usuario.nome}
                        </strong>
                    </p>

                    <p>
                        {usuario.contato}
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
        produto.nome
    )


# ============================================================
# PERFIL
# ============================================================

@app.route("/perfil")
def perfil():

    if not exigir_login():

        return redirect("/login")


    usuario = db.session.get(
        Usuario,
        session["usuario_id"]
    )


    produtos = Produto.query.filter_by(
        usuario_id=usuario.id
    ).order_by(
        Produto.id.desc()
    ).all()


    anuncios = ""


    for produto in produtos:

        anuncios += f"""

        <div class="my-product">

            <div>

                <strong>
                    {produto.nome}
                </strong>

                <p class="info">
                    {produto.categoria}
                </p>

                <div class="price">
                    R$ {preco_formatado(produto.preco)}
                </div>

            </div>

            <div>

                <a
                    href="/produto/{produto.id}"
                    class="btn"
                >
                    Ver
                </a>

                <form
                    method="POST"
                    action="/excluir/{produto.id}"
                    style="display:inline"
                >

                    <button
                        class="delete"
                        type="submit"
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


    conteudo = f"""

    <main>

        <div class="profile">

            <div class="profile-box">

                <h1>
                    Olá, {usuario.nome} 👋
                </h1>

                <p>
                    <strong>
                        E-mail:
                    </strong>

                    {usuario.email}
                </p>

                <p>
                    <strong>
                        Contato:
                    </strong>

                    {usuario.contato}
                </p>

                <a
                    href="/vender"
                    class="btn orange"
                >
                    + Novo anúncio
                </a>

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
        "Minha conta"
    )


# ============================================================
# EXCLUIR
# ============================================================

@app.route(
    "/excluir/<int:produto_id>",
    methods=["POST"]
)
def excluir(produto_id):

    if not exigir_login():

        return redirect("/login")


    produto = Produto.query.filter_by(
        id=produto_id,
        usuario_id=session["usuario_id"]
    ).first()


    if produto:

        db.session.delete(
            produto
        )

        db.session.commit()


        flash(
            "Produto excluído."
        )


    return redirect("/perfil")


# ============================================================
# EXECUTAR
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
