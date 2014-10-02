__author__ = 'mbewley'

import pandas as pd
import re
# df = pd.read_csv('cpc2caab_nsw.csv')
#
#
# def descrip2caab(s):
# m = re.search('\([0-9]*\)', s)
#     if m:
#         caab_code = m.group(0).strip('()')
#         return caab_code
#
# caab_codes = df.caab_descrip.apply(lambda s: descrip2caab(s))
# df['caab_code'] = caab_codes
# null_inds = df.caab_code.isnull()
# df.caab_code.loc[null_inds] = df.loc[null_inds].caab_descrip
# df.pop('caab_descrip')
# df.set_index('cpc_code', inplace=True)
# df.to_csv('cpc2caab_nsw.csv')

import pandas as pd
import psycopg2

conn = psycopg2.connect("dbname='catamidb' user='auv' host='eddy' password='euro!trip'")
query = "SELECT caab_code, code_name FROM annotations_annotationcode ORDER BY code_name"
dbcodes = pd.read_sql(query, conn)
print dbcodes.head()
for g in ['nsw', 'qld2010', 'tas08', 'wa2011']:
    df = pd.read_csv('cpc2caab_%s.csv' % g)
    df = pd.merge(df, dbcodes, on='caab_code').set_index('cpc_code')
    df.to_csv('cpc_caab_output_%s.csv' % g)
