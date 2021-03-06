rm -f db.sqlite3
rm -rf exao_dap/registrar/migrations/*
./manage.py makemigrations registrar
./manage.py migrate
./manage.py fake_registry
