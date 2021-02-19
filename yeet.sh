rm db.sqlite3
rm exao_dap/registrar/migrations/*
./manage.py makemigrations registrar
./manage.py migrate
# ./manage.py createsuperuser --noinput --username admin --email example@example.com
./manage.py shell -c 'from django.contrib.auth.models import User; x,_=User.objects.get_or_create(username="admin", is_staff=True, is_superuser=True); x.set_password("admin"); x.save()'
./manage.py shell -c 'from django.contrib.auth.models import User; x,_=User.objects.get_or_create(username="user"); x.set_password("user"); x.save()'
./manage.py loaddata registrar_datasets.json
