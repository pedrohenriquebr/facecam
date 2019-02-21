# Smarscripts

Esse repositório trata do código que estará rodando no raspberry Pi 3. Trabalha em conjunto com Web-face-recognition.

## Requisitos

* Linux (distro baseada no Debian)

## Guia de instalação

Clone o projeto e entre nele:

```console
$ git clone https://bitbucket.org/nupemteam/smarscripts.git
$ cd smarscripts/
```

Instale as dependências:

```console
$ ./bootstrap.sh
```

Esse script é responsável por instalar pacotes debian importantes para a execução do projeto, segue a lista:

* python3-pip
* python3-picamera
* wget
* python3-dev
* libmysqlclient-dev ou default-libmysqlclient-dev

Segue a lista de módulos Python que são instalados:

* certifi==2018.10.15
* mysqlclient==1.3.13
* numpy==1.15.0
* opencv-python==3.4.2.17
* Pillow==5.2.0
* python-dotenv==0.9.1
* requests==2.20.0
* scikit-learn==0.19.2
* scipy==1.1.0
* urllib3==1.24

Também é instalado a biblioteca Gson em formato JAR.
Além das dependências de bibliotecatecas, é criado o diretório `/smartroom_data` para armazenar dados do projeto,
será utilizado para salvar arquivos com dados importantes para monitoramento, arquivos de log, por exemplo.

Há suporte para usar tanto a webcam quanto ao módulo Pi Camera, contudo
o módulo Pi Camera é usado automaticamente quando detectado o Raspberry Pi.