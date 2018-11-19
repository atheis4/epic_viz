
class SpanMap(object):

    def __init__(self, map_df, id_col, merge_col):
        self.map_df = map_df
        self.id_col = id_col
        self.merge_col = merge_col

        self.map_df.rename(columns={merge_col: 'merge_col'}, inplace=True)


class SpanTarget(object):

    def __init__(self, target_df, id_col, merge_col):
        self.target_df = target_df
        self.id_col = id_col
        self.merge_col = merge_col

        self.target_df.rename(columns={merge_col: 'merge_col'}, inplace=True)


def link_ids(span_map, span_target):
    df = span_target.target_df.copy()
    map_df = span_map.map_df.copy()

    xed = map_df.merge(df, on='merge_col')

    return xed
