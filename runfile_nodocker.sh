# a shell file to run the whole pipeline without docker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python mybot.py

celery -A worker.celery_app worker -l info --without-gossip --without-mingle --without-heartbeat


