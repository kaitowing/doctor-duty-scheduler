# Sistema de Escalas de Plantão Hospitalar

![Ícone do Aplicativo](https://raw.githubusercontent.com/kaitowing/doctor-duty-scheduler/main/web.png)

Aplicativo desktop criado para facilitar a montagem das escalas de plantões hospitalares com interface amigável e exportações profissionais.

## Recursos

- Interface gráfica moderna e intuitiva (PyQt6)
- Geração automática da tabela mensal destacando finais de semana
- Preenchimento rápido dos turnos (Manhã, Tarde, Noite)
- Histórico local de escalas e reabertura de versões anteriores
- Exportação estilizada para PDF e PNG
- Pacote `.deb` pronto para instalação em distribuições baseadas em Debian/Ubuntu

## Instalação

```bash
sudo dpkg -i plantao-hospital_1.0.0_all.deb
sudo apt install -f  # caso falte alguma dependência
```

Após instalado, procure por **"Escalas de Plantão"** no menu do sistema ou execute `plantao-hospital` no terminal.
