#!/bin/bash

echo "========================================="
echo "Build - Pacote .deb"
echo "========================================="
echo ""

VERSION="1.0.0"
ARCH="all"
PACKAGE_NAME="plantao-hospital"
BUILD_DIR="build-deb"

# Limpar builds anteriores
rm -rf "$BUILD_DIR" releases/*.deb

echo "Criando estrutura do pacote .deb..."
echo ""

# Criar estrutura de diretórios
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/opt/$PACKAGE_NAME"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/pixmaps"

# Copiar arquivos do aplicativo
cp main.py "$BUILD_DIR/opt/$PACKAGE_NAME/"
cp requirements.txt "$BUILD_DIR/opt/$PACKAGE_NAME/"
cp web.png "$BUILD_DIR/opt/$PACKAGE_NAME/"
cp web.png "$BUILD_DIR/usr/share/pixmaps/plantao-hospital.png"

# Criar script wrapper
cat > "$BUILD_DIR/opt/$PACKAGE_NAME/run.sh" << 'EOF'
#!/bin/bash

APP_DIR="/opt/plantao-hospital"
VENV_DIR="$HOME/.local/share/plantao-hospital/venv"

# Criar diretório de dados do usuário se não existir
mkdir -p "$HOME/.local/share/plantao-hospital"

# Verificar se o ambiente virtual existe
if [ ! -d "$VENV_DIR" ]; then
    echo "Primeira execução: configurando ambiente..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r "$APP_DIR/requirements.txt" > /dev/null 2>&1
    
    if [ $? -ne 0 ]; then
        zenity --error --text="Erro ao instalar dependências.\nVerifique se python3-venv está instalado:\nsudo apt install python3-venv" 2>/dev/null
        exit 1
    fi
fi

# Ativar ambiente virtual e executar
source "$VENV_DIR/bin/activate"

# Mudar para o diretório de dados do usuário
cd "$HOME/.local/share/plantao-hospital"

# Executar aplicativo
python3 "$APP_DIR/main.py"
EOF

chmod +x "$BUILD_DIR/opt/$PACKAGE_NAME/run.sh"

# Criar symlink em /usr/bin
cat > "$BUILD_DIR/usr/bin/$PACKAGE_NAME" << 'EOF'
#!/bin/bash
/opt/plantao-hospital/run.sh
EOF

chmod +x "$BUILD_DIR/usr/bin/$PACKAGE_NAME"

# Criar arquivo .desktop
cat > "$BUILD_DIR/usr/share/applications/$PACKAGE_NAME.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Escalas de Plantão
Comment=Sistema de gerenciamento de escalas hospitalares
Exec=/opt/plantao-hospital/run.sh
Icon=plantao-hospital
Terminal=false
Categories=Office;Medical;
Keywords=hospital;plantao;escala;medico;
EOF

# Criar arquivo de controle do .deb
cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: misc
Priority: optional
Architecture: $ARCH
Depends: python3 (>= 3.8), python3-venv, python3-pip
Maintainer: Arthur <seu-email@exemplo.com>
Description: Sistema de escalas de plantao hospitalar
 Aplicativo desktop para montar e acompanhar escalas de plantao.
 .
 Funcionalidades:
  - Interface grafica intuitiva (PyQt6)
  - Gera automaticamente o calendario do mes
  - Destaque para sexta, sabado e domingo
  - Exporta tabelas para PDF e PNG
  - Mantem historico local de escalas

EOF

# Criar script postinst (após instalação)
cat > "$BUILD_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

echo "Instalação do Plantão Hospital concluída!"
echo "Execute 'plantao-hospital' ou procure por 'Escalas de Plantão' no menu de aplicativos"

exit 0
EOF

chmod +x "$BUILD_DIR/DEBIAN/postinst"

# Criar script prerm (antes de remover)
cat > "$BUILD_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

# Aviso ao usuário
echo "Removendo Plantão Hospital..."
echo "Os dados do usuário em ~/.local/share/plantao-hospital serão preservados"

exit 0
EOF

chmod +x "$BUILD_DIR/DEBIAN/prerm"

# Construir o pacote .deb
echo "Construindo pacote .deb..."
mkdir -p releases
dpkg-deb --build "$BUILD_DIR" "releases/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Pacote .deb criado com sucesso!"
    echo ""
    echo "Localização: releases/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
    echo ""
    echo "Para testar localmente:"
    echo "  sudo dpkg -i releases/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
    echo ""
    echo "Para remover:"
    echo "  sudo apt remove $PACKAGE_NAME"
    echo ""
    echo "Para distribuir: faça upload do .deb para o GitHub Releases"
    echo ""
    
    # Limpar diretório de build
    rm -rf "$BUILD_DIR"
else
    echo ""
    echo "❌ Erro ao criar pacote .deb"
    exit 1
fi
