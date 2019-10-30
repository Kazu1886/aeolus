"""Science calculations."""
from .calculus import integrate
from .diag import (
    ghe_norm,
    heat_redist_eff,
    minmaxdiff,
    region_mean_diff,
    sfc_net_energy,
    sfc_water_balance,
    toa_cloud_radiative_effect,
    toa_eff_temp,
    toa_net_energy,
    total_precip,
)
from .stats import last_year_mean, meridional_mean, spatial, spatial_quartiles

__all__ = (
    "integrate",
    "ghe_norm",
    "heat_redist_eff",
    "minmaxdiff",
    "sfc_net_energy",
    "sfc_water_balance",
    "region_mean_diff",
    "toa_cloud_radiative_effect",
    "toa_eff_temp",
    "toa_net_energy",
    "total_precip",
    "last_year_mean",
    "meridional_mean",
    "spatial",
    "spatial_quartiles",
)
