from fabric.api import local


def train():
    local("jupyter nbconvert --to script train.ipynb")
    local("THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 ipython train.py")
