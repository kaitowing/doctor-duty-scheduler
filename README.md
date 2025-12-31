# Sistema de Escalas de Plantão Hospitalar

Aplicativo desktop Linux para gerenciamento de escalas de plantões hospitalares.

## Recursos

- Interface gráfica moderna e intuitiva (PyQt6)
- Seleção de mês com geração automática de calendário
- Destaque visual para finais de semana
- Preenchimento fácil de médicos por turno (Manhã, Tarde, Noite)
- Exportação para PDF e PNG
- Histórico de escalas salvas localmente
- Visualização e edição de escalas anteriores

## Desenvolvimento

### Configurar Ambiente

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Executar

```bash
source venv/bin/activate
python3 main.py
```

### Build do Pacote .deb

```bash
./build.sh
```

O pacote será gerado em `releases/plantao-hospital_1.0.0_all.deb`

## Distribuição

O arquivo `.deb` gerado pode ser distribuído via GitHub Releases.

Usuários instalam com:
```bash
sudo dpkg -i plantao-hospital_1.0.0_all.deb
```

Ou executando o GitHub Actions workflow que faz o build e release automaticamente.
