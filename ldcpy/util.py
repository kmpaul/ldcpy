import functools

import xarray as xr

from .metrics import DatasetMetrics, DiffMetrics

def collect_datasets(varnames, list_of_ds, labels, **kwargs):
    """
    Concatonate several different xarray datasets across a new
    "collection" dimension, which can be accessed with the specified 
    labels.  Stores them in an xarray dataset which can be passed to 
    the ldcpy plot functions (Call this OR open_datasets() before
    plotting.)
    

    Parameters
    ==========
    varnames : list
        The variable(s) of interest to combine across input files (usually just one)
    list_of_datasets : list
        The datasets to be concatonated into a collection
    labels : list
        The respective label to access data from each dataset (also used in plotting fcns)

        **kwargs :
        (optional) – Additional arguments passed on to xarray.concat(). A list of available arguments can
        be found here: https://xarray-test.readthedocs.io/en/latest/generated/xarray.concat.html

    Returns
    =======
    out : xarray.Dataset
          a collection containing all the data from the list datasets

    """
    # Error checking:
    # list_of_files and labels must be same length
    assert len(list_of_ds) == len(
        labels
    ), 'collect_dataset dataset list and labels arguments must be the same length'

    #preprocess
    for i, myds in enumerate(list_of_ds):
        list_of_ds[i]= preprocess(myds, varnames)
        
    
    full_ds = xr.concat( list_of_ds , 'collection', **kwargs )

    full_ds['collection'] = xr.DataArray(labels, dims='collection')

    print('dataset size in GB {:0.2f}\n'.format(full_ds.nbytes / 1e9))

    return full_ds
    
    

def open_datasets(varnames, list_of_files, labels, **kwargs):
    """
    Open several different netCDF files, concatenate across
    a new 'collection' dimension, which can be accessed with the specified
    labels. Stores them in an xarray dataset which can be passed to the ldcpy
    plot functions.

    Parameters
    ==========
    varnames : list
           The variable(s) of interest to combine across input files (usually just one)
    list_of_files : list
        The file paths for the netCDF file(s) to be opened
    labels : list
        The respective label to access data from each netCDF file (also used in plotting fcns)

    **kwargs :
        (optional) – Additional arguments passed on to xarray.open_mfdataset(). A list of available arguments can
        be found here: http://xarray.pydata.org/en/stable/generated/xarray.open_dataset.html

    Returns
    =======
    out : xarray.Dataset
          a collection containing all the data from the list of files


    """

    # Error checking:
    # list_of_files and labels must be same length
    assert len(list_of_files) == len(
        labels
    ), 'open_dataset file list and labels arguments must be the same length'

    #preprocess_vars is here for working on jupyter hub...
    def preprocess_vars(ds):
        return ds[varnames];
    
    full_ds = xr.open_mfdataset(
        list_of_files,
        concat_dim='collection',
        combine='nested',
        data_vars=varnames,
        parallel=True,
        preprocess=preprocess_vars,
        **kwargs,
    )

    full_ds['collection'] = xr.DataArray(labels, dims='collection')
    print('dataset size in GB {:0.2f}\n'.format(full_ds.nbytes / 1e9))

    return full_ds


def preprocess(ds, varnames):
    return ds[varnames]


def print_stats(ds, varname, set1, set2, time=0, significant_digits=4):
    """
    Print error summary statistics of two DataArrays

    Parameters
    ==========
    ds : xarray.Dataset
        An xarray dataset containing multiple netCDF files concatenated across a 'collection' dimension
    varname : str
        The variable of interest in the dataset
    set1 : str
        The collection label of the "control" data
    set2 : str
        The collection label of the (1st) data to compare
    time : int, optional
        The time index used to compare the two netCDF files (default 0)

    significant_digits : int, optional
        The number of significant digits to use when printing stats, (default 4)

    Returns
    =======
    out : None

    """
    print('Comparing {} data (set1) to {} data (set2)'.format(set1, set2))

    ds0_metrics = DatasetMetrics(ds[varname].sel(collection=set1).isel(time=time), ['lat', 'lon'])
    ds1_metrics = DatasetMetrics(ds[varname].sel(collection=set2).isel(time=time), ['lat', 'lon'])
    d_metrics = DatasetMetrics(
        ds[varname].sel(collection=set1).isel(time=time)
        - ds[varname].sel(collection=set2).isel(time=time),
        ['lat', 'lon'],
    )
    diff_metrics = DiffMetrics(
        ds[varname].sel(collection=set1).isel(time=time),
        ds[varname].sel(collection=set2).isel(time=time),
        ['lat', 'lon'],
    )

    output = {}

    output['skip1'] = 0

    output['mean set1'] = ds0_metrics.get_metric('mean').values
    output['mean set2'] = ds1_metrics.get_metric('mean').values
    output['mean diff'] = d_metrics.get_metric('mean').values

    output['skip2'] = 0

    output['variance set1'] = ds0_metrics.get_metric('variance').values
    output['variance set2'] = ds1_metrics.get_metric('variance').values

    output['skip3'] = 0

    output['standard deviation set1'] = ds0_metrics.get_metric('std').values
    output['standard deviation set2'] = ds1_metrics.get_metric('std').values

    output['skip4'] = 0

    # output['dynamic range set1'] = ds0_metrics.get_metric('range').values
    # output['dynamic range set2'] = ds1_metrics.get_metric('range').values

    # output['skip5'] = 0xs

    output['max value set1'] = ds0_metrics.get_metric('max_val').values
    output['max value set2'] = ds1_metrics.get_metric('max_val').values
    output['min value set1'] = ds0_metrics.get_metric('min_val').values
    output['min value set2'] = ds1_metrics.get_metric('min_val').values

    output['skip55'] = 0

    output['max abs diff'] = d_metrics.get_metric('max_abs').values
    output['min abs diff'] = d_metrics.get_metric('min_abs').values
    output['mean abs diff'] = d_metrics.get_metric('mean_abs').values

    output['mean squared diff'] = d_metrics.get_metric('mean_squared').values
    output['root mean squared diff'] = d_metrics.get_metric('rms').values

    output['normalized root mean squared diff'] = diff_metrics.get_diff_metric('n_rms').values
    output['normalized max pointwise error'] = diff_metrics.get_diff_metric('n_emax').values
    output['pearson correlation coefficient'] = diff_metrics.get_diff_metric(
        'pearson_correlation_coefficient'
    ).values
    output['ks p-value'] = diff_metrics.get_diff_metric('ks_p_value')
    tmp = 'spatial relative error(% > ' + str(ds0_metrics.get_single_metric('spre_tol')) + ')'
    output[tmp] = diff_metrics.get_diff_metric('spatial_rel_error')
    output['ssim'] = diff_metrics.get_diff_metric('ssim')

    for key, value in output.items():
        if key[:4] != 'skip':
            rounded_value = f'{float(f"{value:.{significant_digits}g}"):g}'
            print(f'{key}: {rounded_value}')
        else:
            print(' ')

            
def check_metrics(ds, varname, set1, set2, time=0):
    """
        
    Check the K-S, Pearson, and Spatial Relative Error metrics from:

    A. H. Baker, H. Xu, D. M. Hammerling, S. Li, and J. Clyne, 
    “Toward a Multi-method Approach: Lossy Data Compression for 
    Climate Simulation Data”, in J.M. Kunkel et al. (Eds.): ISC 
    High Performance Workshops 2017, Lecture Notes in Computer 
    Science 10524, pp. 30–42, 2017 (doi:10.1007/978-3-319-67630-2_3). 
   
    Check the SSIM metric from: 

    A.H. Baker, D.M. Hammerling, and T.L. Turton. “Evaluating image
    quality measures to assess the impact of lossy data compression 
    applied to climate simulation data”, Computer Graphics Forum 38(3),
    June 2019, pp. 517-528 (doi:10.1111/cgf.13707).


    Parameters
    ==========
    ds : xarray.Dataset
        An xarray dataset containing multiple netCDF files concatenated across a 'collection' dimension
    varname : str
        The variable of interest in the dataset
    set1 : str
        The collection label of the "control" data
    set2 : str
        The collection label of the (1st) data to compare
    time : int, optional
        The time index used t
    Returns
    =======
    out : Number of failing metrics

    """

    #TO DO: put metric thresholds in a modifiable data structure
    num_fail = 0
    
    print('Evaluating 4 metrics for {} data (set1) and {} data (set2)'.format(set1, set2), ":")

    diff_metrics = DiffMetrics(
        ds[varname].sel(collection=set1).isel(time=time),
        ds[varname].sel(collection=set2).isel(time=time),
        ['lat', 'lon'],
    )

    #Pearson less than < :99999 means fail
    pcc = diff_metrics.get_diff_metric('pearson_correlation_coefficient').values
    if (pcc < .99999):
        print("     *FAILED pearson correlation coefficient test...(pcc = {0:.5f}".format(pcc), ")")
        num_fail = num_fail + 1
    else:
        print("     PASSED pearson correlation coefficient test...(pcc = {0:.5f}".format(pcc), ")")
        
    #K-S p-value greater than .05 means fail
    ks = diff_metrics.get_diff_metric('ks_p_value')
    if (ks > 0.05):
        print("     *FAILED ks test...(ks p_val = {0:.4f}".format(ks), ")")
        num_fail = num_fail + 1

    else:
        print("     PASSED ks test...(ks p_val = {0:.4f}".format(ks), ")")

        #Spatial rel error fails if more than 5%
    spre = diff_metrics.get_diff_metric('spatial_rel_error')
    if (spre > 5.0):
        print("     *FAILED spatial relative error test ... (spre = {0:.2f}".format(spre), " %)")
        num_fail = num_fail + 1
    else: 
        print("     PASSED spatial relative error test ...(spre = {0:.2f}".format(spre), " %)")

        
    #SSIM less than of 0.99995 is failing
    ssim_val = diff_metrics.get_diff_metric('ssim')
    if (ssim_val < 0.99995):
        print("     *FAILED SSIM test ... (ssim = {0:.5f}".format(ssim_val), ")")
        num_fail = num_fail + 1
    else:
        print("     PASSED SSIM test ... (ssim = {0:.5f}".format(ssim_val), ")")
   

    if (num_fail > 0):
        print("WARNING: {} of 4 tests failed.".format(num_fail))

    return num_fail
        
def subset_data(ds, subset, lat=None, lon=None, lev=0, start=None, end=None):
    """
    Get a subset of the given dataArray, returns a dataArray
    """
    ds_subset = ds

    ds_subset = ds_subset.isel(time=slice(start, end))

    if subset == 'winter':
        ds_subset = ds_subset.where(ds.time.dt.season == 'DJF', drop=True)
    elif subset == 'spring':
        ds_subset = ds_subset.where(ds.time.dt.season == 'MAM', drop=True)
    elif subset == 'summer':
        ds_subset = ds_subset.where(ds.time.dt.season == 'JJA', drop=True)
    elif subset == 'autumn':
        ds_subset = ds_subset.where(ds.time.dt.season == 'SON', drop=True)

    elif subset == 'first5':
        ds_subset = ds_subset.isel(time=slice(None, 5))

    if 'lev' in ds_subset.dims:
        ds_subset = ds_subset.isel(lev=lev)

    if lat is not None:
        ds_subset = ds_subset.sel(lat=lat, method='nearest')
        ds_subset = ds_subset.expand_dims('lat')

    if lon is not None:
        ds_subset = ds_subset.sel(lon=lon + 180, method='nearest')
        ds_subset = ds_subset.expand_dims('lon')

    return ds_subset
