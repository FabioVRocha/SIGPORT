# Empacotando o SIGPORT para Android com Cordova

Este guia explica como criar um APK simples que carrega a interface web do SIGPORT em um WebView usando o Apache Cordova.

## 1. Preparar o backend

1. Instale as dependências Python (`pip install -r requirements.txt`).
2. Configure a variável `DATABASE_URI` em `config.py` ou via ambiente.
3. Execute o servidor Flask normalmente:

```bash
python app.py
```

Garanta que o servidor esteja acessível pela rede (por exemplo, `http://192.168.0.10:5000`).

## 2. Instalar o Cordova

1. Instale [Node.js](https://nodejs.org/) (versão LTS recomendada).
2. Instale o Cordova globalmente:

```bash
npm install -g cordova
```

## 3. Criar o projeto Cordova

```bash
cordova create sigport_mobile com.example.sigport SIGPORT
cd sigport_mobile
cordova platform add android
```

## 4. Configurar o WebView

Edite o arquivo `config.xml` gerado na pasta `sigport_mobile` e defina a URL do backend:

```xml
<content src="http://192.168.0.10:5000/" />
<allow-navigation href="http://192.168.0.10:5000/*" />
```

Adicione o plugin de whitelist para permitir conexões externas:

```bash
cordova plugin add cordova-plugin-whitelist
```

No arquivo `config.xml`, habilite a política de acesso geral:

```xml
<access origin="*" />
```

## 5. Gerar o APK

Conecte um dispositivo ou configure um emulador Android. Em seguida execute:

```bash
cordova build android
```

O APK será gerado em `sigport_mobile/platforms/android/app/build/outputs/apk/`.
Instale-o no dispositivo para testar a interface web do SIGPORT via WebView.

## Observações

- O backend Flask deve permanecer em execução e acessível pela rede enquanto o aplicativo estiver sendo usado.
- Para distribuição pública, considere proteger a API com HTTPS e autenticação adequada.
