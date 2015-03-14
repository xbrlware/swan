# Note we use a shell script because if the server is launched
# from Fabric stopping it leaves dead python processes around...
# export PYTHONPATH=~/workspace/lib/caffe/distribute/python
cd ~/code/swan/ && source env/bin/activate
# export PYTHONPATH=~/workspace/lib/caffe/distribute/python
# ipython notebook --ipython-dir=ipython --profile=default --script
# ipython notebook --ip='*' --script --no-browser --matplotlib inline --port 8888
ipython notebook --ip='*' --script --no-browser --port 8888
# THEANO_FLAGS=optimizer=fast_compile ipython notebook --matplotlib inline --profile=nbserver --script
