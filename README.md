# facetraka
virtual catraka opennable through face recognition

## Visão geral do projeto

**facetraka** é um sistema de “catraca virtual” que utiliza reconhecimento facial para controle de acesso. O objetivo é permitir que acesso (ex: entrada, liberação de portão/catraca) seja autorizado com base no reconhecimento do rosto de uma pessoa — ao invés de chave, crachá ou cartão.

* Tipo de projeto: software open-source.
* Licença: **MIT License**.
* Linguagens: o repositório utiliza majoritariamente **Python**, junto com **HTML**.
* Estrutura geral dividida em módulos: `client`, `recognizer`, `server`.

---

## Estrutura do repositório / Componentes

O repositório está organizado da seguinte forma: ([GitHub][1])

```
facetraka/
  ├── client/        ← parte cliente (o cliente para o servidor, o que vai no dispositivo IoT)
  ├── recognizer/    ← módulo responsável por reconhecimento facial sozinho (irrelevante para a apresentação)
  ├── server/        ← back-end / lógica de servidor, controle de dados / acesso
  └── README.md      ← documentação básica do projeto
```

## Como executar

### 📁 `client/`

- Copie o `.env.example` para `.env` e preencha o URL do servidor
- Execute `uv pip install -r requirements.txt`
- Rode com `uv run main.py`

### 📁 `server/`

- Execute `uv pip install -r requirements.txt`
- Rode com `uv run fastapi run main.py --port 8080`
- Acesse [http://localhost:8080/game/index.html](http://localhost:8080/game/index.html)
