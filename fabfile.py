import os
from fabric.api import local, lcd
from fabric.context_managers import shell_env

# Add caffe to python path so we can access deep learning library
pythonpath = os.getenv("PYTHONPATH", "") + "../../../lib/caffe/distribute/python"


def sync_data_from_getz():
    """ rsync the relevant data directories from getz """
    local("rsync -avz -e ssh"
          " rcurrie@getz.uaudio.com:/data/audio/apple/"
          " /data/audio/apple")


def run_web_server():
    """ Startup instrument detection web server in debug mode """
    with shell_env(PYTHONPATH=pythonpath):
        local("env/bin/activate && python server.py")


def update_dev_server():
    local("rsync -avz"
          " --exclude env"
          " --exclude uploads"
          " ./* /opt/ua/inst/")


def run_uwsgi():
    """ Run server using uwsgi with multiple process as its run on the production servers"""
    local("uwsgi -H env --py-auto-reload=1"
          " --processes 4 --enable-threads"
          " -w server --callable app --http 127.0.0.1:5000")


def run_cluster():
    """ Startup ipython compute cluster """
    with shell_env(PYTHONPATH=pythonpath):
        local("source env/bin/activate; ipcluster start -n 8")


def watch():
    """ Watch all coffee files in client and compile if changed """
    local("cd static && coffee -mcw *.coffee")


def test():
    local("curl -F 'file=@static/piano.wav' http://127.0.0.1:5000/predict")


def update_all_pip():
    local("pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs pip install -U")


def update_caffe():
    with lcd("../../../lib/caffe/"):
        local("git pull")
        local("pip install -r python/requirements.txt")
        local("make clean")
        local("make test")
        local("make runtest")
        local("make pycaffe")
        local("make distribute")


def train_quick():
    """ Run caffe training """
    with lcd("models"):
        local("GLOG_logtostderr=1"
              " ~/workspace/lib/caffe/distribute/bin/train_net.bin"
              " cqt_quick_solver.prototxt")
        local("GLOG_logtostderr=1"
              " ~/workspace/lib/caffe/distribute/bin/train_net.bin"
              " cqt_quick_solver_lr1.prototxt"
              " snapshots/cqt_quick_snap_iter_4000.solverstate")


def train_full():
    """ Run caffe training """
    with lcd("models"):
        local("GLOG_logtostderr=1"
              " ~/workspace/lib/caffe/distribute/bin/train_net.bin"
              " cqt_full_solver.prototxt")
        local("GLOG_logtostderr=1"
              " ~/workspace/lib/caffe/distribute/bin/train_net.bin"
              " cqt_full_solver_lr1.prototxt"
              " snapshots/cqt_full_iter_60000.solverstate")
        local("GLOG_logtostderr=1"
              " ~/workspace/lib/caffe/distribute/bin/train_net.bin"
              " cqt_full_solver_lr2.prototxt"
              " snapshots/cqt_full_iter_65000.solverstate")