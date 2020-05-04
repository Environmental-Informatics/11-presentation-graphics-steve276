#!/bin/env python
# Modified May 04, 2020
# by Miriam Stevens
# This is the script for assignment 11-Presentation Graphics
# Summary figures are generated from annual and monthly streamflow metrics
# computed in assignment 10
# Seethe assignment documentation and repository at:
# https://github.com/Environmental-Informatics/11-presentation.git for more details
#
import pandas as pd
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "agency_cd", "site_no", "Date", "Discharge", "Quality". The 
    "Date" column should be used as the DataFrame index. The pandas read_csv
    function will automatically replace missing values with np.NaN, but needs
    help identifying other flags used by the USGS to indicate no data is 
    availabiel.  Function returns the completed DataFrame."""
    
    # define column names
    colNames = ['agency_cd', 'site_no', 'Date', 'Discharge', 'Quality']

    # open and read the file
    DataDF = pd.read_csv(fileName, header=1, names=colNames,  
                         delimiter=r"\s+",parse_dates=[2], comment='#',
                         na_values=['Eqp'])
    
    DataDF = DataDF.set_index('Date')
    
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isnull().sum()
    
     # replace negative values with nan
    DataDF.loc[DataDF['Discharge'] < 0, 'Discharge'] = np.NaN

    
    return( DataDF, MissingValues )


def ClipData( DataDF, startDate, endDate ):
    """This function clips the given time series dataframe to a given range 
    of dates. Function returns the clipped dataframe and and the number of 
    missing values."""
    
    #clip data 
    DataDF = DataDF.loc[startDate:endDate]  
    
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isnull().sum()
    
    return( DataDF, MissingValues )


def ReadMetrics( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    the metrics from the assignment on descriptive statistics and 
    environmental metrics.  Works for both annual and monthly metrics. 
    Date column should be used as the index for the new dataframe.  Function 
    returns the completed DataFrame."""
    
    # open and read the csv file
    DataDF = pd.read_csv(fileName, header=0, parse_dates=[0], index_col='Date')
    
    return( DataDF )

def GetMonthlyAverages(DataDF):
    """This function calculates annual average monthly flow.  
    The routine returns an array of mean values 
    for the Discharge values in the original dataframe."""
    
    colName = ['Discharge']
    
    # define index as dates of ressmpled data. 
    # data is resampled monthly
    monthlyIndex = DataDF.resample('MS').mean().index
    
    # create empty dataframe
    MoDataDF = pd.DataFrame(data=0, index=monthlyIndex, columns=colName)
    
    # add resampled discharge data to dataframe
    MoDataDF['Discharge'] = DataDF['Discharge'].resample('MS').mean()
    
    # compute monthly averages
    MonthlyAverages = MoDataDF.groupby(MoDataDF.index.month).mean()
    
    
    return( MonthlyAverages )

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    # define full river names as a dictionary so that abbreviations are not used in figures
    riverName = { "Wildcat": "Wildcat Creek",
                  "Tippe": "Tippecanoe River" }
    
    # define txt filenames as a dictionary
    fileName = { "Wildcat": "WildcatCreek_Discharge_03335000_19540601-20200315.txt",
                 "Tippe": "TippecanoeRiver_Discharge_03331500_19431001-20200315.txt" }
    
    # define csv names as a dictionary
    csvName = {"Annual": "Annual_Metrics-Copy.csv",
               "Monthly": "Monthly_Metrics-Copy.csv"}
    
    # define blank dictionaries for each file type
    DataDF = {}
    MissingValues = {}
    MonthlyAverages = {}
    
    # process txt files to get daily streamflow values and annual monhtly averages
    for file in fileName.keys():
        
        DataDF[file] = ReadData(fileName[file])
        
        DataDF[file] = ClipData( DataDF[file], '1969-10-01', '2019-09-30' )
        
        MonthlyAverages[file] = GetMonthlyAverages(DataDF[file])
        
    # process csv files to get daily metrics   
    for csv in csvName.keys():
        DataDF[csv] = ReadMetrics(csvName[csv])
        
        
        
    #generate plots 
    
    #Daily flow for last 5 years of the record
    
    plt.plot(DataDF['Wildcat']['2015-01-01':'2019-12-30']['Discharge'], label="Wildcat Creek")
    plt.plot(DataDF['Tippe']['2015-01-01':'2019-12-30']['Discharge'], label="Tippecanoe River")
    plt.xlabel('Date', fontsize=15)
    plt.ylabel('Discharge\n cubic feet per second (cfs)', fontsize=15)
    plt.title('Daily streamflow', fontsize=20)
    plt.legend(fontsize=13)
    fig = plt.gcf()
    fig.set_size_inches(9, 6)
    plt.savefig('Daily-streamflow.png', dpi=96)
    plt.show()
    
    
   # Annual coefficient of variation

    plt.plot(DataDF['Wildcat']['Coeff Var'][0:50], label='Wildcat Creek')
    plt.plot(DataDF['Tippe']['Coeff Var'][50:101], label='Tippecanoe River')
    plt.xlabel('Date', fontsize=15)
    plt.ylabel('Coefficient of variation', fontsize=15)
    plt.title('Annual Coefficient of Variation', fontsize=20)
    plt.legend(fontsize=13)
    fig = plt.gcf()
    fig.set_size_inches(10, 6.5)
    plt.savefig('annual-CV.png', dpi=96)
    plt.show()
    
   
    #Annual TQmean 
    
    plt.plot(DataDF['Wildcat']['Tqmean'][0:50], label='Wildcat Creek')
    plt.plot(DataDF['Tippe']['Tqmean'][50:101], label='Tippecanoe River')
    plt.xlabel('Date', fontsize=15)
    plt.ylabel('Tqmean (&)', fontsize=15)
    plt.title('Tqmean', fontsize=20)
    plt.legend(loc="upper right", fontsize=13)
    fig = plt.gcf()
    fig.set_size_inches(10, 6.5)
    plt.savefig('Tqmean.png', dpi=96)
    plt.show()
    
    #Annual R-B index
    
    plt.plot(DataDF['Wildcat']['R-B Index'][0:50], label='Wildcat Creek')
    plt.plot(DataDF['Tippe']['R-B Index'][50:101], label='Tippecanoe River')
    plt.xlabel('Date', fontsize=15)
    plt.ylabel('R-B Index', fontsize=15)
    plt.title('Richards-Baker Flashiness Index (R-B Index)', fontsize=20)
    plt.legend( fontsize=13)
    fig = plt.gcf()
    fig.set_size_inches(10, 6.5)
    plt.savefig('RBindex.png')
    plt.show()
        
        
    #Average annual monthly flow
    
    plt.plot(DataDF['Wildcat'], label='Wildcat Creek')
    plt.plot(DataDF['Tippe'], label='Tippecanoe River')
    plt.xlabel('Month', fontsize=15)
    plt.ylabel('Discharge\n cubic feet per second (cfs)', fontsize=15)
    plt.title('Annual average monthly streamflow', fontsize=20)
    plt.legend( fontsize=13)
    fig = plt.gcf()
    fig.set_size_inches(10, 6.5)
    plt.savefig('monthly-averages.png')
    plt.show()
    
    #Return period of annual peak flow events
        

    
    
    
    
    
 
