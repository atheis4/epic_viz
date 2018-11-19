import datetime
from io import BytesIO
import time
import xlsxwriter

from django.core import serializers
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

from epic_viz import epi_calls
from epic_viz import logic
from epic_viz import models


def _set_status(row, date):
    mvid = row.model_version_id
    mvsid = row.model_version_status_id
    date_inserted = row.date_inserted

    if mvid is None:
        return 'red'
    else:
        if mvsid == 1:
            if date_inserted > date:
                return 'green'
            else:
                return 'yellow'
        else:
            return 'orange'


def return_search_tags(request):
    if request.method == 'GET':
        search_text = request.GET['search']
        tag_list = logic.return_tag_by_search(search_text)
    tag_list = [logic._json_encode_tag(tag) for tag in tag_list]
    print(tag_list)
    return JsonResponse(tag_list, safe=False)


def return_all_tags(request):
    """Returns and encodes the full list of tags from the prov db."""
    tag_list = logic.return_all_tags()
    tag_list = [logic._json_encode_tag(tag) for tag in tag_list]
    return JsonResponse(tag_list, safe=False)


def return_csv(request):
    import time
    start = time.time()
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('EpiC Viz')
    # Generate gbd process data for title
    compare_data = epi_calls.return_gbd_data()
    process = compare_data.gbd_process[0]
    process_date = compare_data.date_inserted[0]
    title = ('Epi Computation Visualizer Output: Models compared to '
             '{} on {}').format(process, process_date)
    # Generate tag/me data
    data = logic.return_data_for_csv()
    data['status'] = ''
    for idx, row in data.iterrows():
        data.loc[idx, 'status'] = _set_status(row, process_date)
    # After comparison/status set, convert date to string
    data['date_inserted'] = data.date_inserted.apply(logic.convert_date_to_str)
    data['best_start'] = data.best_start.apply(logic.convert_date_to_str)
    # Formatting dicts
    title_format = workbook.add_format({'bold': True})
    status_to_color = {'green': '#99E399', 'yellow': '#EBF189',
                       'orange': '#F3BD58', 'red': '#E38D83'}
    # Add title to worksheet
    row = 0
    worksheet.write(row, 0, title, title_format)
    row += 2
    # Add columns to worksheet
    columns = ['tag_name_short', 'modelable_entity_id', 'model_version_id',
               'description', 'model_version_status_id', 'best_user',
               'date_inserted', 'best_start']
    for i, col in enumerate(columns):
        worksheet.write(row, i, col, title_format)
    row += 1
    # Add data to worksheet
    for i in range(len(data)):
        _rform = workbook.add_format({'bg_color':
                                      status_to_color[data.loc[i, 'status']]})
        worksheet.write(row, 0, data.loc[i, 'tag_name_short'], _rform)
        worksheet.write(row, 1, data.loc[i, 'modelable_entity_id'], _rform)
        worksheet.write(row, 2, data.loc[i, 'model_version_id'], _rform)
        worksheet.write(row, 3, data.loc[i, 'description'], _rform)
        worksheet.write(row, 4, data.loc[i, 'model_version_status_id'], _rform)
        worksheet.write(row, 5, data.loc[i, 'best_user'], _rform)
        worksheet.write(row, 6, data.loc[i, 'date_inserted'], _rform)
        worksheet.write(row, 7, data.loc[i, 'best_start'], _rform)
        row += 1
    # Close workbook
    workbook.close()
    output.seek(0)
    content_type = ('application/vnd.openxmlformats-officedocument.'
                    'spreadsheetml.sheet')
    print('end of csv in views - total time: {}'.format(time.time()-start))
    return HttpResponse(output.read(), content_type=content_type)


def return_me(request):
    if request.method == 'GET':
        tag_id = request.GET['tag_id']

    tag_id = int(tag_id)
    tag = logic.return_tag_model(tag_id)
    tag = logic._json_encode_tag(tag)

    # Only false if comparing modelable entities to a hard date--True if
    # comparing to a central machine run.
    dynamic = False

    if dynamic:
        source = None
        process_df = logic.get_compare_data()
        gbd_process = process_df.gbd_process[0]
        compare_date = process_df.date_inserted[0].to_pydatetime()
    else:
        source = 'static'
        gbd_process = u'8th version of clinical data'
        compare_date = datetime.datetime(2018, 5, 16, 0, 0, 0)

    gbd_process = logic._json_encode_process(gbd_process)
    compare_date = logic.convert_date_to_str(compare_date, source)
    compare_date = logic._json_encode_date(compare_date)

    models = logic.return_models_by_tag(tag_id)
    for model in models:
        if model.date_inserted:
            model.date_inserted = logic.convert_date_to_str(
                model.date_inserted)
    models = [logic._json_encode_me(model) for model in models]

    tag_results = {'tag': tag, 'process': gbd_process, 'date': compare_date,
                   'models': models}
    print(tag_results)

    return JsonResponse(tag_results, safe=False)


def render_home(request):
    return render(request, 'epic_viz/index.html')
