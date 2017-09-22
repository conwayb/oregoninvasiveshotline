from django.conf import global_settings

from arcutils.settings import init_settings


def update_elasticsearch_options(settings):
    """
    Intelligently sets HTTP authentication when use of
    AWS Elasticsearch service is detected.
    """
    from requests_aws4auth import AWS4Auth
    import elasticsearch
    import boto3

    def get_elasticsearch_kwargs():
        elasticsearch_kwargs = {}

        if 'es.amazonaws.com' in settings['HAYSTACK_CONNECTIONS']['default']['URL']:
            session = boto3.session.Session(region_name='us-west-2')
            credentials = session.get_credentials()
            awsauth = AWS4Auth(
                credentials.access_key,
                credentials.secret_key,
                session.region_name,
                'es',
                session_token=credentials.token
            )

            elasticsearch_kwargs.update(
                http_auth=awsauth,
                connection_class=elasticsearch.RequestsHttpConnection,
            )

        return elasticsearch_kwargs

    settings['HAYSTACK_CONNECTIONS']['default']['KWARGS'] = get_elasticsearch_kwargs()


settings = init_settings(settings_processors=[update_elasticsearch_options])

PASSWORD_HASHERS = list(global_settings.PASSWORD_HASHERS)
PASSWORD_HASHERS.insert(1, 'oregoninvasiveshotline.utils.RubyPasswordHasher')
