import kivy
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from function import buscar_dados_cliente
import requests
import json

kivy.require('2.0.0')
Window.size = (350, 580)
class InputScreen(BoxLayout):

    def limit_text_length_cs(self, instance, value):
        if len(value) > self.max_length_cs:
            instance.text = value[:self.max_length_cs]

    def limit_text_length_tqs(self, instance, value):
        if len(value) > self.max_length_tqs:
            instance.text = value[:self.max_length_tqs]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        self.max_length_cs = 7
        self.max_length_tqs = 2

        # Inserir o codigo SAP
        self.label_titulo1 = Label(text="Código SAP")
        self.add_widget(self.label_titulo1)
        self.text_input1 = TextInput(input_filter='int',hint_text="...",multiline=False)
        self.text_input1.bind(text=self.limit_text_length_cs)
        self.add_widget(self.text_input1)

        # Retorno das informações do cliente

        self.botao_buscar = Button(text="Buscar cliente")
        self.razao_social_label = Label(text=f"Razão Social: ")
        self.endereco_label = Label(text=f"Endereço: ")
        self.nome_fantasia_label = Label(text=f"Nome Fantasia: ")
        self.botao_buscar.bind(on_press=self.realizar_busca)
        self.add_widget(self.botao_buscar)
        self.add_widget(self.razao_social_label)  
        self.add_widget(self.nome_fantasia_label)  
        self.add_widget(self.endereco_label)
            

        # Caixa de texto para colocar a data
        self.label_titulo3 = Label(text="Data de recolhimento")
        self.add_widget(self.label_titulo3)
        self.text_input3 = TextInput(hint_text="...")
        self.add_widget(self.text_input3)

        # Caixa de texto para informar a quantidade de tanques
        self.label_titulo4 = Label(text="Quantidade de tanques")
        self.add_widget(self.label_titulo4)
        self.text_qntdetanques = TextInput(input_filter='int')
        self.text_qntdetanques.bind(text=self.limit_text_length_tqs)
        self.add_widget(self.text_qntdetanques)

        # Caixa para pergunta, recolhido a telemetria?  

        self.flag_telemetria = Spinner(
            text='Sim ou Não',
            values=('Sim', 'Não'),
            size_hint=(1, None),
            height=22
        )
        self.flag_label = Label(text="Recolhido com telemetria: ")
        self.add_widget(self.flag_label)
        self.add_widget(self.flag_telemetria)

        # Botão de envio
        self.send_button = Button(text="Registrar ordem de retirada ")
        self.send_button.bind(on_press=self.send_user_input_to_firebase)
        self.add_widget(self.send_button)

        # Label para feedback
        self.feedback_label = Label(text="")
        self.add_widget(self.feedback_label)

    def realizar_busca(self, instance):
        codigo = self.text_input1.text
        dados_cliente = buscar_dados_cliente(int(codigo))

        if dados_cliente == "Cliente não encontrado":
            self.razao_social_label.text = "Cliente não encontrado"
            self.endereco_label.text = ""
            self.nome_fantasia_label.text = ""
        elif isinstance(dados_cliente, dict):
            self.razao_social_label.text = dados_cliente['razao_social']
            self.endereco_label.text = dados_cliente['endereco_do_cliente']
            self.nome_fantasia_label.text = dados_cliente['nome_da_oportunidade']

    def send_user_input_to_firebase(self, instance):
        valor1 = self.text_input1.text
        valor2 = self.razao_social_label.text
        valor3 = self.endereco_label.text
        valor4 = self.text_qntdetanques.text
        valor5 = self.flag_telemetria.text
        # Crie um dicionário com os dados que você quer enviar
        data_to_send = { "Código SAP": valor1,
                         "Razão Social": valor2,
                         "Endereço": valor3,
                         "Quantidade de tanques recolhido":valor4,
                         "Recolhido com telemetria":valor5
                         }
        json_data = json.dumps(data_to_send)

        # Conectar com o firebase
        firebase_url = "https://projeto-retiradas-default-rtdb.firebaseio.com/.json"

        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(firebase_url, data=json_data, headers=headers)
            response.raise_for_status()
            self.feedback_label.text = f"Dados enviados com sucesso! Resposta: {response.json()}"
            self.text_input1.text = "" # Limpa a caixa de texto após o envio
            self.text_input3.text = "" # Limpa a terceira caixa de texto
            self.text_qntdetanques.text = "" # Limpa a quarta caixa de texto
        except requests.exceptions.RequestException as e:
            self.feedback_label.text = f"Erro ao enviar para o Firebase: {e}"

class MyApp(App):
    def build(self):
        return InputScreen()

if __name__ == '__main__':
    MyApp().run()
