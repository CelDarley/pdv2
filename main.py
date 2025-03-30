from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.relativelayout import RelativeLayout
import json
import os

# Dados dos produtos (pratos)
PRODUTOS = [
    {
        'id': 1,
        'nome': 'X-Burger',
        'preco': 25.90,
        'descricao': 'Hambúrguer com queijo, alface, tomate e molho especial',
        'imagem': 'assets/xburger.jpg'
    },
    {
        'id': 2,
        'nome': 'Pizza Margherita',
        'preco': 45.90,
        'descricao': 'Molho de tomate, mussarela, manjericão e azeite',
        'imagem': 'assets/pizza.jpg'
    },
    {
        'id': 3,
        'nome': 'Batata Frita',
        'preco': 15.90,
        'descricao': 'Batatas fritas crocantes com sal e temperos especiais',
        'imagem': 'assets/batata.jpg'
    }
]

class CardProduto(ButtonBehavior, BoxLayout):
    def __init__(self, produto, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(200)
        self.padding = dp(10)
        self.spacing = dp(5)
        
        # Imagem do produto
        self.imagem = Image(
            source=produto['imagem'],
            size_hint_y=0.7,
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Nome do produto
        self.nome = Label(
            text=produto['nome'],
            size_hint_y=0.15,
            font_size='16sp'
        )
        
        # Preço
        self.preco = Label(
            text=f"R$ {produto['preco']:.2f}",
            size_hint_y=0.15,
            font_size='14sp',
            color=(0, 0.7, 0, 1)  # Verde
        )
        
        self.add_widget(self.imagem)
        self.add_widget(self.nome)
        self.add_widget(self.preco)
        
        self.produto = produto
        self.bind(on_press=self.on_press)

    def on_press(self, instance):
        app = App.get_running_app()
        app.root.current = 'detalhes'
        app.root.get_screen('detalhes').carregar_produto(self.produto)

class TelaPrincipal(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        # Título
        self.titulo = Label(
            text='Cardápio',
            size_hint_y=0.1,
            font_size='24sp'
        )
        
        # Grid de produtos
        self.grid = GridLayout(
            cols=2,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=0.9,
            row_default_height=dp(200)
        )
        
        # ScrollView para o grid
        self.scroll = ScrollView()
        self.scroll.add_widget(self.grid)
        
        # Adiciona os cards dos produtos
        for produto in PRODUTOS:
            self.grid.add_widget(CardProduto(produto))
        
        self.layout.add_widget(self.titulo)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

class TelaDetalhes(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        # Botão voltar
        self.btn_voltar = Button(
            text='Voltar',
            size_hint_y=0.1,
            background_color=(0.8, 0.8, 0.8, 1)
        )
        self.btn_voltar.bind(on_press=self.voltar)
        
        # Container para detalhes
        self.detalhes = BoxLayout(orientation='vertical', padding=dp(20))
        
        # Imagem do produto
        self.imagem = Image(
            size_hint_y=0.4,
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Nome do produto
        self.nome = Label(
            font_size='24sp',
            size_hint_y=0.1
        )
        
        # Preço
        self.preco = Label(
            font_size='20sp',
            size_hint_y=0.1,
            color=(0, 0.7, 0, 1)
        )
        
        # Descrição
        self.descricao = Label(
            size_hint_y=0.2,
            text_size=(Window.width - dp(40), None)
        )
        
        # Container para quantidade
        self.quantidade_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.1,
            spacing=dp(10)
        )
        
        self.btn_diminuir = Button(
            text='-',
            size_hint_x=0.2,
            background_color=(0.8, 0.8, 0.8, 1)
        )
        self.btn_diminuir.bind(on_press=self.diminuir_quantidade)
        
        self.lbl_quantidade = Label(
            text='1',
            size_hint_x=0.6,
            font_size='20sp'
        )
        
        self.btn_aumentar = Button(
            text='+',
            size_hint_x=0.2,
            background_color=(0.8, 0.8, 0.8, 1)
        )
        self.btn_aumentar.bind(on_press=self.aumentar_quantidade)
        
        self.quantidade_layout.add_widget(self.btn_diminuir)
        self.quantidade_layout.add_widget(self.lbl_quantidade)
        self.quantidade_layout.add_widget(self.btn_aumentar)
        
        # Botão adicionar ao pedido
        self.btn_adicionar = Button(
            text='Adicionar ao Pedido',
            size_hint_y=0.1,
            background_color=(0, 0.7, 0, 1)
        )
        self.btn_adicionar.bind(on_press=self.adicionar_ao_pedido)
        
        # Adiciona widgets ao layout de detalhes
        self.detalhes.add_widget(self.imagem)
        self.detalhes.add_widget(self.nome)
        self.detalhes.add_widget(self.preco)
        self.detalhes.add_widget(self.descricao)
        self.detalhes.add_widget(self.quantidade_layout)
        self.detalhes.add_widget(self.btn_adicionar)
        
        # Adiciona widgets ao layout principal
        self.layout.add_widget(self.btn_voltar)
        self.layout.add_widget(self.detalhes)
        self.add_widget(self.layout)
        
        self.produto_atual = None
        self.quantidade = 1

    def carregar_produto(self, produto):
        self.produto_atual = produto
        self.imagem.source = produto['imagem']
        self.nome.text = produto['nome']
        self.preco.text = f"R$ {produto['preco']:.2f}"
        self.descricao.text = produto['descricao']
        self.quantidade = 1
        self.lbl_quantidade.text = '1'

    def aumentar_quantidade(self, instance):
        self.quantidade += 1
        self.lbl_quantidade.text = str(self.quantidade)

    def diminuir_quantidade(self, instance):
        if self.quantidade > 1:
            self.quantidade -= 1
            self.lbl_quantidade.text = str(self.quantidade)

    def adicionar_ao_pedido(self, instance):
        if self.produto_atual:
            # Aqui você pode implementar a lógica para adicionar ao pedido
            popup = Popup(
                title='Sucesso',
                content=Label(text=f'{self.quantidade}x {self.produto_atual["nome"]} adicionado ao pedido!'),
                size_hint=(None, None),
                size=(300, 200)
            )
            popup.open()

    def voltar(self, instance):
        self.parent.current = 'principal'

class RestauranteApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TelaPrincipal(name='principal'))
        sm.add_widget(TelaDetalhes(name='detalhes'))
        return sm

if __name__ == '__main__':
    RestauranteApp().run() 