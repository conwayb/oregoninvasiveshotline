from collections import defaultdict

from runcommands import DEFAULT_ENV, command
from runcommands.util import confirm, printer

from arctasks.aws.commands import *
from arctasks.aws.deploy import AWSDeployer
from arctasks.django import call_command, setup


@command(env='dev')
def loaddata(config):
    # XXX: Prevents difficult-to-diagnose name shadowing by
    #      tucking 'manage' in the local (function) scope.
    from arctasks.django import manage

    manage(config, (
        'loaddata',
        'dummy_user.json category.json severity.json counties.json pages.json',
    ))


@command(env='dev', timed=True)
def init(config, overwrite=False):
    virtualenv(config, config.venv, overwrite=overwrite)
    install(config)
    createdb(config, drop=overwrite, with_postgis=True)
    migrate(config)
    loaddata(config)
    call_command(config, 'rebuild_index', interactive=True)
    call_command(config, 'generate_icons', clean=False, force=False, interactive=True)
    test(config, with_coverage=True, force_env='test')


class Deployer(AWSDeployer):
    def post_install(self):
        from arctasks.remote import manage, rsync

        # Push media
        remote(config, ('mkdir', '-p', '{remote.path.media}'))
        rsync(config, 'media/*', config.remote.path.media)
        # Generate icons
        manage(config, 'generate_icons')
        # Migrate database schema
        manage(config, 'migrate')
        # Rebuild search index
        manage(config, 'rebuild_index')


@command(env=True)
def deploy_app(config, provision=False, createdb=False):
    if provision:
        provision_webhost(config, with_gis=True)
    if createdb:
        createdb_aws(config, with_postgis=True)

    deploy(config, deployer_class=Deployer)
