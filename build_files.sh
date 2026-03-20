
echo "BUILD START"
python3 -m pip install -r requirements.txt
python3 -m manage.py collectstatic --noinput  --clear
python3 -m pip install django
echo "BUILD END"