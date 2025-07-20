#!/bin/bash

echo "🔧 Solucionando problema de permisos PostgreSQL..."

# Conectar como usuario postgres y configurar permisos
sudo -u postgres psql << EOF
-- Conectar a la base de datos security_corp
\c security_corp;

-- Dar permisos completos al usuario en el esquema public
GRANT ALL PRIVILEGES ON SCHEMA public TO security_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO security_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO security_user;

-- Dar permisos para crear objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO security_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO security_user;

-- Hacer al usuario propietario de la base de datos
ALTER DATABASE security_corp OWNER TO security_user;

-- Salir
\q
EOF

echo "✅ Permisos de PostgreSQL configurados correctamente"
