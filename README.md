# Design System Adapter

Um script Python para extrair automaticamente paletas de cores de logotipos e integrar com design systems existentes.

## Funcionalidades

- Extração de cores dominantes de imagens
- Geração de paletas de cores completas
- Mapeamento inteligente para variáveis SCSS existentes
- Análise de contraste para acessibilidade
- Visualização de paletas de cores

## Requisitos

- Python 3.6+
- OpenCV
- NumPy
- scikit-learn
- matplotlib
- colormath

## Instalação

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt