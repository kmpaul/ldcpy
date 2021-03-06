from unittest import TestCase

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import ldcpy
from ldcpy.metrics import DatasetMetrics, DiffMetrics

times = pd.date_range('2000-01-01', periods=10)
lats = [0, 1, 2, 3]
lons = [0, 1, 2, 3, 4]
test_data = xr.DataArray(
    np.arange(-100, 100).reshape(4, 5, 10), coords=[lats, lons, times], dims=['lat', 'lon', 'time']
)
test_data_2 = xr.DataArray(
    np.arange(-99, 101).reshape(4, 5, 10), coords=[lats, lons, times], dims=['lat', 'lon', 'time']
)
test_overall_metrics = ldcpy.DatasetMetrics(test_data, ['time', 'lat', 'lon'])
test_spatial_metrics = ldcpy.DatasetMetrics(test_data, ['time'])
test_time_series_metrics = ldcpy.DatasetMetrics(test_data, ['lat', 'lon'])
test_diff_metrics = ldcpy.DiffMetrics(test_data, test_data_2, ['time', 'lat', 'lon'])


class TestErrorMetrics(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._samples = [
            {
                'measured': np.arange(0, 100, dtype='int64'),
                'observed': np.arange(0, 100, dtype='int64'),
                'expected_error': np.zeros(100, dtype='double'),
            }
        ]

    @pytest.mark.nonsequential
    def test_creation_01(self):
        DiffMetrics(
            xr.DataArray(self._samples[0]['observed']),
            xr.DataArray(self._samples[0]['measured']),
            [],
        )

    @pytest.mark.nonsequential
    def test_error_01(self):
        em = DatasetMetrics(
            xr.DataArray(self._samples[0]['observed']) - xr.DataArray(self._samples[0]['measured']),
            [],
        )

        self.assertTrue(all(self._samples[0]['expected_error'] == em.sum))

    @pytest.mark.nonsequential
    def test_mean_error_01(self):
        em = DatasetMetrics(
            xr.DataArray(self._samples[0]['observed']) - xr.DataArray(self._samples[0]['measured']),
            [],
        )
        self.assertTrue(em.mean.all() == 0.0)

    @pytest.mark.nonsequential
    def test_mean_error_02(self):
        em = DatasetMetrics(
            xr.DataArray(self._samples[0]['observed'] - xr.DataArray(self._samples[0]['measured'])),
            [],
        )

        self.assertTrue(em.mean.all() == 0.0)

        em.mean_error = 42.0

        self.assertTrue(em.mean.all() == 0.0)

    @pytest.mark.nonsequential
    def test_TS_02(self):
        import xarray as xr
        import zfpy

        ds = xr.open_dataset('data/cam-fv/orig.TS.100days.nc')

        TS = ds.TS

        print(type(TS))

    @pytest.mark.nonsequential
    def test_mean(self):
        self.assertTrue(test_overall_metrics.mean == -0.5)

    @pytest.mark.nonsequential
    def test_mean_abs(self):
        self.assertTrue(test_overall_metrics.mean_abs == 50)

    @pytest.mark.nonsequential
    def test_mean_squared(self):
        self.assertTrue(np.isclose(test_overall_metrics.mean_squared, 0.25, rtol=1e-09))

    @pytest.mark.nonsequential
    def test_min_abs(self):
        self.assertTrue(test_overall_metrics.min_abs == 0)

    @pytest.mark.nonsequential
    def test_max_abs(self):
        self.assertTrue(test_overall_metrics.max_abs == 100)

    @pytest.mark.nonsequential
    def test_min_val(self):
        self.assertTrue(test_overall_metrics.min_val == -100)

    @pytest.mark.nonsequential
    def test_max_val(self):
        self.assertTrue(test_overall_metrics.max_val == 99)

    @pytest.mark.nonsequential
    def test_ns_con_var(self):
        self.assertTrue(test_overall_metrics.ns_con_var == 2500)  # is this right?

    @pytest.mark.nonsequential
    def test_ew_con_var(self):
        self.assertTrue(test_overall_metrics.ew_con_var == 400)  # is this right?

    @pytest.mark.nonsequential
    def test_odds_positive(self):
        self.assertTrue(np.isclose(test_overall_metrics.odds_positive, 0.98019802, rtol=1e-09))

    @pytest.mark.nonsequential
    def test_prob_negative(self):
        self.assertTrue(test_overall_metrics.prob_negative == 0.5)

    @pytest.mark.nonsequential
    def test_prob_positive(self):
        self.assertTrue(test_overall_metrics.prob_positive == 0.495)

    @pytest.mark.nonsequential
    def test_dyn_range(self):
        self.assertTrue(test_overall_metrics.dyn_range == 199)

    @pytest.mark.nonsequential
    def test_corr_lag1(self):
        self.assertTrue(np.isnan(test_overall_metrics.corr_lag1).all())  # is this right?

    @pytest.mark.nonsequential
    def test_lag1(self):
        self.assertTrue(test_overall_metrics.lag1.all() == 0)  # is this right?

    @pytest.mark.nonsequential
    def test_median(self):
        self.assertTrue(test_overall_metrics.get_metric('quantile', 0.5) == -0.5)

    @pytest.mark.nonsequential
    def test_rms(self):
        self.assertTrue(np.isclose(test_overall_metrics.get_metric('rms'), 57.73647028, rtol=1e-09))

    @pytest.mark.nonsequential
    def test_std(self):
        self.assertTrue(np.isclose(test_overall_metrics.get_metric('std'), 57.73430523, rtol=1e-09))

    @pytest.mark.nonsequential
    def test_sum(self):
        self.assertTrue(test_overall_metrics.get_metric('sum') == -100)

    @pytest.mark.nonsequential
    def test_variance(self):
        self.assertTrue(test_overall_metrics.get_metric('variance') == 3333.25)

    @pytest.mark.nonsequential
    def test_zscore(self):
        self.assertTrue(
            np.isclose(test_overall_metrics.get_metric('zscore'), -0.02738647, rtol=1e-09)
        )

    @pytest.mark.nonsequential
    def test_mean_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('mean')
                == np.array(
                    [
                        [-95.5, -85.5, -75.5, -65.5, -55.5],
                        [-45.5, -35.5, -25.5, -15.5, -5.5],
                        [4.5, 14.5, 24.5, 34.5, 44.5],
                        [54.5, 64.5, 74.5, 84.5, 94.5],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_mean_abs_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('mean_abs')
                == np.array(
                    [
                        [95.5, 85.5, 75.5, 65.5, 55.5],
                        [45.5, 35.5, 25.5, 15.5, 5.5],
                        [4.5, 14.5, 24.5, 34.5, 44.5],
                        [54.5, 64.5, 74.5, 84.5, 94.5],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_mean_squared_spatial(self):
        self.assertTrue(
            np.isclose(
                test_spatial_metrics.get_metric('mean_squared'),
                np.array(
                    [
                        [9120.25, 7310.25, 5700.25, 4290.25, 3080.25],
                        [2070.25, 1260.25, 650.25, 240.25, 30.25],
                        [20.25, 210.25, 600.25, 1190.25, 1980.25],
                        [2970.25, 4160.25, 5550.25, 7140.25, 8930.25],
                    ]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_min_abs_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('min_abs')
                == np.array(
                    [
                        [91.0, 81.0, 71.0, 61.0, 51.0],
                        [41.0, 31.0, 21.0, 11.0, 1.0],
                        [0.0, 10.0, 20.0, 30.0, 40.0],
                        [50.0, 60.0, 70.0, 80.0, 90.0],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_max_abs_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('max_abs')
                == np.array(
                    [
                        [100.0, 90.0, 80.0, 70.0, 60.0],
                        [50.0, 40.0, 30.0, 20.0, 10.0],
                        [9.0, 19.0, 29.0, 39.0, 49.0],
                        [59.0, 69.0, 79.0, 89.0, 99.0],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_min_val_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('min_val')
                == np.array(
                    [
                        [-100.0, -90.0, -80.0, -70.0, -60.0],
                        [-50.0, -40.0, -30.0, -20.0, -10.0],
                        [0.0, 10.0, 20.0, 30.0, 40.0],
                        [50.0, 60.0, 70.0, 80.0, 90.0],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_max_val_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('max_val')
                == np.array(
                    [
                        [-91.0, -81.0, -71.0, -61.0, -51.0],
                        [-41.0, -31.0, -21.0, -11.0, -1.0],
                        [9.0, 19.0, 29.0, 39.0, 49.0],
                        [59.0, 69.0, 79.0, 89.0, 99.0],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_ns_con_var_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('ns_con_var')
                == np.array(
                    [
                        [2500.0, 2500.0, 2500.0, 2500.0, 2500.0],
                        [2500.0, 2500.0, 2500.0, 2500.0, 2500.0],
                        [2500.0, 2500.0, 2500.0, 2500.0, 2500.0],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_odds_positive_spatial(self):
        self.assertTrue(
            np.isclose(
                test_spatial_metrics.get_metric('odds_positive'),
                np.array(
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [9.0, np.inf, np.inf, np.inf, np.inf],
                        [np.inf, np.inf, np.inf, np.inf, np.inf],
                    ]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_prob_positive_spatial(self):
        self.assertTrue(
            np.isclose(
                test_spatial_metrics.get_metric('prob_positive'),
                np.array(
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.9, 1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0, 1.0],
                    ]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_prob_negative_spatial(self):
        self.assertTrue(
            np.isclose(
                test_spatial_metrics.get_metric('prob_negative'),
                np.array(
                    [
                        [1.0, 1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0, 1.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                    ]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_median_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('quantile', 0.5)
                == np.array(
                    [
                        [-95.5, -85.5, -75.5, -65.5, -55.5],
                        [-45.5, -35.5, -25.5, -15.5, -5.5],
                        [4.5, 14.5, 24.5, 34.5, 44.5],
                        [54.5, 64.5, 74.5, 84.5, 94.5],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_rms_spatial(self):
        self.assertTrue(
            np.isclose(
                test_spatial_metrics.get_metric('rms'),
                np.array(
                    [
                        [95.54318395, 85.54823201, 75.55461601, 65.56294685, 55.57427462],
                        [45.5905692, 35.61600764, 25.66125484, 15.76388277, 6.20483682],
                        [5.33853913, 14.7817455, 24.66779277, 34.61935875, 44.59260028],
                        [54.57563559, 64.56392181, 74.55534857, 84.54880248, 94.54364072],
                    ]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_std_spatial(self):
        self.assertTrue(
            np.isclose(
                test_spatial_metrics.get_metric('std'),
                np.array(
                    [
                        [2.87228132, 2.87228132, 2.87228132, 2.87228132, 2.87228132],
                        [2.87228132, 2.87228132, 2.87228132, 2.87228132, 2.87228132],
                        [2.87228132, 2.87228132, 2.87228132, 2.87228132, 2.87228132],
                        [2.87228132, 2.87228132, 2.87228132, 2.87228132, 2.87228132],
                    ]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_sum_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('sum')
                == np.array(
                    [
                        [-955.0, -855.0, -755.0, -655.0, -555.0],
                        [-455.0, -355.0, -255.0, -155.0, -55.0],
                        [45.0, 145.0, 245.0, 345.0, 445.0],
                        [545.0, 645.0, 745.0, 845.0, 945.0],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_variance_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('variance')
                == np.array(
                    [
                        [8.25, 8.25, 8.25, 8.25, 8.25],
                        [8.25, 8.25, 8.25, 8.25, 8.25],
                        [8.25, 8.25, 8.25, 8.25, 8.25],
                        [8.25, 8.25, 8.25, 8.25, 8.25],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_zscore_spatial(self):
        self.assertTrue(
            np.isclose(
                test_spatial_metrics.get_metric('zscore'),
                np.array(
                    [
                        [-105.14203957, -94.13240192, -83.12276427, -72.11312662, -61.10348896],
                        [-50.09385131, -39.08421366, -28.07457601, -17.06493836, -6.05530071],
                        [4.95433694, 15.96397459, 26.97361225, 37.9832499, 48.99288755],
                        [60.0025252, 71.01216285, 82.0218005, 93.03143815, 104.0410758],
                    ]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_corr_lag1_spatial(self):
        self.assertTrue(np.isnan(test_spatial_metrics.get_metric('corr_lag1')).all())

    @pytest.mark.nonsequential
    def test_ew_con_var_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('ew_con_var')
                == np.array(
                    [
                        [100.0, 100.0, 100.0, 100.0, 1600.0],
                        [100.0, 100.0, 100.0, 100.0, 1600.0],
                        [100.0, 100.0, 100.0, 100.0, 1600.0],
                        [100.0, 100.0, 100.0, 100.0, 1600.0],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_lag1_spatial(self):
        self.assertTrue(
            (
                test_spatial_metrics.get_metric('lag1')
                == np.array(
                    [
                        [
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                        [
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                        [
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                        [
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                    ]
                )
            ).all()
        )

    @pytest.mark.nonsequential
    def test_mean_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('mean'),
                np.array([-5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_mean_abs_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('mean_abs'),
                np.array([50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_mean_squared_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('mean_squared'),
                np.array([25.0, 16.0, 9.0, 4.0, 1.0, 0.0, 1.0, 4.0, 9.0, 16.0]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_max_abs_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('max_abs'),
                np.array([100.0, 99.0, 98.0, 97.0, 96.0, 95.0, 96.0, 97.0, 98.0, 99.0]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_max_val_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('max_val'),
                np.array([90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0, 97.0, 98.0, 99.0]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_min_abs_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('min_abs'),
                np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_min_val_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('min_val'),
                np.array([-100.0, -99.0, -98.0, -97.0, -96.0, -95.0, -94.0, -93.0, -92.0, -91.0]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_ns_con_var_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('ns_con_var'),
                np.array(
                    [2500.0, 2500.0, 2500.0, 2500.0, 2500.0, 2500.0, 2500.0, 2500.0, 2500.0, 2500.0]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_odds_positive_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('odds_positive'),
                np.array([0.81818182, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_prob_negative_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('prob_negative'),
                np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_prob_positive_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('prob_positive'),
                np.array([0.45, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_median_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('quantile', 0.5),
                np.array([-5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_rms_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('rms'),
                np.array(
                    [
                        57.87918451,
                        57.80138407,
                        57.74080013,
                        57.69748695,
                        57.67148342,
                        57.66281297,
                        57.67148342,
                        57.69748695,
                        57.74080013,
                        57.80138407,
                    ]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_std_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('std'),
                np.array(
                    [
                        57.66281297,
                        57.66281297,
                        57.66281297,
                        57.66281297,
                        57.66281297,
                        57.66281297,
                        57.66281297,
                        57.66281297,
                        57.66281297,
                        57.66281297,
                    ]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_sum_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('sum'),
                np.array([-100.0, -80.0, -60.0, -40.0, -20.0, 0.0, 20.0, 40.0, 60.0, 80.0]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_variance_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('variance'),
                np.array(
                    [3325.0, 3325.0, 3325.0, 3325.0, 3325.0, 3325.0, 3325.0, 3325.0, 3325.0, 3325.0]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_zscore_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('zscore'),
                np.array(
                    [
                        -0.27420425,
                        -0.2193634,
                        -0.16452255,
                        -0.1096817,
                        -0.05484085,
                        0.0,
                        0.05484085,
                        0.1096817,
                        0.16452255,
                        0.2193634,
                    ]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_corr_lag1_time_series(self):
        self.assertTrue(np.isnan(test_time_series_metrics.corr_lag1).all())

    @pytest.mark.nonsequential
    def test_ew_con_var_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('ew_con_var'),
                np.array([400.0, 400.0, 400.0, 400.0, 400.0, 400.0, 400.0, 400.0, 400.0, 400.0]),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_lag1_time_series(self):
        self.assertTrue(
            np.isclose(
                test_time_series_metrics.get_metric('lag1'),
                np.array(
                    [
                        [
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                        [
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                        [
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                        [
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                    ]
                ),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_diff_pcc(self):
        self.assertTrue(
            np.isclose(
                test_diff_metrics.get_diff_metric('pearson_correlation_coefficient'),
                np.array(1.0),
                rtol=1e-09,
            ).all()
        )

    @pytest.mark.nonsequential
    def test_diff_ksp(self):
        self.assertTrue(
            np.isclose(
                test_diff_metrics.get_diff_metric('ks_p_value'), np.array(0.005), rtol=1e-09
            ).all()
        )

    @pytest.mark.nonsequential
    def test_diff_covariance(self):
        self.assertTrue(
            np.isclose(
                test_diff_metrics.get_diff_metric('covariance'), np.array(3333.25), rtol=1e-09
            ).all()
        )

    @pytest.mark.nonsequential
    def test_diff_normalized_max_pointwise_error(self):
        self.assertTrue(
            np.isclose(
                test_diff_metrics.get_diff_metric('n_emax'), np.array(0.00502513), rtol=1e-09
            ).all()
        )

    @pytest.mark.nonsequential
    def test_diff_normalized_root_mean_squared(self):
        self.assertTrue(
            np.isclose(
                test_diff_metrics.get_diff_metric('n_rms'), np.array(0.00502513), rtol=1e-09
            ).all()
        )
