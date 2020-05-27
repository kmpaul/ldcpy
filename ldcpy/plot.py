import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
#import matplotlib as mpl
import cartopy
import cartopy.crs as ccrs
import cmocean
from cartopy.util import add_cyclic_point
import math
import scipy.stats as ss

###############

def compare_mean(ds, varname, ens_o, ens_r, method_str, nlevs=24):
    """
    visualize mean value at each grid point for orig and compressed (time-series)
    assuming FV data and put the weighted mean
    """
    mean_data_o = ds[varname].sel(ensemble=ens_o).mean(dim='time')
    mean_data_r = ds[varname].sel(ensemble=ens_r).mean(dim='time')


    #weighted mean
    gw = ds['gw'].values
    o_wt_mean = np.average(np.average(mean_data_o,axis=0, weights=gw))
    r_wt_mean = np.average(np.average(mean_data_r,axis=0, weights=gw))

    title_1 = f"mean = {o_wt_mean:.2f}"
    title_2 = f"mean = {r_wt_mean:.2f}"
    color = "cmo.thermal"

    compare_plot(mean_data_o, mean_data_r, varname, method_str, title_1, title_2, color, nlevs)

###############

def compare_std(ds, varname, ens_o, ens_r, method_str, nlevs=24):
    """
    TODO: visualize std dev at each grid point for orig and compressed (time-series)
    assuming FV mean
    """
    std_data_o = ds[varname].sel(ensemble=ens_o).std(dim='time', ddof=1)
    std_data_r = ds[varname].sel(ensemble=ens_r).std(dim='time', ddof=1)
    title="std"
    color = "coolwarm"

    compare_plot(std_data_o, std_data_r, varname, method_str, title, title, color, nlevs)

###############

def compare_con_var(ds, varname, ens_o, ens_r, method_str, nlevs=24, dir="NS"):
    """
    TODO: visualize contrast variance at each grid point for orig and compressed (time-series)
    assuming FV mean
    """

    assert dir in ["NS", "EW"], "direction must be NS or EW"
    if dir == "NS":
        lat_length = ds[varname].sel(ensemble=ens_o).sizes['lat']
        o_1, o_2 = xr.align(ds[varname].sel(ensemble=ens_o).head({'lat': lat_length-1}),
                        ds[varname].sel(ensemble=ens_o).tail({'lat': lat_length-1}), join='override')
        r_1, r_2 = xr.align(ds[varname].sel(ensemble=ens_r).head({'lat': lat_length-1}),
                        ds[varname].sel(ensemble=ens_r).tail({'lat': lat_length-1}), join='override')
    else:
        lon_length = ds[varname].sel(ensemble=ens_o).sizes['lon']
        ds[varname].sel(ensemble=ens_o).head({'lon': lon_length-1})
        o_1, o_2 = xr.align(ds[varname].sel(ensemble=ens_o),
                            xr.concat([ds[varname].sel(ensemble=ens_o).tail({'lon': lon_length-1}),
                                       ds[varname].sel(ensemble=ens_o).head({'lon': 1})], dim="lon"), join='override')
        r_1, r_2 = xr.align(ds[varname].sel(ensemble=ens_r),
                            xr.concat([ds[varname].sel(ensemble=ens_r).tail({'lon': lon_length-1}),
                                       ds[varname].sel(ensemble=ens_r).head({'lon': 1})], dim="lon"), join='override')

    con_var_o = xr.ufuncs.square((o_1 - o_2)).mean(dim='time')
    con_var_r = xr.ufuncs.square((r_1 - r_2)).mean(dim='time')
    log_con_var_data_o = xr.ufuncs.log10(con_var_o)
    log_con_var_data_r = xr.ufuncs.log10(con_var_r)

    title=f"{dir} con_var"
    color="binary_r"
    compare_plot(log_con_var_data_o, log_con_var_data_r, varname, method_str, title, title, color, nlevs)

###############

def _odds_rain(ds, ens_o, ens_r, method_str, nlevs=24):
    data_o = ds["PRECT"].sel(ensemble=ens_o)
    data_r = ds["PRECT"].sel(ensemble=ens_r)

    rain_days_o = data_o > 0
    # Adding one rainy and one dry day?
    prob_rain_o = (rain_days_o.sum(dim="time") ) / (rain_days_o.sizes["time"] )
    odds_rain_o = prob_rain_o / (1 - prob_rain_o)
    log_odds_o = xr.ufuncs.log10(odds_rain_o)

    rain_days_r = data_r > 0
    # Adding one rainy and one dry day?
    prob_rain_r = (rain_days_r.sum(dim="time") ) / (rain_days_r.sizes["time"] )
    odds_rain_r = prob_rain_r / (1 - prob_rain_r)
    log_odds_r = xr.ufuncs.log10(odds_rain_r)
    return log_odds_o, log_odds_r


def odds_rain_ratio(ds, ens_o, ens_r, method_str, nlevs=24):
    log_odds_o, log_odds_r = _odds_rain(ds, ens_o, ens_r, method_str, nlevs=24)
    odds_ratio = log_odds_r / log_odds_o
    plot_error("log10(odds ratio)", odds_ratio, "PRECT", method_str)


def compare_odds_rain(ds, ens_o, ens_r, method_str, nlevs=24):
    log_odds_o, log_odds_r = _odds_rain(ds, ens_o, ens_r, method_str, nlevs=24)
    compare_plot(log_odds_o, log_odds_r, "PRECT", method_str, "log10(odds rain)", "log10(odds rain)", "coolwarm")


def compare_neg_rain(ds, ens_o, ens_r, method_str, nlevs=24):
    data_o = ds["PRECT"].sel(ensemble=ens_o)
    data_r = ds["PRECT"].sel(ensemble=ens_r)

    neg_rain_days_o = data_o < 0
    prob_neg_rain_o = (neg_rain_days_o.sum(dim="time") ) / (neg_rain_days_o.sizes["time"] )

    neg_rain_days_r = data_r < 0
    prob_neg_rain_r = (neg_rain_days_r.sum(dim="time") ) / (neg_rain_days_r.sizes["time"] )
    compare_plot(prob_neg_rain_o, prob_neg_rain_r, "PRECT", method_str, "P(neg rainfall)", "P(neg rainfall)", "binary")

def neg_rain_error(ds, ens_o, ens_r, method_str, nlevs=24):
    data_o = ds["PRECT"].sel(ensemble=ens_o)
    data_r = ds["PRECT"].sel(ensemble=ens_r)

    neg_rain_days_o = data_o < 0
    prob_neg_rain_o = (neg_rain_days_o.sum(dim="time") ) / (neg_rain_days_o.sizes["time"] )

    neg_rain_days_r = data_r < 0
    prob_neg_rain_r = (neg_rain_days_r.sum(dim="time") ) / (neg_rain_days_r.sizes["time"] )
    plot_error("P(neg rain) error", prob_neg_rain_o-prob_neg_rain_r, "PRECT", method_str)


def compare_plot(ds_o, ds_r, varname, method_str, title_1, title_2, color, nlevs=24):
    lat_o = ds_o['lat']
    lat_r = ds_r['lat']
    cy_data_o, lon_o = add_cyclic_point(ds_o, coord=ds_o['lon'])
    cy_data_r, lon_r = add_cyclic_point(ds_r, coord=ds_r['lon'])
    fig = plt.figure(dpi=300, figsize=(9, 2.5))

    mymap = plt.get_cmap(f"{color}")

    # both plots use same contour levels
    levels = _calc_contour_levels(cy_data_o, cy_data_r, nlevs)

    ax1 = plt.subplot(1, 2, 1, projection=ccrs.Robinson(central_longitude=0.0))
    title_1 = f'orig:{varname}: {title_1}'
    ax1.set_title(title_1)
    pc1 = ax1.contourf(lon_o, lat_o, cy_data_o, transform=ccrs.PlateCarree(), cmap=mymap, levels=levels)
    ax1.set_global()
    ax1.coastlines()

    ax2 = plt.subplot(1, 2, 2, projection=ccrs.Robinson(central_longitude=0.0))
    title_2 = f'{method_str}:{varname}: {title_2}'
    ax2.set_title(title_2)
    pc2 = ax2.contourf(lon_r, lat_r, cy_data_r, transform=ccrs.PlateCarree(), cmap=mymap, levels=levels)
    ax2.set_global()
    ax2.coastlines()

    # add colorbar
    fig.subplots_adjust(left=0.1, right=0.9, bottom=0.05, top=0.95)
    cax = fig.add_axes([0.1, 0, 0.8, 0.05])
    cbar = fig.colorbar(pc1, cax=cax, orientation='horizontal')
    cbar.ax.tick_params(labelsize=8, rotation=30)


def mean_error(ds, varname, ens_o, ens_r, method_str):
    e = ds[varname].sel(ensemble=ens_o) - ds[varname].sel(ensemble=ens_r)
    mean_e = e.mean(dim='time')
    plot_error("mean error", mean_e, varname, method_str)


def std_error(ds, varname, ens_o, ens_r, method_str):
    e = ds[varname].sel(ensemble=ens_o) - ds[varname].sel(ensemble=ens_r)
    std_e = e.std(dim='time', ddof=1)
    plot_error("std error", std_e, varname, method_str)


def con_var_error(ds, varname, ens_o, ens_r, method_str, dir):
    e = ds[varname].sel(ensemble=ens_o) - ds[varname].sel(ensemble=ens_r)

    assert dir in ["NS", "EW"], "direction must be NS or EW"
    if dir == "NS":
        lat_length = e.sizes['lat']
        o_1, o_2 = xr.align(e.head({'lat': lat_length - 1}),
                            e.tail({'lat': lat_length - 1}), join='override')
    else:
        lon_length = e.sizes['lon']
        e.head({'lon': lon_length - 1})
        o_1, o_2 = xr.align(e,
                            xr.concat([e.tail({'lon': lon_length - 1}),
                                       e.head({'lon': 1})], dim="lon"), join='override')

    con_var_e = xr.ufuncs.square((o_1 - o_2)).mean(dim='time')
    log_con_var_data_e = xr.ufuncs.log10(con_var_e)
    plot_error(f"{dir} con_var error", log_con_var_data_e, varname, method_str)


def zscore_error(ds, varname, ens_o, ens_r, method_str):
    data_o = ds[varname].sel(ensemble=ens_o)
    data_r = ds[varname].sel(ensemble=ens_r)
    diff_data = data_o - data_r

    diff_data_mean = diff_data.mean(dim="time")
    diff_data_sd = diff_data.std(dim='time', ddof=1)

    z_data = np.divide(diff_data_mean, diff_data_sd / np.sqrt(diff_data.sizes["time"]))

    pvals = 2 * (1 - ss.norm.cdf(np.abs(z_data)))
    sorted_pvals = np.sort(pvals).flatten()
    fdr_zscore = 0.01
    p = np.argwhere(sorted_pvals <= fdr_zscore * np.arange(1, pvals.size+1) / pvals.size)
    pval_cutoff = sorted_pvals[p[len(p)-1]]
    if(not(pval_cutoff.size == 0)):
        zscore_cutoff = ss.norm.ppf(1-pval_cutoff)
        sig_locs = np.argwhere(pvals <= pval_cutoff)
        percent_sig = (100 * np.size(sig_locs, 0)/pvals.size)
    else:
        zscore_cutoff = 'na'
        percent_sig = 0

    title = f"z-score error: cutoff {zscore_cutoff[0]:.2f}, % sig: {percent_sig:.2f}"

    plot_error(title, z_data, varname, method_str)


def plot_error(name, ds, varname, method_str):
    """
    visualize the mean error
    want to be able to input multiple?
    """

    lat = ds['lat']
    cy_data, lon = add_cyclic_point(ds, coord=ds['lon'])
    myfig = plt.figure(dpi=300)

    mymap = plt.get_cmap('coolwarm')
    nlevs = 24

    ax = plt.subplot(1, 1, 1, projection=ccrs.Robinson(central_longitude=0.0))
    pc = ax.pcolormesh(lon, lat, cy_data, transform=ccrs.PlateCarree(), cmap=mymap)
#    pc = ax.contourf(lon, lat, cy_data, transform=ccrs.PlateCarree(), cmap=mymap, levels=nlevs)
    cb = plt.colorbar(pc, orientation='horizontal', shrink=.95)
    cb.ax.tick_params(labelsize=8, rotation=30)

    ax.set_global()
    ax.coastlines()
    title = f'{varname} ({method_str}): {name}'
    ax.set_title(title)

###############

def error_time_series(ds, varname, ens_o, ens_r):
    """
    error time series
    """
    pass

###############

def _calc_contour_levels(dat_1, dat_2, nlevs):
    """
    TODO: minval returns the smallest value not equal to -inf, is there a more elegant solution to plotting -inf values
    (for EW contrast variance in particular)?
    """
    # both plots use same contour levels
    minval = np.nanmin(np.minimum(dat_1, dat_2))
    if(minval == -math.inf):
        minval = np.minimum(dat_1[np.isfinite(dat_1)].min(), dat_2[np.isfinite(dat_2)].min())
    maxval = np.nanmax(np.maximum(dat_1, dat_2))
    if (maxval == math.inf):
        maxval = np.maximum(dat_1[np.isfinite(dat_1)].max(), dat_2[np.isfinite(dat_2)].max())
    levels = minval + np.arange(nlevs+1)*(maxval - minval)/nlevs
    #print('Min value: {}\nMax value: {}'.format(minval, maxval))
    return levels