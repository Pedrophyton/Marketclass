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
# EEEP JEOVÁ COSTA LIMA
# Marketplace de fardamentos e materiais escolares
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

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


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

            contato TEXT NOT NULL

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

            criado_em TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(usuario_id)
                REFERENCES usuarios(id)

        )
    """)

    db.commit()

    db.close()


# ============================================================
# FUNÇÕES
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


def usuario_logado():

    return "usuario_id" in session


def exigir_login():

    if not usuario_logado():

        flash(
            "Você precisa entrar na sua conta."
        )

        return False

    return True


# ============================================================
# CSS
# ============================================================

CSS = """

* {
    box-sizing: border-box;
}

body {
    margin: 0;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background: #f7f5fa;

    color: #202124;
}

a {
    text-decoration: none;
    color: inherit;
}


/* HEADER */

header {

    background: white;

    border-bottom:
        1px solid #e5e0ea;

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

    padding:
        9px 10px;

    font-size: 14px;
}


/* BOTÕES */

.btn {

    display: inline-block;

    background:
        #6f2dbd;

    color: white;

    border: none;

    border-radius: 10px;

    padding:
        11px 16px;

    font-weight: bold;

    cursor: pointer;
}

.btn:hover {

    opacity: .9;
}

.orange {

    background:
        #ff8500;
}

.purple {

    color:
        #6f2dbd;

    font-weight:
        bold;
}


/* HERO */

.hero {

    background:
        linear-gradient(
            135deg,
            #4b168a,
            #6f2dbd
        );

    color: white;

    padding:
        65px 20px;
}

.hero-content {

    max-width:
        1000px;

    margin:
        auto;
}

.hero h1 {

    font-size:
        45px;

    margin:
        0 0 15px;
}

.hero p {

    max-width:
        750px;

    font-size:
        18px;

    line-height:
        1.6;
}


/* PESQUISA */

.search {

    max-width:
        900px;

    background:
        white;

    padding:
        7px;

    border-radius:
        12px;

    display:
        flex;

    gap:
        7px;

    margin-top:
        25px;
}

.search input,
.search select {

    flex:
        1;

    min-width:
        0;

    padding:
        13px;

    border:
        none;

    outline:
        none;

    font-size:
        15px;
}

.search button {

    background:
        #ff8500;

    color:
        white;

    border:
        none;

    border-radius:
        9px;

    padding:
        0 20px;

    font-weight:
        bold;

    cursor:
        pointer;
}


/* CONTEÚDO */

main {

    max-width:
        1200px;

    margin:
        auto;

    padding:
        35px 20px 70px;
}

.section-header {

    display:
        flex;

    justify-content:
        space-between;

    align-items:
        center;

    margin-bottom:
        20px;
}


/* PRODUTOS */

.products {

    display:
        grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap:
        18px;
}

.product {

    background:
        white;

    border:
        1px solid #e5e0ea;

    border-radius:
        16px;

    overflow:
        hidden;

    transition:
        transform .2s,
        box-shadow .2s;
}

.product:hover {

    transform:
        translateY(-3px);

    box-shadow:
        0 8px 25px
        rgba(50,20,80,.1);
}

.product-image {

    width:
        100%;

    height:
        190px;

    object-fit:
        cover;
}

.product-placeholder {

    height:
        190px;

    display:
        flex;

    justify-content:
        center;

    align-items:
        center;

    background:
        #f1e8ff;

    font-size:
        60px;
}

.product-content {

    padding:
        16px;
}

.category {

    color:
        #6f2dbd;

    font-size:
        11px;

    font-weight:
        bold;

    text-transform:
        uppercase;
}

.product h3 {

    min-height:
        42px;
}

.price {

    color:
        #6f2dbd;

    font-size:
        21px;

    font-weight:
        900;
}

.info {

    color:
        #777;

    font-size:
        13px;
}


/* FORMULÁRIOS */

.form-card {

    max-width:
        650px;

    margin:
        20px auto;

    padding:
        30px;

    background:
        white;

    border:
        1px solid #e5e0ea;

    border-radius:
        18px;
}

.form {

    display:
        grid;

    gap:
        16px;
}

.form label {

    font-weight:
        bold;
}

.form input,
.form select,
.form textarea {

    width:
        100%;

    margin-top:
        6px;

    padding:
        12px;

    border:
        1px solid #ddd;

    border-radius:
        9px;

    font-size:
        15px;

    font-family:
        inherit;
}

.form textarea {

    resize:
        vertical;
}


/* DETALHES */

.detail {

    display:
        grid;

    grid-template-columns:
        1fr 1fr;

    gap:
        45px;
}

.detail-image {

    width:
        100%;

    max-height:
        550px;

    object-fit:
        contain;

    background:
        #f1e8ff;

    border-radius:
        18px;
}

.detail-placeholder {

    width:
        100%;

    height:
        450px;

    display:
        flex;

    justify-content:
        center;

    align-items:
        center;

    background:
        #f1e8ff;

    border-radius:
        18px;

    font-size:
        100px;
}

.detail h1 {

    font-size:
        38px;
}

.detail-price {

    color:
        #6f2dbd;

    font-size:
        34px;

    font-weight:
        900;
}

.seller {

    margin-top:
        25px;

    padding:
        20px;

    background:
        white;

    border:
        1px solid #ddd;

    border-radius:
        15px;
}


/* PERFIL */

.profile {

    max-width:
        800px;

    margin:
        auto;
}

.profile-box {

    background:
        white;

    padding:
        25px;

    border-radius:
        15px;

    border:
        1px solid #ddd;

    margin-bottom:
        25px;
}

.my-product {

    display:
        flex;

    justify-content:
        space-between;

    align-items:
        center;

    gap:
        15px;

    background:
        white;

    padding:
        15px;

    margin-bottom:
        10px;

    border:
        1px solid #ddd;

    border-radius:
        12px;
}

.delete {

    border:
        none;

    background:
        #d63031;

    color:
        white;

    padding:
        9px 12px;

    border-radius:
        8px;

    cursor:
        pointer;
}


/* MENSAGENS */

.messages {

    max-width:
        1000px;

    margin:
        15px auto;

    padding:
        0 15px;
}

.message {

    background:
        #e9f8ee;

    color:
        #17652c;

    padding:
        13px;

    border-radius:
        10px;
}


/* VAZIO */

.empty {

    text-align:
        center;

    background:
        white;

    border-radius:
        15px;

    padding:
        50px;

    grid-column:
        1 / -1;
}


/* FOOTER */

footer {

    background:
        #24113b;

    color:
        white;

    text-align:
        center;

    padding:
        35px 20px;
}


/* CELULAR */

@media (max-width: 950px) {

    .products {

        grid-template-columns:
            repeat(2, 1fr);
    }

    .detail {

        grid-template-columns:
            1fr;
    }
}


@media (max-width: 650px) {

    .navbar {

        flex-wrap:
            wrap;
    }

    .school {

        display:
            none;
    }

    nav {

        width:
            100%;

        justify-content:
            center;
    }

    .hero h1 {

        font-size:
            32px;
    }

    .search {

        flex-direction:
            column;
    }

    .search button {

        padding:
            13px;
    }

    .products {

        grid-template-columns:
            1fr;
    }

    .section-header {

        flex-direction:
            column;

        align-items:
            flex-start;

        gap:
            12px;
    }

    .detail h1 {

        font-size:
            30px;
    }

    .my-product {

        flex-direction:
            column;

        align-items:
            flex-start;
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

<title>
{{ titulo }}
</title>

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

<a
href="{{ url_for('index') }}"
>
Início
</a>


{% if session.get("usuario_id") %}

<a
href="{{ url_for('vender') }}"
>
Vender
</a>


<a
href="{{ url_for('perfil') }}"
>
Minha conta
</a>


<a
href="{{ url_for('logout') }}"
>
Sair
</a>


{% else %}

<a
href="{{ url_for('login') }}"
>
Entrar
</a>


<a
href="{{ url_for('cadastro') }}"
class="btn"
>
Criar conta
</a>

{% endif %}

</nav>

</div>

</header>


{% with messages =
get_flashed_messages() %}

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
Fardamentos, livros e materiais escolares
com preços acessíveis.
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

            ON produtos.usuario_id =
               usuarios.id

        WHERE 1 = 1

    """


    params = []


    if busca:

        query += """

            AND (

                produtos.nome LIKE ?

                OR

                produtos.descricao LIKE ?

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

        params.append(
            categoria
        )


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
                url_for("cadastro")
            )


        if len(senha) < 6:

            flash(
                "A senha precisa ter pelo menos 6 caracteres."
            )

            return redirect(
                url_for("cadastro")
            )


        db = get_db()


        try:

            db.execute(
                """

                INSERT INTO usuarios

                (
                    nome,
                    email,
                    senha,
                    contato
                )

                VALUES (?, ?, ?, ?)

                """,

                (
                    nome,
                    email,
                    generate_password_hash(
                        senha
                    ),
                    contato
                )
            )


            db.commit()


        except sqlite3.IntegrityError:

            db.close()


            flash(
                "Este e-mail já está cadastrado."
            )


            return redirect(
                url_for("cadastro")
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


        session["usuario_id"] = (
            usuario["id"]
        )


        session["usuario_nome"] = (
            usuario["nome"]
        )


        flash(
            "Conta criada com sucesso!"
        )


        return redirect(
            url_for("index")
        )


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
                        placeholder="88999999999"
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

            session["usuario_id"] = (
                usuario["id"]
            )


            session["usuario_nome"] = (
                usuario["nome"]
            )


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

                Ainda não possui uma conta?

                <a
                    href="/cadastro"
                    class="purple"
                >

                    Criar conta

                </a>

            </p>

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

    session.clear()

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


        if (
            not nome
            or not categoria
            or not preco_texto
        ):

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


        if (
            arquivo
            and
            arquivo.filename
        ):

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


            arquivo.save(
                caminho
            )


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

                Venda seu fardamento,
                livro ou material para
                outros alunos.

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

            ON produtos.usuario_id =
               usuarios.id

        WHERE produtos.id = ?

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

        (
            session["usuario_id"],
        )
    ).fetchone()


    produtos = db.execute(
        """

        SELECT *

        FROM produtos

        WHERE usuario_id = ?

        ORDER BY id DESC

        """,

        (
            session["usuario_id"],
        )
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


    conteudo = f"""

    <main>

        <div class="profile">

            <div class="profile-box">

                <h1>

                    Olá,
                    {usuario['nome']}
                    👋

                </h1>


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
# INICIALIZAÇÃO
# ============================================================

init_db()


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
