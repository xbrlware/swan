from fabric.api import local, run, cd, env, abort, settings, hide, lcd

env.hosts = ["rcurrie@www.ampdat.com"]


def install_local():
    "Install required python packages in virtual env"
    local('source env/bin/activate && pip install -r requirements.txt')


def upgrade():
    """ Update all python packages with pip and update requirements """
    local("pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs pip install -U")
    local("pip freeze > requirements.txt")


def update_edgar_local():
    "Update parsed edgar files listed in default.csv"
    local("source env/bin/activate && python edgar.py")


def sync():
    local("rsync -avz --exclude 'env' -e ssh * %s:swan" % env.host)


def check():
    """ Check for PEP8 compliance, pip requirements and repository uncommitted/untracked files. """

    if local("pip freeze | diff - requirements.txt"):
        abort("pip freeze and requirements.txt differ")

    with settings(hide('warnings'), warn_only=True):
        local('pep8 --ignore=E501 --exclude=env .')

    with settings(hide('warnings'), warn_only=True):
        with(lcd('..')):
            local('pylint *.py --rcfile=pylint.conf --max-line-length=255 --reports=n')

    if local('git diff-index --exit-code HEAD --', capture=True):
        abort('Repository has uncommitted changes.')


def update_server():
    """ Update the server files """
    # run('cd swan;')
    with cd('~/swan'):
        run('git pull')
        run('source env/bin/activate && pip install -r requirements.txt')
