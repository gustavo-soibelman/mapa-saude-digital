# Mapa de Experiências de Saúde Digital — CONASEMS e IdeiaSUS

Aplicação interativa para explorar experiências de saúde digital no Brasil, com dados do CONASEMS e IdeiaSUS.

🔗 **Acesse o mapa online:**  
(Adicione aqui o link gerado após deploy)

## Funcionalidades

- Filtros interativos por ano, região, estado, município e palavras-chave
- Visualização geográfica com marcadores dinâmicos
- Tooltip com título da experiência e palavras-chave
- Cache inteligente para acelerar carregamento

## Como rodar localmente

```bash
git clone https://github.com/seu-usuario/mapa-saude-digital.git
cd mapa-saude-digital
pip install -r requirements.txt
streamlit run app_mapa.py
