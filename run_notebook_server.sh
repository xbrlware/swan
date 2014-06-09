# Note we use a shell script because if the server is launched
# from Fabric stopping it leaves dead python processes around...
export PYTHONPATH=~/workspace/lib/caffe/distribute/python
ipython notebook --ipython-dir=ipython --profile=default --script
