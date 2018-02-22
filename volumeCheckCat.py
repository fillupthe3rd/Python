"""
Client Service Category Vol/KPI Monitor



"""

import numpy as np
import pyodbc
import pandas as pd
from pandas import TimeGrouper
from pandas import ExcelWriter
import xlsxwriter
import matplotlib.pyplot as plt
from functools import lru_cache
from datetime import datetime as dt
import calendar

# Declarations
# List of clients and categories to be included
client = 'Cigna East'
category = 'Anesthesia'


# Connect to and query SQL server for given Client & Service Category
def SQLpull(client, category):

    # SQl context
    conn = pyodbc.connect(r'DRIVER={ODBC Driver 13 for SQL Server};'
                          r'SERVER=businteldw.stratose.com,1565;'
                          r'DATABASE=CAIDataWarehouse;'
                          r'Trusted_Connection=yes')
    sql = '''
        select --dc.ClientParentNameShort Client
            --, dst.CategoryDesc Category
            --, dd.DateMonthSSRS Month
            --, 
            dd.DateDay 
            , count(f.CMID) Claims
            , sum(f.CMAllowed) Allowed
            , sum(f.CMAllowedHit) Hit
            , sum(f.LineSavings) Savings
            , sum(f.CMAllowedhit)/sum(f.CMAllowed) HitRate
            , sum(f.LineSavings)/sum(f.CMAllowedHit) SaveRate
            , sum(f.LineSavings)/sum(f.CMAllowed) SaveRateEff
        
        
        from v_FactClaimLine f 
            join DimDate dd on f.dimdatereceivedkey = dd.dimdatekey
            join dimclient dc on f.dimclientkey = dc.dimclientkey
            join dimclaimeligible dce on f.dimclaimeligiblekey = dce.dimclaimeligiblekey
            join dimservicetype dst on f.dimservicetypekey = dst.dimservicetypekey
            join dimproduct dpr on f.dimproductkey = dpr.dimproductkey
            join dimclaimtype dct on f.dimclaimtypekey = dct.dimclaimtypekey
            join DimProvider prov on f.DimProviderKey = prov.DimProviderKey
        
        where dce.ClaimEligible = 'Eligible'
            and dd.DateDay between (convert(date, getdate() - 30)) and (convert(date, getdate()))
            and dc.ClientParentNameShort = '%s'
            and dst.CategoryDesc = '%s'
        
        group by --dc.ClientParentNameShort
            --, dst.CategoryDesc
            --, dd.DateMonthSSRS
            --, 
            dd.DateDay
        
        order by --dc.ClientParentNameShort
            --, dst.CategoryDesc
            --, dd.DateMonthSSRS
            --, 
            dd.DateDay
    ''' % (client, category)

    # Read SQL data, set date as index, close connection to server
    df = pd.read_sql(sql, conn)
    df = df.set_index('DateDay')
    conn.close()

    return df


# Calculated columns
def calc(df):
    df = df.set_index('DateDay')
    return df


# Write results to Excel, add charts, format
def toExcel(df, sheet):

    #
    dfKPI = df.loc[:, 'HitRate':]
    rowCount = len(df.index)

    writer = pd.ExcelWriter(r'C:\Users\pallen\Documents\VolumeCheck.xlsx', engine='xlsxwriter')
    workbook = writer.book
    worksheet = writer.sheets['Anesthesia']

    dfKPI.to_excel(writer, sheet_name='Anesthesia', startrow=1, startcol=1)

    chart = workbook.add_chart({'type': 'line'})
    chart.add_series({'values': '=Anesthesia!$B$2:$D$%s'})
    worksheet.insert_chart('F2', chart)

    format1 = workbook.add_format({'num_format': '$#,##0'})
    format2 = workbook.add_format({'num_format': '0%'})
    format3 = workbook.add_format({'num_format': '#,##0'})

    worksheet.set_column('C:E', 15, format2)

    writer.save()

    return



df1.pivot(index='DateDay', values='SaveP').plot(kind='bar')



def plot(client, category):
    def toExcelopen():
        writer = pd.ExcelWriter(r'C:\Users\pallen\Documents\VolumeCheck.xlsx', engine='openpyxl')
        wb = load_workbook(writer)
        dfTest.to_excel(writer, 'Anesthesia', startrow=0, startcol=0)
        ws = wb.active

        c1 = LineChart()
        data = Reference(ws, min_col=2, min_row=1, max_col=2, max_row=rowCount)
        c1.add_data(data, titles_from_data=True)

        ws.add_chart(c1, "D2")
        writer.save()
        workbook.close()

        return
    return


for i in range(0, len(client)):
    for j in range(0, len(category)):
        df = SQLpull(client[i], category[j])