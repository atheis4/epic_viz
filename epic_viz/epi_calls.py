import pandas as pd

from db_tools.ezfuncs import query
from db_tools.mysqlapis import MySQLEngine
from db_tools.query_tools import make_sql_obj

from epic_viz import settings


def create_sql_engine(db):
    return MySQLEngine(host=settings.DATABASES[db]['HOST'],
                       user_name=settings.DATABASES[db]['USER'],
                       password=settings.DATABASES[db]['PASSWORD'])


def query_all_artifacts():
    q = """SELECT * FROM prov.artifact;"""
    return query(q, mysqlengine=create_sql_engine('prov'))


def query_all_tags():
    q = """SELECT * FROM prov.tag;"""
    return query(q, mysqlengine=create_sql_engine('prov'))


def query_all_artifact_tag_links():
    q = """SELECT * FROM prov.artifact_tag;"""
    return query(q, mysqlengine=create_sql_engine('prov'))


def query_artifacts_by_me(me_list):
    q = """
    SELECT artifact_id,
           foreign_id,
           artifact_type_id
    FROM prov.artifact
    WHERE foreign_id IN ({});
    """.format(make_sql_obj(me_list))
    return query(q, mysqlengine=create_sql_engine('prov'))


def query_tags_by_name(tag_names):
    q = """
    SELECT tag_id,
           tag_name,
           tag_name_short,
           tag_type_id
    FROM prov.tag
    WHERE tag_name IN ({});
    """.format(make_sql_obj(tag_names))
    return query(q, mysqlengine=create_sql_engine('prov'))


def query_me_data(meid):
    """Query Epi DB for model version data via modelable entity id."""
    q = """
    SELECT me.modelable_entity_id,
           me.modelable_entity_name,
           met.modelable_entity_type,
           mt.model_type,
           mv.model_version_id,
           mv.model_version_status_id,
           mv.date_inserted,
           mv.best_start,
           mv.gbd_round_id,
           mv.description,
           mv.best_user
    FROM epi.modelable_entity me
    LEFT JOIN epi.model_version mv USING (modelable_entity_id)
    JOIN epi.modelable_entity_type met USING (modelable_entity_type_id)
    JOIN epi.model_type mt USING (model_type_id)
    WHERE modelable_entity_id IN ({});
    """.format(make_sql_obj(meid))
    return query(q, mysqlengine=create_sql_engine('epi'))


def query_cause_info(meids):
    """Used to generate new tags for causes associated with input meids."""
    q = """
    SELECT me.modelable_entity_id,
           me.modelable_entity_name,
           mec.cause_id,
           sh.cause_name,
           sh.acause
    FROM epi.modelable_entity me
    JOIN epi.modelable_entity_cause mec USING (modelable_entity_id)
    JOIN shared.cause sh USING (cause_id)
    WHERE me.end_date IS NULL
        AND me.modelable_entity_id IN ({});
    """.format(make_sql_obj(meids))
    return query(q, mysqlengine=create_sql_engine('epi'))


def query_rei_info(meids):
    """Used to generate new tags for rei associated with input meids."""
    q = """
    SELECT me.modelable_entity_id,
           me.modelable_entity_name,
           mer.rei_id,
           sh.rei_name,
           sh.rei_name_short
    FROM epi.modelable_entity me
    JOIN epi.modelable_entity_rei mer USING (modelable_entity_id)
    JOIN shared.rei sh USING (rei_id)
    WHERE me.end_date IS NULL
        AND me.modelable_entity_id IN ({});
    """.format(make_sql_obj(meids))
    return query(q, mysqlengine=create_sql_engine('epi'))


def return_gbd_data():
    """Query GBD DB to return most recent COMO process."""
    q = """
    SELECT gpv.gbd_process_version_id,
           gpv.gbd_process_version_note AS gbd_process,
           gpv.date_inserted,
           gpv.last_updated
    FROM gbd.gbd_process_version gpv
    WHERE gpv.gbd_process_id = 1
        AND gpv.gbd_round_id = 5
        AND gpv.gbd_process_version_status_id = 1;
    """
    return query(q, mysqlengine=create_sql_engine('gbd'))
