import numpy as np
import os
import pandas as pd

from db_tools.ezfuncs import query
from db_tools.mysqlapis import MySQLEngine
from db_tools.query_tools import make_sql_obj

from epic_viz import epi_calls
from epic_viz import settings


class Artifact(object):
    """docstring for Artifact."""
    def __init__(self, foreign_id, artifact_type_id=1):
        self.foreign_id = foreign_id
        self.artifact_type_id = artifact_type_id

    def __repr__(self):
        """String representation for printing to db insert statement."""
        return '(\'{}\', \'{}\')'.format(self.foreign_id,
                                         self.artifact_type_id)


class Tag(object):
    """docstring for Tag."""
    def __init__(self, tag_name, tag_name_short, tag_type_id):
        self.tag_name = tag_name
        self.tag_name_short = tag_name_short
        self.tag_type_id = tag_type_id

    def __repr__(self):
        """String representation for printing to db insert statement."""
        return '(\'{}\', \'{}\', \'{}\')'.format(self.tag_name,
                                                 self.tag_name_short,
                                                 self.tag_type_id)


class ArtifactTagLink(object):
    """docstring for ArtifactTagLink."""
    def __init__(self, artifact_id, tag_id):
        self.artifact_id = artifact_id
        self.tag_id = tag_id

    def __repr__(self):
        return '(\'{}\', \'{}\')'.format(self.artifact_id, self.tag_id)


def query_cause_tag_info(meids):
    q = """
    SELECT me.modelable_entity_id AS foreign_id,
           me.modelable_entity_name,
           mec.cause_id AS epi_db_id,
           sh.cause_name AS tag_name,
           sh.acause AS tag_name_short
    FROM epi.modelable_entity me
    JOIN epi.modelable_entity_cause mec
        USING (modelable_entity_id)
    JOIN shared.cause sh
        USING (cause_id)
    WHERE me.end_date IS NULL
        AND me.modelable_entity_id IN ({})
    """.format(make_sql_obj(meids))
    return query(q, conn_def='epi')


def query_rei_tag_info(meids):
    q = """
    SELECT me.modelable_entity_id AS foreign_id,
           me.modelable_entity_name,
           mer.rei_id AS epi_db_id,
           sh.rei_name AS tag_name,
           sh.rei_name_short AS tag_name_short
    FROM epi.modelable_entity me
    JOIN epi.modelable_entity_rei mer
        USING (modelable_entity_id)
    JOIN shared.rei sh
        USING (rei_id)
    WHERE me.end_date IS NULL
        AND me.modelable_entity_id IN ({})
    """.format(make_sql_obj(meids))
    return query(q, conn_def='epi')


def insert_artifacts_into_prov(artifact_list):
    q = """
    INSERT INTO artifact (foreign_id, artifact_type_id)
    VALUES {};
    """.format(make_sql_obj(artifact_list))
    return 0


def insert_tags_into_prov(tag_list):
    q = """
    INSERT INTO tag (tag_name, tag_name_short, tag_type_id)
    VALUES {};
    """.format(make_sql_obj(tag_list))
    return 0


def delete_artifacts_from_prov(foreign_ids):
    q = """
    DELETE FROM artifact
    WHERE foreign_id IN ({});
    """.format(make_sql_obj(foreign_ids))
    return 0


def return_all_artifacts(db='prov'):
    q = """SELECT * FROM prov.artifact"""
    return query(q, conn_def='prov')


def return_artifact_by_foreign_id(foreign_ids, db='prov'):
    q = """
    SELECT * FROM prov.artifact
    WHERE foreign_id IN ({})
    """.format(make_sql_obj(foreign_ids))
    return query(q, mysqlengine=create_db_engine(db))


def return_all_tags(db='prov'):
    q = """SELECT * FROM prov.tag"""
    return query(q, mysqlengine=create_db_engine(db))


def create_db_engine(db):
    return MySQLEngine(host=settings.DATABASES[db]['HOST'],
                       user_name=settings.DATABASES[db]['USER'],
                       password=settings.DATABASES[db]['PASSWORD'])


def is_new(me_list):
    prov_artifacts = return_all_artifacts()
    existing_mes = prov_artifacts.foreign_id.unique()
    missing = [me for me in me_list if me not in existing_mes]
    return missing


def is_existing(me_list):
    prov_artifacts = return_all_artifacts()
    existing_mes = prov_artifacts.foreign_id.unique()
    existing = [me for me in me_list if me in existing_mes]
    return existing


def is_deprecated(me_list):
    prov_artifacts = return_all_artifacts()
    existing_mes = prov_artifacts.foreign_id.unique()
    deprecated = [me for me in existing_mes if me not in me_list]
    return deprecated


# Establish db dict and db connection
PROV = settings.DATABASES['prov']

# Read in meids from spreadsheet
dirname = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(dirname, 'me_updates/epic_viz_inputs.xlsx')
new = pd.read_excel(filepath)

# Compare existing me's with list of new
input_mes = new.modelable_entity_id.unique()
# meids not currently in prov
new_me = is_new(input_mes)
# meids from input that exist in prov
old_me = is_existing(input_mes)
# deprecated meids from prov db (keep foreign_id=1, COMO)
deprecated_me = is_deprecated(input_mes)
deprecated_me.remove(1)
# Per Logan's request, delete a select list of residual me_ids
to_delete = [1627, 1531, 2831, 1918, 1962, 2063, 2330, 15776, 1605, 1556]
to_delete += old_me

new_me = [me for me in new_me if me not in to_delete]

# Delete deprecated meids from prov
# Use meids to get list of artifact_ids
# Delete artifact_ids from artifact_tag table
# Delete artifact_ids from artifact table

# Generate tag data from new_me ids
causes = query_cause_tag_info(new_me)
causes['tag_type_id'] = 1
reis = query_rei_tag_info(new_me)
reis['tag_type_id'] = 2

# Which me's did not return tag data?
new_tag_metadata = pd.concat([causes, reis])
no_tag_mes = [me for me in new_me if me not in
              new_tag_metadata.foreign_id.unique()]
print('The following modelable_entity_ids did not return cause or rei '
      'data: {}'.format(no_tag_mes))

# Create tag_name, tag_name_short, and tag_type_id data
new_tag_metadata.reset_index(inplace=True, drop=True)
tag_data = []
for i in range(len(new_tag_metadata)):
    tag_data.append((new_tag_metadata.loc[i, 'tag_name'],
                     new_tag_metadata.loc[i, 'tag_name_short'],
                     new_tag_metadata.loc[i, 'tag_type_id']))
# limit to unique tags
tag_data = set(tag_data)

# Create list of artifacts
artifact_list = [Artifact(meid, 1) for meid in new_me]

# Create list of tags
tag_list = [Tag(name, name_short, tag_type) for name, name_short, tag_type
            in tag_data]

# These failed to upload new entries
insert_artifacts_into_prov(artifact_list)
insert_tags_into_prov(tag_list)

# Create artifact-tag entries.
# read tag ids after inserting new tags to db
prov_tags = return_all_tags()
prov_arts = return_all_artifacts()

# Merge on new_tag_metadata to identify unique artifact/tag pairs
df = new_tag_metadata.merge(prov_tags, on='tag_name')
df = df.merge(prov_arts, on='foreign_id')

art_tag_tuple = []
for i in range(len(df)):
    art_tag_tuple.append((df.loc[i, 'artifact_id'], df.loc[i, 'tag_id']))

# Create artifact-tag pair objects for easy printing into INSERT statement
art_tag_link = [ArtifactTagLink(art_id, tag_id) for art_id, tag_id in
                art_tag_tuple]
