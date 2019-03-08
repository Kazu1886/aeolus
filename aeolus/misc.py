# -*- coding: utf-8 -*-
"""Miscellaneous."""
import warnings

import iris

import numpy as np

from .coord_utils import nearest_coord_value


def vertical_cross_section_area(cube2d, r_planet):
    """Create a cube of vertical cross-section areas in metres."""
    cube2d = cube2d.copy()
    m_per_deg = (np.pi / 180) * r_planet
    if iris.util.guess_coord_axis(cube2d.dim_coords[1]) == "X":
        m_per_deg *= np.cos(np.deg2rad(cube2d.coord(axis="Y").points[0]))

    for dim_coord in cube2d.dim_coords:
        if not dim_coord.has_bounds():
            dim_coord.guess_bounds()
    x_bounds = cube2d.coord(cube2d.dim_coords[1]).bounds
    z_bounds = cube2d.coord(cube2d.dim_coords[0]).bounds

    vc_area = cube2d.copy(
        data=(z_bounds[:, 1] - z_bounds[:, 0])[:, None]
        * ((x_bounds[:, 1] - x_bounds[:, 0])[None, :] * m_per_deg)
    )
    vc_area.units = "m**2"
    vc_area.rename("vertical_section_area")
    for dim_coord in vc_area.dim_coords:
        dim_coord.bounds = None
    return vc_area


def net_horizontal_flux_to_region(
    scalar_cube, latlon_box_dict, u, v, r_planet, vertical_constraint=None
):
    """Calculate horizontal fluxes of `scalar_cube` quantity and add them to get the net result."""
    ll_other = {"longitude": "latitude", "latitude": "longitude"}
    perpendicular_wind_cmpnts = {"longitude": u, "latitude": v}

    total_h_fluxes = []
    for i, (ll_coord, ll_val) in enumerate(latlon_box_dict.items()):
        this_coord = ll_coord[:-1]
        other_coord = ll_other[ll_coord[:-1]]
        nearest = nearest_coord_value(scalar_cube, this_coord, ll_val)
        if abs(nearest - ll_val) > 10:
            warnings.warn(
                f"Nearest value is {np.round(nearest - ll_val, 2)} deg away"
                f" from the given value of {this_coord}"
            )
        vcross_cnstr = iris.Constraint(**{this_coord: nearest})
        other_min = latlon_box_dict[f"{other_coord}0"]
        other_max = latlon_box_dict[f"{other_coord}1"]
        if vertical_constraint is not None:
            vcross_cnstr &= vertical_constraint
        if other_max >= other_min:
            vcross_cnstr &= iris.Constraint(
                **{other_coord: lambda x: other_min <= x <= other_max}
            )
            cube = scalar_cube.extract(vcross_cnstr)
        else:
            vcross_cnstr &= iris.Constraint(
                **{other_coord: lambda x: (other_max >= x) or (other_min <= x)}
            )
            cube = scalar_cube.extract(vcross_cnstr)
        vcross_area = vertical_cross_section_area(cube, r_planet=r_planet)

        # Calculate energy flux (2d)
        cube = (
            perpendicular_wind_cmpnts[this_coord].extract(vcross_cnstr)
            * scalar_cube.extract(vcross_cnstr)
            * vcross_area
        )
        # Total flux
        cube_total = cube.collapsed(cube.dim_coords, iris.analysis.SUM)
        total_h_fluxes.append(cube_total)

    net_flux = (total_h_fluxes[0] - total_h_fluxes[1]) + (
        total_h_fluxes[2] - total_h_fluxes[3]
    )
    net_flux.rename(f"net_{scalar_cube.name()}_horizontal_flux_to_region")

    return net_flux
