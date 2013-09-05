from fabric.api import sudo, local, run, cd, env, abort, settings, hide, lcd

env.hosts = ['rcurrie@www.ampdat.com']


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


def update_cloud():
    """ Update the server files """
    # run('cd swan;')
    with cd('~/swan'):
        run('git pull')
