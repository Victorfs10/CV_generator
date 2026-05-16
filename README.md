# Gerador de Currículos Profissionais

Sistema web para geração automatizada de currículos profissionais, desenvolvido como projeto integrador para a UNIVESP.

## Sobre

Permite que jovens em início de carreira preencham um formulário e gerem um currículo profissional em PDF de forma simples e estruturada. As descrições de experiência são organizadas automaticamente em tópicos via inteligência artificial.

## Funcionalidades

- Formulário com dados pessoais, formação acadêmica, experiências profissionais, habilidades e certificações
- Geração de PDF formatado e pronto para uso
- Organização automática das atividades em tópicos via OpenAI
- Campos dinâmicos (adicionar/remover experiências e formações)
- Máscara automática para telefone

## Tecnologias

- Python + Flask
- fpdf2 (geração de PDF)
- OpenAI API
- HTML + CSS + JavaScript

## Como rodar

1. Clone o repositório:
```bash
git clone https://github.com/Victorfs10/CV_generator.git
cd CV_generator
```

2. Crie o arquivo `.env` com sua chave da OpenAI:
```
OPENAI_API_KEY=sua_chave_aqui
```

3. Instale as dependências e rode:
```bash
uv sync
uv run python app.py
```

4. Acesse `http://127.0.0.1:5000` no navegador.

## Integrantes

- Jhonatas Lima Parra
- João Pedro de Oliveira Rodrigues
- João Pedro Nascimento Sales
- Victor França da Silva

**UNIVESP — PJI310 Projeto Integrador — 2026**
