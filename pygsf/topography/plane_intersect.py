# -*- coding: utf-8 -*-


from ..spatial.rasters.geoarray import GeoArray
from ..spatial.rasters.fields import *
from ..spatial.vectorial.vectorial import Point, Segment

from ..orientations.orientations import Plane


def ijarr2xyz(ijarr2xy_func: Callable, xy2z_func: Callable, i: float, j: float) -> Tuple[float, float, float]:
    """
    Return a tuple of (x, y, z) values, starting by array indices.

    :param ijarr2xy_func: a function converting from array to geographic coordinates.
    :param xy2z_func: a callable converting from x, y geographic coordinates to a z value.
    :param i: i index.
    :param j: j index.
    :return: Point
    """

    x, y = ijarr2xy_func(i, j)
    z = xy2z_func(x, y)
    return x, y, z


def xyarr2segmentslope(
        xy2z_func: Callable,
        arrij2xy_func: Callable,
        i: float,
        j: float,
        i_start=0.0,
        j_start=0.0) -> float:
    """
    Calculates the segment slope along a gridded direction defined by its end point i, j array coordinates.
    Assumed start point is array coordinates 0, 0.

    :param xy2z_func: a callable deriving a z value from geographic x-y coordinates..
    :param arrij2xy_func: a function converting from array coordinates to geographic coordinates.
    :param i: i index of end point.
    :param j: j index of end point.
    :param i_start: i index of start point. Default is 0.0.
    :param j_start:j index of start point. Default is 0.0.
    :return: segment slope.
    :rtype: float.
    """

    start_point = Point(*ijarr2xyz(
        ijarr2xy_func=arrij2xy_func,
        xy2z_func=xy2z_func,
        i=i_start,
        j=j_start))

    end_point = Point(*ijarr2xyz(
        ijarr2xy_func=arrij2xy_func,
        xy2z_func=xy2z_func,
        i=i,
        j=j))

    return Segment(start_point, end_point).slope


def segment_intersections_array(
        m_arr1: np.ndarray,
        m_arr2: np.ndarray,
        q_arr1: np.ndarray,
        q_arr2: np.ndarray,
        cell_size: float,
        m_delta_tol: Optional[float]=1e-6,
        q_delta_tol: Optional[float]=1e-6) -> np.ndarray:
    """
    Creates array that gives the residual index [0-1[ of the intersection between segments along the considered
    array axis (i or j) whose m (slope) and q (y-axis intersection) values along the considered array axis (i or j)
    are defined in the two pairs of input arrays.

    :param m_arr1: array storing values of grid 1 segment slopes.
    :param m_arr2: array storing values of grid 2 segment slopes.
    :param q_arr1: array storing values of grid 1 segment y-axis intersections.
    :param q_arr2: array storing values of grid 2 segment y-axis intersections.
    :param cell_size: cell size of the two grids along the considered direction. Required the same in the two grids.
    :param m_delta_tol: optional tolerance for delta between grid 1 and grid 2 segment slopes.
    :param q_delta_tol: optional tolerance for delta between grid 1 and grid 2 segment y-axis intersections.
    :return: array with values of intersection residual indices [0 - 1[
    """

    # if segments slope are not sub-equal, we calculate the intersection residual slope using the required formula

    inters_residual_indices = np.where(abs(m_arr1 - m_arr2) < m_delta_tol, np.NaN, (q_arr2 - q_arr1) / (cell_size * (m_arr1 - m_arr2)))

    # if the elevations at the left cell center are sub-equal,
    # the residual index is set to 0.0, i.e. there is an intersection at the left cell

    inters_with_coincident_starts = np.where(abs(q_arr1 - q_arr2) < q_delta_tol, 0.0, inters_residual_indices)

    # we filter out residual indices that are not within cell span, i.e., not between 0.0 (included) and 1.0 (excluded)

    inters_intracells_residuals = np.where(np.logical_and(inters_with_coincident_starts >= 0.0, inters_with_coincident_starts < 1.0), inters_with_coincident_starts, np.NaN)

    return inters_intracells_residuals


def array2points(direction: str, arr: np.ndarray, ij2xy_func: Callable) -> List[Point]:
    """
    Converts an array of along-direction (i- or j-) intra-cell segments [0 -> 1[ into
    a list of 2D points.

    :param direction: considered intersection direction: 'i' (for i axis) or 'j' (for j axis).
    :param arr: array of along-direction (i- or j-) intra-cell segments [0 -> 1[.
    :param ij2xy_func: function to convert from array indices to x-y geographic coordinates.
    :return: list of Points.:
    :raise: Exception when direction is not 'i' or 'j'
    """

    pts = []
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            val = arr[i, j]
            if np.isfinite(val):
                if direction == 'i':
                    i_int, j_int = i + val, j
                elif direction == 'j':
                    i_int, j_int = i, j + val
                else:
                    raise Exception('Unexpected array direction value: {}'.format(direction))
                x, y = ij2xy_func(i_int, j_int)
                pts.append(Point(x, y))

    return pts


def plane_dem_intersection(
        srcPlaneAttitude: Plane,
        srcPt: Point,
        geo_array: GeoArray,
        level_ndx: int=0) -> Tuple[List[Point], List[Point]]:
    """
    Calculates the intersections (as points) between the grid and a planar analytical surface.

    :param srcPlaneAttitude: orientation of the surface (currently only planes).
    :type srcPlaneAttitude: class Plane.
    :param srcPt: point, expressed in geographical coordinates, that the plane must contain.
    :type srcPt: Point.
    :param geo_array: the input GeoArray storing the used grid.
    :type geo_array: GeoArray.
    :param level_ndx: the grid level to use from the provided geoarray. Default is first (index equal to zero).
    :type level_ndx: integer.
    :return: tuple of two intersection points lists, the first along the j directions, the second along the i directions.

    Examples:
    """

    # dem values as a Numpy array

    q_d = geo_array.level(
        level_ndx=level_ndx)

    # row and column numbers of the dem

    row_num, col_num = q_d.shape

    # plane closure that, given (x, y), derive z

    plane_z_closure = srcPlaneAttitude.closure_plane_from_geo(srcPt)

    # plane elevations at grid cell centers

    q_p = array_from_function(
        row_num=row_num,
        col_num=col_num,
        geotransform=geo_array.gt,
        z_transfer_func=plane_z_closure)

    index_multiplier = 100  # large value to ensure a precise slope values

    mi_p = xyarr2segmentslope(
        xy2z_func=plane_z_closure,
        arrij2xy_func=geo_array.ijArrToxy,
        i=index_multiplier,
        j=0) * np.ones((row_num, col_num))

    mj_p = xyarr2segmentslope(
        xy2z_func=plane_z_closure,
        arrij2xy_func=geo_array.ijArrToxy,
        i=0,
        j=index_multiplier) * np.ones((row_num, col_num))

    # 2D array of DEM segment parameters

    cell_size_j, cell_size_i = geo_array.geotransf_cell_sizes()

    mj_d = grad_j(
        fld=q_d,
        cell_size_j=cell_size_j)

    mi_d = grad_iminus(
        fld=q_d,
        cell_size_i=cell_size_i)

    # intersection points

    intersection_pts_j = segment_intersections_array(
        m_arr1=mj_d,
        m_arr2=mj_p,
        q_arr1=q_d,
        q_arr2=q_p,
        cell_size=cell_size_j)

    intersection_pts_j = array2points(
        direction='j',
        arr=intersection_pts_j,
        ij2xy_func=geo_array.ijArrToxy)

    intersection_pts_i = segment_intersections_array(
        m_arr1=mi_d,
        m_arr2=mi_p,
        q_arr1=q_d,
        q_arr2=q_p,
        cell_size=cell_size_i)

    intersection_pts_i = array2points(
        direction='i',
        arr=intersection_pts_i,
        ij2xy_func=geo_array.ijArrToxy)

    return intersection_pts_j, intersection_pts_i

