import csv
import datetime
import numpy as np
import pandas as pd

from db_tools.query_tools import make_sql_obj

from epic_viz import models
from epic_viz import epi_calls


def return_all_tags():
    """."""
    return models.Tag.objects.all()


def return_all_artifact_tag_links():
    """."""
    return models.ArtifactTag.objects.all()


def return_tag_by_search(search_text):
    """."""
    tag_list = models.Tag.objects.filter(tag_name__icontains=search_text)
    return tag_list


def return_artifact_tag_links(tag_id):
    """."""
    q = """
    SELECT
        artifact_id,
        tag_id AS id
    FROM
        prov.artifact_tag
    WHERE
        tag_id IN ({});
    """.format(make_sql_obj(tag_id))
    return models.ArtifactTag.objects.raw(q)


def create_model_obj(df):
    """."""
    df.reset_index(inplace=True)

    meid = df.at[0, 'modelable_entity_id']
    me_name = df.at[0, 'modelable_entity_name']
    me_type = df.at[0, 'modelable_entity_type']
    model_type = df.at[0, 'model_type']
    mvid = df.at[0, 'model_version_id']
    status_id = df.at[0, 'model_version_status_id']
    date_inserted = df.at[0, 'date_inserted']
    best_start = df.at[0, 'best_start']
    description = df.at[0, 'description']
    status = df.at[0, 'status']

    return models.ModelOutput(meid,
                              me_name,
                              me_type,
                              model_type,
                              mvid,
                              status_id,
                              date_inserted,
                              best_start,
                              description,
                              status)


def get_compare_data():
    return epi_calls.return_gbd_data()


def query_epi_results(meid):
    df = epi_calls.query_me_data(meid)
    meid = list(df.modelable_entity_id)[0]
    me_name = df.modelable_entity_name[0]

    if df.model_version_id[0] is None:
        df = create_modeless_df(df, meid, me_name)
    else:
        df = limit_epi_results(df)

    df['status'] = set_df_status(df)
    return df


def create_modeless_df(df, meid, me_name):
    d = {'modelable_entity_id': [meid],
         'modelable_entity_name': [me_name],
         'modelable_entity_type': [None],
         'model_type': [None],
         'model_version_id': [None],
         'model_version_status_id': [None],
         'date_inserted': [None],
         'best_start': [None],
         'gbd_round_id': [None],
         'description': ['No model run for GBD round 5']}
    return pd.DataFrame(d)


def limit_epi_results(df):
    meid = df.modelable_entity_id[0]
    me_name = df.modelable_entity_name[0]
    temp_df = df[df.gbd_round_id == 5]
    if len(temp_df) > 0:
        status_ids = list(temp_df.model_version_status_id)
        if 1 in status_ids:
            df = temp_df[temp_df.model_version_status_id == 1]
        else:
            df = temp_df[temp_df.date_inserted == max(temp_df.date_inserted)]
    else:
        df = create_modeless_df(df, meid, me_name)
    return df


def set_df_status(df, dynamic=False):
    """
    Returns the status column for all models in the dataframe.

    Compares the date of the model to the dynamic date (COMO run) or a flat
    date (set below in the else branch).

    Returns:
        String representing the status via color.
    """
    if dynamic:
        compare_df = get_compare_data()
        date = compare_df.at[0, 'date_inserted'].to_pydatetime()
    else:
        date = datetime.datetime(2018, 5, 16, 0, 0, 0)
    df = df.reset_index()

    mvid = df.model_version_id[0]
    mvsid = df.model_version_status_id[0]

    if mvid is None:
        return 'red'
    else:
        if mvsid == 1:
            if df.date_inserted[0] > date:
                return 'green'
            else:
                return 'yellow'
        else:
            return 'orange'


def return_tag_model(tag_id):
    tag_model = models.Tag.objects.get(tag_id=tag_id)
    return tag_model


def _json_encode_tag(tag):
    return {'tag_id': tag.tag_id, 'tag_name': tag.tag_name}


def _json_encode_me(me):
    return {'me_id': me.meid,
            'me_name': me.me_name,
            'me_type': me.me_type,
            'model_type': me.model_type,
            'mvid': me.mvid,
            'date': me.date_inserted,
            'description': me.description,
            'status': me.status}


def _json_encode_date(date):
    return {'date': date}


def _json_encode_process(process):
    return {'process': process}


def convert_date_to_str(date, source=None):
    """Dates will come from two 'sources':

    1. dynamically generated from the db--such as central processes or model
    version metadata.

    2. statically input--at the beginning before como runs when we want to
    compare with new releases of Dismod software.

    Flag to trigger which source is passed in from views.py(105).return_me().
    """
    if source:
        return date.strftime('%B %d, %Y')
    else:
        return date.strftime('%B %d, %Y %H:%M:%S')


def return_models_by_tag(tag_id):
    """."""
    art_tag_links = return_artifact_tag_links(tag_id)
    artifact_ids = [i.artifact_id for i in art_tag_links]
    artifacts = models.Artifact.objects.filter(artifact_id__in=artifact_ids)

    meids = [i.foreign_id for i in artifacts]
    results = [query_epi_results(i) for i in meids]
    object_list = [create_model_obj(i) for i in results]
    return object_list


def return_data_for_csv():
    tags = epi_calls.query_all_tags()
    artifacts = epi_calls.query_all_artifacts()
    art_tags = epi_calls.query_all_artifact_tag_links()

    df = art_tags.merge(tags, on='tag_id')
    df = df.merge(artifacts, on='artifact_id')
    df.rename(columns={'foreign_id': 'modelable_entity_id'}, inplace=True)
    df = df[['tag_name', 'tag_name_short', 'modelable_entity_id']]

    meids = df.modelable_entity_id.unique().tolist()
    results = epi_calls.query_me_data(meids)
    results = limit_epi_results(results)

    results = results[['modelable_entity_id', 'model_version_id',
                       'description', 'model_version_status_id',
                       'date_inserted', 'best_start', 'best_user']]

    df = df.merge(results, on='modelable_entity_id')
    return df
