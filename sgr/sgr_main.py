
import sgr.get_data
import sgr.modis_waterfrac
import sgr.sgr_data
import os
import numpy as np




def main(argv=None):
    #get_gdac_file_by_date(skipifexists=True)
    #get_modis_file_by_date(thedatetime=datetime.datetime(2016,2,2),skipifexists=True)
    url,fname = sgr.get_data.get_last_available_modis_file()

    lst = sgr.get_data.get_available_modis_files([2014,2015,2016])

    for url in lst:
        fname = os.path.basename(url)
        lfilename = os.path.join(sgr.get_data.stagingarea, fname)
        if not os.path.exists(lfilename):
            sgr.get_data.httpdownloadurl(url,lfilename)
            h5fname = sgr.get_data.converttohdf5(lfilename)

    return
    x,y,swir21 = sgr.modis_waterfrac.readmodisswir21(h5fname)
    wf = sgr.modis_waterfrac.detwfrac(swir21)
    sngid = sgr.sgr_data.get_signal_ids(295,y,x)

    signal = wf[sngid].mean()
    # now initialize the lookup object

    sgrObj = sgr.sgr_data.SignalQCdf(sgr.sgr_data.qnetcdf,sgr.sgr_data.modissignalnetcdf)

    result = sgrObj.findqfromsignal(signal,295)

    print result
    #get_stationfrombeck('Beck_Runoff_Database_v3.nc',2)


if __name__ == "__main__":
    main()