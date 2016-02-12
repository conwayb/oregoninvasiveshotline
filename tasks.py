import os
import posixpath
import shutil
from collections import defaultdict
from getpass import getpass
from urllib.parse import urlencode

from arctasks import *
from arctasks.django import call_command, setup, get_settings, manage


@arctask(configured='dev', timed=True)
def init(ctx, overwrite=False):
    virtualenv(ctx, overwrite=overwrite)
    install(ctx)
    createdb(ctx, drop=overwrite)
    migrate(ctx)
    rebuild_index(ctx, input=False)
    loaddata(ctx)
    generate_icons(ctx, clean=overwrite, input=False)


@arctask(configured='dev')
def loaddata(ctx):
    manage(ctx, (
        'loaddata',
        'dummy_user.json category.json severity.json counties.json pages.json',
    ))


@arctask(configured=DEFAULT_ENV)
def post_deploy(ctx):
    """A set of tasks that commonly needs to be run after deploying.

    This is pretty brutish and doesn't necessarily always need to be
    run. After we get out of the beta phase of this project, this can
    be removed.

    """
    copy_records(ctx, icons=False, reindex=False)
    copy_images(ctx)
    generate_icons(ctx, clean=True, input=False)
    rebuild_index(ctx, input=False)


@arctask(configured=DEFAULT_ENV)
def rebuild_index(ctx, input=True):
    call_command('rebuild_index', interactive=input)


@arctask(configured=DEFAULT_ENV)
def generate_icons(ctx, clean=False, force=False, input=True):
    call_command('generate_icons', clean=clean, force=force, interactive=input)


@arctask(configured=DEFAULT_ENV, timed=True)
def copy_records(ctx, recreate_db=False, icons=True, reindex=True):
    """Copy database records from old site.

    This is messy because only certain records are copied from the old
    site while others are loaded from fixtures.

    """
    settings = get_settings()

    password = getattr(settings, 'OLD_DATABASE_PASSWORD', None)
    if not password:
        password = getpass(
            'Old database password (get from '
            '/vol/www/invasivespecieshotline/invasivespecieshotline/config/database.yml): '
        )

    settings.DATABASES['old'] = {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': 'pgsql.rc.pdx.edu',
        'NAME': 'invhotline',
        'USER': 'invhotline_l',
        'PASSWORD': password,
    }

    # Disable real-time reindexing
    settings.HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.BaseSignalProcessor'

    setup()

    from django.db import connections
    from django.db.models.signals import post_save
    from django.contrib.auth import get_user_model
    from oregoninvasiveshotline.reports.models import Report, receiver__generate_icon

    # Keep icons from being generated on save
    post_save.disconnect(receiver__generate_icon, sender=Report)

    User = get_user_model()

    if recreate_db:
        createdb(ctx, drop=True)
        migrate(ctx)
        loaddata(ctx)

    _copy_records(settings)

    default = connections['default']

    print('Updating sequences...', end='')
    tables = (
        'category', 'comment', 'county', 'image', 'invite', 'notification', 'report', 'species',
        'user', 'user_notification_query',
    )
    statement = """
        SELECT setval(
            pg_get_serial_sequence('{table}', '{table}_id'),
            coalesce(max({table}_id), 0) + 1,
            false
        )
        FROM "{table}";
    """
    statements = ' '.join(statement.format(table=table) for table in tables)
    default.cursor().execute(statements)
    print('Done')

    print('Updating expert contact name...', end='')
    expert = User.objects.filter(first_name='EXPERT', last_name='CONTACT')
    expert.update(first_name='', last_name='')
    print('Done')

    if icons:
        generate_icons(ctx, clean=True, input=False)

    if reindex:
        rebuild_index(ctx, False)


def _copy_records(settings):
    import pytz
    from arcutils.db import dictfetchall
    from django.apps import apps
    from django.db import connections, transaction
    from django.contrib.auth import get_user_model

    old = connections['old'].cursor()
    tz = pytz.timezone(settings.TIME_ZONE)
    User = get_user_model()

    Comment = apps.get_model('comments', 'Comment')
    County = apps.get_model('counties', 'County')
    Image = apps.get_model('images', 'Image')
    Report = apps.get_model('reports', 'Report')
    Species = apps.get_model('species', 'Species')
    UserNotificationQuery = apps.get_model('notifications', 'UserNotificationQuery')

    user_id_map = {}
    report_submitter_user_id = {}
    key_to_user_id = {}

    @transaction.atomic
    def copy_species():
        print('Copying species...', end='', flush=True)
        old.execute("""
            SELECT id, category_id, severity_id, name_sci, name_comm, remedy, resources
            FROM issues
        """)
        species = []
        for row in dictfetchall(old):
            pk = row['id']
            data = {
                'category_id': row['category_id'],
                'name': row['name_comm'] or '',
                'remedy': row['remedy'] or '',
                'resources': row['resources'] or '',
                'scientific_name': row['name_sci'] or '',
                'severity_id': row['severity_id'],
            }
            if not Species.objects.filter(pk=pk).exists():
                species.append(Species(pk=pk, **data))
        if species:
            print('\n    New species:')
            for s in species:
                print('    ', s.name)
            Species.objects.bulk_create(species)
        print('Done')

    @transaction.atomic
    def copy_users():
        print('Copying users...', end='', flush=True)
        old.execute("""
            SELECT cardable_id, users.id AS user_id, affiliations, enabled, vcards.id, n_family,
                n_given, n_prefix, n_suffix, cardable_type, email, hashed_password
            FROM vcards
            LEFT JOIN users ON vcards.cardable_id = users.id AND cardable_type = 'User'
            ORDER BY cardable_type
        """)
        for row in dictfetchall(old):
            email = row['email']
            exists = User.objects.filter(email=email).exists()
            data = {
                'first_name': row['n_given'] or '',
                'last_name': row['n_family'] or '',
                'prefix': row['n_prefix'] or '',
                'suffix': row['n_suffix'] or '',
            }
            if not exists:
                # Only update these fields if the user wasn't already imported
                data.update({
                    'affiliations': row['affiliations'] or '',
                    'is_active': bool(row['enabled']),
                    'password': 'RubyPasswordHasher$0$${hashed_password}'.format(**row),
                })
            user, created = User.objects.update_or_create(email=email, defaults=data)
            user_id_map[row['user_id']] = user.pk
            if row['cardable_type'] == 'Submitter':
                report_submitter_user_id[row['cardable_id']] = user.pk
            key_to_user_id[(row['cardable_type'], row['cardable_id'])] = user.pk
        print('Done')

    @transaction.atomic
    def copy_reports():
        print('Copying reports...', end='', flush=True)
        staff_user = User.objects.filter(is_staff=True).first()
        edrr_status_map = {2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5}
        category_map = {
            5: 13,  # Aquatic Vertebrates => Reptiles and Amphibians
        }
        old.execute("""
            SELECT reports.id, category_id, issue_id, reported_category, reported_issue, has_sample,
                issue_desc, private_note, location_desc, reports.created_at, reports.updated_at,
                closed, user_id, edrr_status, lat, lng
            FROM reports
            LEFT JOIN locations
                ON locations.locateable_id = reports.id AND locateable_type = 'Report'
        """)
        for row in dictfetchall(old):
            pk = row['id']
            point = 'POINT({lng} {lat})'.format(**row)
            actual_species_id = row['issue_id']
            if not Species.objects.filter(pk=actual_species_id).exists():
                actual_species_id = None
            reported_species_id = row['reported_issue']
            if not Species.objects.filter(pk=reported_species_id).exists():
                reported_species_id = None
            created_on = tz.localize(row['created_at'])
            reported_category_id = row['reported_category']
            reported_category_id = category_map.get(reported_category_id, reported_category_id)
            data = {
                'actual_species_id': actual_species_id,
                'claimed_by_id': user_id_map[row['user_id']],
                'county': County.objects.filter(the_geom__intersects=point).first(),
                'created_by_id': report_submitter_user_id[row['id']],
                'created_on': created_on,
                'description': row['issue_desc'] or '',
                'edrr_status': edrr_status_map.get(row['edrr_status'], None),
                'has_specimen': row['has_sample'],
                'is_archived': bool(row['closed'] and not row['issue_id']),
                'is_public': bool(row['closed'] and row['issue_id']),
                'location': row['location_desc'] or '',
                'point': point,
                'reported_category_id': reported_category_id,
                'reported_species_id': reported_species_id,
            }
            report, created = Report.objects.update_or_create(pk=pk, defaults=data)
            if created:
                # Note: Setting created_on when creating Reports does
                # nothing; now is *always* used on creation when a field is
                # configured to use auto_now_add.
                report.created_on = created_on
                report.save()
            # Create a private comment for the private_note field; the PK
            # should be large to avoid colliding with the comments that are
            # imported later.
            if row['private_note']:
                pk = report.pk + 100000
                Comment.objects.update_or_create(pk=pk, defaults={
                    'body': row['private_note'],
                    'created_by': report.claimed_by or staff_user,
                    'created_on': tz.localize(row['created_at']),
                    'report_id': report.pk,
                    'visibility': Comment.PRIVATE,
                })
        print('Done')

    @transaction.atomic
    def copy_comments():
        print('Copying comments...', end='', flush=True)
        old.execute("""
            SELECT private, id, report_id, annotator_id, annotator_type, body, created_at
            FROM annotations
        """)
        for row in dictfetchall(old):
            pk = row['id']
            report_id = row['report_id']
            report = Report.objects.get(pk=report_id)
            if row['annotator_type'] == 'User':
                created_by_id = user_id_map[row['annotator_id']]
            elif row['annotator_type'] == 'Submitter':
                created_by_id = report.created_by_id
            elif row['annotator_type'] == 'Expert':
                created_by_id = key_to_user_id[(row['annotator_type'], row['annotator_id'])]
            else:
                created_by_id = report.created_by_id
            Comment.objects.update_or_create(pk=pk, defaults={
                'body': row['body'] or '',
                'created_by_id': created_by_id,
                'created_on': tz.localize(row['created_at']),
                'report_id': report_id,
                'visibility': Comment.PRIVATE if row['private'] else Comment.PUBLIC,
            })
        print('Done')

    @transaction.atomic
    def copy_images():
        print('Copying images...', end='', flush=True)
        old.execute("""
            SELECT id, imageable_id, imageable_type, filename, created_at, label
            FROM images
            WHERE imageable_type = 'Report'
        """)
        for row in dictfetchall(old):
            pk = row['id']
            image = posixpath.join('images', '{pk:04d}-{filename}'.format(pk=pk, **row))
            report_id = row['imageable_id']
            report = Report.objects.get(pk=report_id)
            Image.objects.update_or_create(pk=pk, defaults={
                'created_by_id': report.created_by_id,
                'created_on': tz.localize(row['created_at']),
                'image': image,
                'name': row['label'],
                'report': report,
                'visibility': Image.PUBLIC,
            })
        print('Done')

    @transaction.atomic
    def copy_user_notification_queries():
        print('Creating user notification queries...', flush=True)
        user_query_info = defaultdict(lambda: defaultdict(list))
        counties = County.objects.values()
        county_map = {c['name'].lower(): c['county_id'] for c in counties}
        print('    Removing existing notification queries...')
        UserNotificationQuery.objects.filter(name='Imported').delete()
        print('    Getting user categories...')
        old.execute("""
            SELECT user_id, category_id
            FROM categories_users
        """)
        for row in dictfetchall(old):
            user_id = user_id_map[row['user_id']]
            user_query_info[user_id]['categories'].append(row['category_id'])
        print('    Getting user counties...')
        old.execute("""
            SELECT user_id, label as county
            FROM regions_users
            INNER JOIN regions ON regions.id = region_id
        """)
        for row in dictfetchall(old):
            user_id = user_id_map[row['user_id']]
            if row['county'].lower() == 'hoodriver':
                row['county'] = 'Hood River'
            county = row['county'].lower()
            if county.endswith(' county, wa'):
                county = county[:-len(' county, wa')]
            if county in county_map:
                county_pk = county_map[county]
                user_query_info[user_id]['counties'].append(county_pk)
            else:
                print('    Unknown county: {county}'.format_map(row))
        print('    Adding notification query records...')
        for user_id, info in user_query_info.items():
            query = urlencode({
                'categories': info['categories'],
                'counties': info['counties'],
            }, doseq=True)
            UserNotificationQuery.objects.create(name='Imported', query=query, user_id=user_id)
        print('Done')

    copy_species()
    copy_users()
    copy_reports()
    copy_comments()
    copy_images()
    copy_user_notification_queries()


@arctask(configured=DEFAULT_ENV)
def copy_images(ctx, dry_run=False):
    """Copy images from old site."""
    settings = get_settings()
    src_dir = '/vol/www/invasivespecieshotline/invasivespecieshotline/public/uploads/images/0000'
    dest_dir = os.path.join(settings.MEDIA_ROOT, 'images')

    if os.path.exists(dest_dir):
        print('Destination image directory exists at', dest_dir)
    else:
        print('Creating destination image directory at', dest_dir)
        os.makedirs(dest_dir)

    src_files = []
    for dirpath, dirnames, filenames in os.walk(src_dir):
        paths = [os.path.join(dirpath, f) for f in filenames]
        paths = [os.path.relpath(p, src_dir) for p in paths]
        src_files.extend(paths)

    for src_file in src_files:
        src_path = os.path.join(src_dir, src_file)
        dest_path = os.path.join(dest_dir, src_file.replace(os.sep, '-'))
        print(src_path, '=>', dest_path)
        if not dry_run:
            shutil.copyfile(src_path, dest_path)
