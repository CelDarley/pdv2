# Sistema de Pedidos para Restaurante

Este é um sistema web para gerenciamento de pedidos em restaurantes, desenvolvido com Flask.

## Funcionalidades

- Visualização do cardápio com produtos e preços
- Detalhes de cada produto
- Carrinho de pedidos com controle de quantidade
- Finalização de pedidos

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/restaurante.git
cd restaurante
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
- Copie o arquivo `.env.example` para `.env`
- Edite o arquivo `.env` com suas configurações

## Executando a aplicação

1. Ative o ambiente virtual (se ainda não estiver ativo):
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Execute a aplicação:
```bash
python app.py
```

3. Acesse a aplicação no navegador:
```
http://localhost:5000
```

## Estrutura do Projeto

```
restaurante/
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências do projeto
├── .env               # Variáveis de ambiente
├── static/            # Arquivos estáticos
│   └── images/        # Imagens dos produtos
└── templates/         # Templates HTML
    ├── index.html     # Página inicial
    ├── detalhes.html  # Detalhes do produto
    └── carrinho.html  # Carrinho de pedidos
```

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 

sistema PVD

### Primeiro, clone o repositório:
~~~bash
 git clone https://github.com/CelDarley/pdv2.git
 cd pdv2
 ~~~

### Crie e ative um ambiente virtual:
~~~bash
python -m venv venv
source venv/bin/activate  # No Linux
venv\Scripts\activate  # No Windows
~~~
### Instale as dependências do projeto:
~~~bash
pip install django
pip install pillow
pip install django-crispy-forms
pip install crispy-bootstrap5
~~~
### Faça as migrações do banco de dados:
~~~bash
python manage.py makemigrations
python manage.py migrate
~~~
### Crie um superusuário para acessar o painel administrativo:
~~~bash
python manage.py createsuperuser
~~~
### Inicie o servidor:
~~~bash
python manage.py runserver
~~~
### Após executar estes comandos, o servidor estará rodando em http://127.0.0.1:8000/
