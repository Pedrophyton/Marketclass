import os
import base64
import secrets
from functools import wraps

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
    render_template_string,
    send_file
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text,
    LargeBinary,
    DateTime,
    ForeignKey,
    func
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    relationship
)


# ============================================================
# MARKETCLASS
# EEEP JEOVÁ COSTA LIMA
#
# Marketplace de fardamentos e materiais escolares
# ============================================================


app = Flask(__name__)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "marketclass-secret-key-2026"
)


# Seu WhatsApp
ADMIN_WHATSAPP = "5584999502071"


# Senha do administrador.
#
# NO RENDER:
#
# ADMIN_PASSWORD=coloque-uma-senha-forte
#
ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "troque-esta-senha"
)


# ============================================================
# BANCO DE DADOS
# ============================================================

DATABASE_URL = os.environ.get(
    "DATABASE_URL"
)


# Render pode fornecer postgres://.
# O SQLAlchemy atual utiliza postgresql:// ou
# postgresql+psycopg2://.
if DATABASE_URL:

    if DATABASE_URL.startswith(
        "postgres://"
    ):

        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql+psycopg2://",
            1
        )

    elif DATABASE_URL.startswith(
        "postgresql://"
    ):

        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://",
            "postgresql+psycopg2://",
            1
        )

else:

    DATABASE_URL = "sqlite:///marketclass.db"


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False
)


Base = declarative_base()


# ============================================================
# MODELOS
# ============================================================

class Usuario(Base):

    __tablename__ = "usuarios"

    id = Column(
        Integer,
        primary_key=True
    )

    nome = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(200),
        unique=True,
        nullable=False
    )

    senha = Column(
        String(300),
        nullable=False
    )

    contato = Column(
        String(50),
        nullable=False
    )

    tipo = Column(
        String(20),
        nullable=False
    )

    aprovado = Column(
        Integer,
        default=0,
        nullable=False
    )

    criado_em = Column(
        DateTime,
        default=func.now()
    )

    produtos = relationship(
        "Produto",
        back_populates="vendedor",
        cascade="all, delete-orphan"
    )


class Produto(Base):

    __tablename__ = "produtos"

    id = Column(
        Integer,
        primary_key=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey(
            "usuarios.id"
        ),
        nullable=False
    )

    nome = Column(
        String(200),
        nullable=False
    )

    categoria = Column(
        String(100),
        nullable=False
    )

    preco = Column(
        Float,
        nullable=False
    )

    conservacao = Column(
        String(100),
        nullable=False
    )

    tamanho = Column(
        String(50)
    )

    descricao = Column(
        Text
    )

    imagem = Column(
        LargeBinary
    )

    imagem_tipo = Column(
        String(100)
    )

    criado_em = Column(
        DateTime,
        default=func.now()
    )

    vendedor = relationship(
        "Usuario",
        back_populates="produtos"
    )


# Criar tabelas
Base.metadata.create_all(
    engine
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def banco():

    return SessionLocal()


def usuario_atual():

    usuario_id = session.get(
        "usuario_id"
    )

    if not usuario_id:

        return None

    db = banco()

    usuario = db.get(
        Usuario,
        usuario_id
    )

    db.close()

    return usuario


def login_obrigatorio():

    if not session.get(
        "usuario_id"
    ):

        flash(
            "Você precisa entrar na sua conta."
        )

        return False

    return True


def vendedor_aprovado():

    usuario = usuario_atual()

    if not usuario:

        return False

    return (
        usuario.tipo == "vendedor"
        and
        usuario.aprovado == 1
    )


def formatar_preco(valor):

    return (
        f"{valor:.2f}"
        .replace(".", ",")
    )


def whatsapp_numero(numero):

    numero = (
        numero
        .replace(" ", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace("+", "")
    )

    if not numero.startswith("55"):

        numero = "55" + numero

    return numero


def whatsapp_link(numero):

    return (
        "https://wa.me/"
        + whatsapp_numero(numero)
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

    flex-wrap: wrap;
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

.green {

    background:
        #16803c;
}

.red {

    background:
        #d63031;
}

.gray {

    background:
        #666;
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


/* ABAS */

.tabs {

    display:
        flex;

    margin-bottom:
        25px;

    border-bottom:
        2px solid #eee;
}

.tab {

    flex:
        1;

    padding:
        14px;

    text-align:
        center;

    font-weight:
        bold;

    background:
        #f4f1f7;

    color:
        #666;
}

.tab.active {

    background:
        #6f2dbd;

    color:
        white;
}


/* AVISOS */

.notice {

    padding:
        18px;

    border-radius:
        12px;

    margin:
        15px 0;
}

.notice-yellow {

    background:
        #fff5d6;

    color:
        #765600;
}

.notice-green {

    background:
        #e9f8ee;

    color:
        #17652c;
}

.notice-red {

    background:
        #ffe9e9;

    color:
        #8a2020;
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
        850px;

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


/* ADMIN */

.admin-card {

    background:
        white;

    border:
        1px solid #ddd;

    border-radius:
        15px;

    padding:
        20px;

    margin-bottom:
        15px;
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

    .tabs {

        flex-direction:
            column;
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

<a href="{{ url_for('index') }}">
    Início
</a>

{% if session.get("usuario_id") %}

<a href="{{ url_for('perfil') }}">
    Minha conta
</a>

{% if session.get("tipo") == "vendedor" and session.get("aprovado") == 1 %}

<a
    href="{{ url_for('vender') }}"
    class="btn"
>
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
Fardamentos, livros e materiais escolares
com preços acessíveis.
</p>

</footer>

</body>

</html>

"""


def pagina(
    conteudo,
    titulo="MarketClass"
):

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


    db = banco()


    query = db.query(
        Produto
    ).join(
        Usuario
    ).filter(
        Usuario.tipo == "vendedor",
        Usuario.aprovado == 1
    )


    if busca:

        termo = f"%{busca}%"

        query = query.filter(
            Produto.nome.ilike(termo)
            |
            Produto.descricao.ilike(termo)
        )


    if categoria:

        query = query.filter(
            Produto.categoria ==
            categoria
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
                alt="Produto"
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
                " • Tamanho "
                + produto.tamanho
            )


        preco = formatar_preco(
            produto.preco
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
                    R$ {preco}
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
                Ainda não existem anúncios publicados.
            </p>

            <a
                href="/cadastro"
                class="btn orange"
            >
                Criar conta
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
                Encontre fardamentos, livros,
                mochilas e materiais escolares
                com preços acessíveis.
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
                href="/cadastro?tipo=vendedor"
            >
                + Quero vender
            </a>

        </div>

        <div class="products">

            {cards}

        </div>

    </main>

    """


    db.close()


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

    tipo_inicial = request.args.get(
        "tipo",
        "comprador"
    )


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


        db = banco()


        existente = db.query(
            Usuario
        ).filter(
            Usuario.email == email
        ).first()


        if existente:

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


        # Compradores entram imediatamente.
        #
        # Vendedores ficam pendentes.
        if tipo == "comprador":

            aprovado = 1

        else:

            aprovado = 0


        usuario = Usuario(

            nome=nome,

            email=email,

            senha=generate_password_hash(
                senha
            ),

            contato=contato,

            tipo=tipo,

            aprovado=aprovado

        )


        db.add(usuario)

        db.commit()

        usuario_id = usuario.id

        db.close()


        # ----------------------------------------------------
        # COMPRADOR
        # ----------------------------------------------------

        if tipo == "comprador":

            session["usuario_id"] = (
                usuario_id
            )

            session["usuario_nome"] = nome

            session["tipo"] = (
                "comprador"
            )

            session["aprovado"] = 1


            flash(
                "Conta de comprador criada com sucesso!"
            )


            return redirect(
                url_for("index")
            )


        # ----------------------------------------------------
        # VENDEDOR
        # ----------------------------------------------------

        mensagem = (
            "Olá! Solicitação de aprovação "
            "para vender no MarketClass.%0A%0A"
            "Nome: "
            + nome
            + "%0A"
            "E-mail: "
            + email
            + "%0A"
            "Contato: "
            + contato
        )


        link_admin = (
            "https://wa.me/"
            + ADMIN_WHATSAPP
            + "?text="
            + mensagem
        )


        conteudo = f"""

        <main>

            <div class="form-card">

                <h1>
                    Solicitação enviada!
                </h1>

                <div class="notice notice-yellow">

                    <strong>
                        Sua conta de vendedor está
                        aguardando aprovação.
                    </strong>

                    <p>
                        Para poder publicar anúncios,
                        você precisa ser aprovado pelo
                        responsável do MarketClass.
                    </p>

                </div>

                <p>
                    Entre em contato pelo WhatsApp
                    oficial para solicitar sua aprovação.
                </p>

                <a
                    href="{link_admin}"
                    target="_blank"
                    class="btn orange"
                >
                    Solicitar aprovação pelo WhatsApp
                </a>

                <br><br>

                <a
                    href="/login"
                    class="purple"
                >
                    Já tenho uma conta
                </a>

            </div>

        </main>

        """


        return pagina(
            conteudo,
            "Aguardando aprovação — MarketClass"
        )


    # ========================================================
    # FORMULÁRIO DE CADASTRO
    # ========================================================

    vendedor_active = (
        tipo_inicial == "vendedor"
    )


    conteudo = f"""

    <main>

        <div class="form-card">

            <h1>
                Criar conta
            </h1>

            <p>
                Escolha como você deseja usar
                o MarketClass.
            </p>


            <div class="tabs">

                <a
                    href="/cadastro?tipo=comprador"
                    class="tab
                    {'active' if not vendedor_active else ''}"
                >
                    👤 Comprador
                </a>

                <a
                    href="/cadastro?tipo=vendedor"
                    class="tab
                    {'active' if vendedor_active else ''}"
                >
                    🏪 Vendedor
                </a>

            </div>


            <form
                method="POST"
                class="form"
            >

                <input
                    type="hidden"
                    name="tipo"
                    value="{
                        'vendedor'
                        if vendedor_active
                        else 'comprador'
                    }"
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
                        placeholder="(84) 99999-9999"
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


            {
                '''
                <div class="notice notice-yellow">
                    <strong>
                        Atenção:
                    </strong>

                    <p>
                        Contas de vendedor precisam
                        ser aprovadas pelo responsável
                        antes de poderem publicar anúncios.
                    </p>
                </div>
                '''
                if vendedor_active
                else
                '''
                <div class="notice notice-green">
                    Você poderá entrar imediatamente
                    como comprador.
                </div>
                '''
            }


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


        db = banco()


        usuario = db.query(
            Usuario
        ).filter(
            Usuario.email == email
        ).first()


        db.close()


        if (
            usuario
            and
            check_password_hash(
                usuario.senha,
                senha
            )
        ):

            session["usuario_id"] = (
                usuario.id
            )

            session["usuario_nome"] = (
                usuario.nome
            )

            session["tipo"] = (
                usuario.tipo
            )

            session["aprovado"] = (
                usuario.aprovado
            )


            if (
                usuario.tipo == "vendedor"
                and
                usuario.aprovado == 0
            ):

                flash(
                    "Sua conta de vendedor ainda está aguardando aprovação."
                )

            else:

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

    if not login_obrigatorio():

        return redirect(
            url_for("login")
        )


    usuario = usuario_atual()


    if (
        not usuario
        or
        usuario.tipo != "vendedor"
    ):

        flash(
            "Somente contas de vendedor podem publicar anúncios."
        )

        return redirect(
            url_for("index")
        )


    if usuario.aprovado != 1:

        flash(
            "Sua conta de vendedor ainda não foi aprovada."
        )

        return redirect(
            url_for("index")
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


        if not nome or not categoria:

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

        imagem_tipo = None


        arquivo = request.files.get(
            "imagem"
        )


        if arquivo and arquivo.filename:

            dados = arquivo.read()


            if len(dados) > 5 * 1024 * 1024:

                flash(
                    "A imagem deve ter no máximo 5 MB."
                )

                return redirect(
                    url_for("vender")
                )


            tipos_permitidos = [

                "image/png",

                "image/jpeg",

                "image/webp"

            ]


            if arquivo.mimetype not in tipos_permitidos:

                flash(
                    "Use uma imagem JPG, PNG ou WEBP."
                )

                return redirect(
                    url_for("vender")
                )


            imagem = dados

            imagem_tipo = arquivo.mimetype


        db = banco()


        produto = Produto(

            usuario_id=usuario.id,

            nome=nome,

            categoria=categoria,

            preco=preco,

            conservacao=conservacao,

            tamanho=tamanho,

            descricao=descricao,

            imagem=imagem,

            imagem_tipo=imagem_tipo

        )


        db.add(produto)

        db.commit()

        db.close()


        flash(
            "Produto anunciado com sucesso! Agora ele está visível para os outros usuários."
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

            <div class="notice notice-green">

                <strong>
                    Você está autorizado a vender.
                </strong>

                <p>
                    Depois de publicar, seu anúncio
                    ficará disponível para os usuários
                    do MarketClass.
                </p>

            </div>


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

                        <option value="">
                            Escolha uma categoria
                        </option>

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
# IMAGEM DO PRODUTO
# ============================================================

@app.route(
    "/imagem/<int:produto_id>"
)
def imagem_produto(produto_id):

    db = banco()


    produto = db.get(
        Produto,
        produto_id
    )


    if not produto or not produto.imagem:

        db.close()

        abort(404)


    dados = produto.imagem

    tipo = (
        produto.imagem_tipo
        or
        "image/jpeg"
    )


    db.close()


    from io import BytesIO


    return send_file(
        BytesIO(dados),
        mimetype=tipo
    )


# ============================================================
# DETALHES DO PRODUTO
# ============================================================

@app.route(
    "/produto/<int:produto_id>"
)
def produto(produto_id):

    db = banco()


    item = db.get(
        Produto,
        produto_id
    )


    if not item:

        db.close()

        abort(404)


    vendedor = db.get(
        Usuario,
        item.usuario_id
    )


    if (
        not vendedor
        or
        vendedor.tipo != "vendedor"
        or
        vendedor.aprovado != 1
    ):

        db.close()

        abort(404)


    preco = formatar_preco(
        item.preco
    )


    if item.imagem:

        imagem = f"""

        <img
            src="/imagem/{item.id}"
            class="detail-image"
            alt="Produto"
        >

        """

    else:

        imagem = """

        <div class="detail-placeholder">
            📦
        </div>

        """


    tamanho = ""


    if item.tamanho:

        tamanho = f"""

        <p>

            <strong>
                Tamanho:
            </strong>

            {item.tamanho}

        </p>

        """


    contato = whatsapp_numero(
        vendedor.contato
    )


    link_whatsapp = (
        "https://wa.me/"
        + contato
        + "?text="
        + "Olá! Vi seu anúncio no MarketClass."
    )


    conteudo = f"""

    <main>

        <div class="detail">

            <div>

                {imagem}

            </div>


            <div>

                <span class="category">
                    {item.categoria}
                </span>


                <h1>
                    {item.nome}
                </h1>


                <div class="detail-price">
                    R$ {preco}
                </div>


                <p>

                    <strong>
                        Estado:
                    </strong>

                    {item.conservacao}

                </p>


                {tamanho}


                <p>

                    <strong>
                        Descrição:
                    </strong>

                </p>


                <p>

                    {item.descricao
                    or
                    "Nenhuma descrição informada."}

                </p>


                <div class="seller">

                    <h3>
                        Vendedor
                    </h3>


                    <p>

                        <strong>
                            {vendedor.nome}
                        </strong>

                    </p>


                    <p>
                        Contato:
                        {vendedor.contato}
                    </p>


                    <a
                        class="btn orange"
                        target="_blank"
                        href="{link_whatsapp}"
                    >
                        💬 Conversar pelo WhatsApp
                    </a>

                </div>

            </div>

        </div>

    </main>

    """


    db.close()


    return pagina(
        conteudo,
        f"{item.nome} — MarketClass"
    )


# ============================================================
# PERFIL
# ============================================================

@app.route("/perfil")
def perfil():

    if not login_obrigatorio():

        return redirect(
            url_for("login")
        )


    usuario = usuario_atual()


    if not usuario:

        session.clear()

        return redirect(
            url_for("login")
        )


    db = banco()


    produtos = db.query(
        Produto
    ).filter(
        Produto.usuario_id ==
        usuario.id
    ).order_by(
        Produto.id.desc()
    ).all()


    db.close()


    anuncios = ""


    for produto in produtos:

        preco = formatar_preco(
            produto.preco
        )


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
                    R$ {preco}
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
                        type="submit"
                        class="btn red"
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


    if (
        usuario.tipo == "vendedor"
        and
        usuario.aprovado == 0
    ):

        status = """

        <div class="notice notice-yellow">

            <strong>
                ⏳ Vendedor aguardando aprovação
            </strong>

            <p>
                Você ainda não pode publicar
                produtos. Aguarde a aprovação
                do responsável.
            </p>

            <a
                href="https://wa.me/5584999502071"
                target="_blank"
                class="btn orange"
            >
                Falar com o responsável
            </a>

        </div>

        """

    elif (
        usuario.tipo == "vendedor"
        and
        usuario.aprovado == 1
    ):

        status = """

        <div class="notice notice-green">

            <strong>
                ✅ Vendedor aprovado
            </strong>

            <p>
                Você pode publicar anúncios.
            </p>

        </div>

        """

    else:

        status = """

        <div class="notice notice-green">

            <strong>
                👤 Conta de comprador
            </strong>

            <p>
                Você pode visualizar os anúncios
                e entrar em contato com vendedores.
            </p>

        </div>

        """


    botao_vender = ""


    if (
        usuario.tipo == "vendedor"
        and
        usuario.aprovado == 1
    ):

        botao_vender = """

        <a
            href="/vender"
            class="btn orange"
        >
            + Novo anúncio
        </a>

        """


    conteudo = f"""

    <main>

        <div class="profile">

            <div class="profile-box">

                <h1>
                    Olá, {usuario.nome} 👋
                </h1>


                {status}


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


                {botao_vender}

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

    if not login_obrigatorio():

        return redirect(
            url_for("login")
        )


    usuario = usuario_atual()


    if not usuario:

        return redirect(
            url_for("login")
        )


    db = banco()


    produto = db.query(
        Produto
    ).filter(
        Produto.id == produto_id,
        Produto.usuario_id == usuario.id
    ).first()


    if produto:

        db.delete(
            produto
        )

        db.commit()


        flash(
            "Produto excluído com sucesso."
        )


    db.close()


    return redirect(
        url_for("perfil")
    )


# ============================================================
# ÁREA ADMINISTRATIVA
# ============================================================

@app.route(
    "/admin",
    methods=["GET", "POST"]
)
def admin():

    if request.method == "POST":

        senha = request.form.get(
            "senha",
            ""
        )


        if secrets.compare_digest(
            senha,
            ADMIN_PASSWORD
        ):

            session["admin"] = True

            return redirect(
                url_for("admin")
            )


        flash(
            "Senha administrativa incorreta."
        )


    if not session.get("admin"):

        conteudo = """

        <main>

            <div class="form-card">

                <h1>
                    Área administrativa
                </h1>

                <p>
                    Somente o responsável pelo
                    MarketClass deve acessar esta área.
                </p>


                <form
                    method="POST"
                    class="form"
                >

                    <label>

                        Senha administrativa

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

            </div>

        </main>

        """


        return pagina(
            conteudo,
            "Admin — MarketClass"
        )


    db = banco()


    vendedores = db.query(
        Usuario
    ).filter(
        Usuario.tipo == "vendedor"
    ).order_by(
        Usuario.id.desc()
    ).all()


    conteudo = """

    <main>

        <h1>
            Aprovação de vendedores
        </h1>

        <p>
            Aqui você decide quem pode vender
            no MarketClass.
        </p>

    """


    if not vendedores:

        conteudo += """

        <div class="empty">

            <h3>
                Nenhum vendedor cadastrado.
            </h3>

        </div>

        """


    for vendedor in vendedores:

        if vendedor.aprovado == 1:

            status = """

            <div class="notice notice-green">

                ✅ Vendedor aprovado

            </div>

            """

            acao = f"""

            <form
                method="POST"
                action="/admin/reprovar/{vendedor.id}"
                style="display:inline"
            >

                <button
                    class="btn red"
                    type="submit"
                >
                    Bloquear vendedor
                </button>

            </form>

            """

        else:

            status = """

            <div class="notice notice-yellow">

                ⏳ Aguardando aprovação

            </div>

            """

            acao = f"""

            <form
                method="POST"
                action="/admin/aprovar/{vendedor.id}"
                style="display:inline"
            >

                <button
                    class="btn green"
                    type="submit"
                >
                    ✅ Aprovar vendedor
                </button>

            </form>

            """


        conteudo += f"""

        <div class="admin-card">

            <h2>
                {vendedor.nome}
            </h2>

            <p>
                <strong>
                    E-mail:
                </strong>
                {vendedor.email}
            </p>

            <p>
                <strong>
                    WhatsApp:
                </strong>
                {vendedor.contato}
            </p>

            {status}

            {acao}

            <a
                href="https://wa.me/{whatsapp_numero(vendedor.contato)}"
                target="_blank"
                class="btn"
            >
                WhatsApp
            </a>

        </div>

        """


    conteudo += """

    <br>

    <a
        href="/admin/logout"
        class="btn gray"
    >
        Sair da área administrativa
    </a>

    </main>

    """


    db.close()


    return pagina(
        conteudo,
        "Admin — MarketClass"
    )


# ============================================================
# APROVAR VENDEDOR
# ============================================================

@app.route(
    "/admin/aprovar/<int:usuario_id>",
    methods=["POST"]
)
def aprovar_vendedor(usuario_id):

    if not session.get("admin"):

        abort(403)


    db = banco()


    usuario = db.get(
        Usuario,
        usuario_id
    )


    if usuario and usuario.tipo == "vendedor":

        usuario.aprovado = 1

        db.commit()


        flash(
            f"{usuario.nome} foi aprovado para vender."
        )


    db.close()


    return redirect(
        url_for("admin")
    )


# ============================================================
# REPROVAR / BLOQUEAR VENDEDOR
# ============================================================

@app.route(
    "/admin/reprovar/<int:usuario_id>",
    methods=["POST"]
)
def reprovar_vendedor(usuario_id):

    if not session.get("admin"):

        abort(403)


    db = banco()


    usuario = db.get(
        Usuario,
        usuario_id
    )


    if usuario and usuario.tipo == "vendedor":

        usuario.aprovado = 0

        db.commit()


        flash(
            f"{usuario.nome} foi bloqueado."
        )


    db.close()


    return redirect(
        url_for("admin")
    )


# ============================================================
# LOGOUT ADMIN
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin",
        None
    )

    return redirect(
        url_for("index")
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return "MarketClass funcionando!"


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
        port=port,
        debug=False
    )
