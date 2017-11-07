from runcommands import command

from emcee.dev import commands as dev
from emcee.aws import commands as aws
from emcee.aws.deploy import AWSDeployer
from emcee.django import call_command

from emcee.aws.commands import *


@command(env='dev')
def loaddata(config):
    # XXX: Prevents difficult-to-diagnose name shadowing by
    #      tucking 'manage' in the local (function) scope.
    from emcee.django import manage

    manage(config, (
        'loaddata',
        'dummy_user.json category.json severity.json counties.json pages.json',
    ))


@command(env='dev', timed=True)
def init(config, overwrite=False):
    dev.virtualenv(config, config.venv, overwrite=overwrite)
    dev.install(config)
    dev.createdb(config, drop=overwrite, with_postgis=True)
    dev.migrate(config)
    dev.loaddata(config)
    call_command(config, 'rebuild_index', interactive=True)
    call_command(config, 'generate_icons', clean=False, force=False, interactive=True)
    dev.test(config, with_coverage=True, force_env='test')


class Deployer(AWSDeployer):
    def post_install(self):
        from emcee.remote import manage, rsync

        # Push media
        remote(self.config, ('mkdir', '-p', '{remote.path.media}'))
        rsync(self.config, 'media/*', self.config.remote.path.media)
        # Migrate database schema
        manage(self.config, 'migrate')
        # Rebuild search index
        manage(self.config, 'rebuild_index')
        # Generate icons
        manage(self.config, 'generate_icons')


@command(env=True)
def deploy_app(config, provision=False, createdb=False):
    if provision:
        aws.provision_webhost(config, with_gis=True)
    if createdb:
        aws.createdb(config, with_postgis=True)

    aws.deploy(config, deployer_class=Deployer)
