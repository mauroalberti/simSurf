# -*- coding: utf-8 -*-

import os
from typing import Dict, Tuple, Union, List

from osgeo import ogr, osr

from .exceptions import *


def try_open_shapefile(path: str) -> Tuple[bool, Union["OGRLayer", str]]:

    dataSource = ogr.Open(path)

    if dataSource is None:
        return False, "Unable to open shapefile in provided path"

    shapelayer = dataSource.GetLayer()

    return True, shapelayer


def read_line_shapefile_via_ogr(line_shp_path: str) -> Dict:
    """
    Read line shapefile using OGR.

    :param  line_shp_path:  parameter to check.
    :type  line_shp_path:  QString or string
    """

    # reset layer parameters

    if line_shp_path is None or line_shp_path == '':
        return dict(success=False, error_message='No input path')

        # open input vector layer
    shape_driver = ogr.GetDriverByName("ESRI Shapefile")

    line_shape = shape_driver.Open(str(line_shp_path), 0)

    # layer not read
    if line_shape is None:
        return dict(success=False, error_message='Unable to open input shapefile')

        # get internal layer
    lnLayer = line_shape.GetLayer(0)

    # set vector layer extent
    layer_extent = lnLayer.GetExtent()
    lines_extent = {'xmin': layer_extent[0], 'xmax': layer_extent[1], 'ymin': layer_extent[2], 'ymax': layer_extent[3]}

    # initialize lists storing vertex coordinates of line
    lines_points = []

    # start reading layer features
    curr_line = lnLayer.GetNextFeature()

    # loop in layer features
    while curr_line:

        line_points = []

        line_geom = curr_line.GetGeometryRef()

        if line_geom is None:
            line_shape.Destroy()
            return dict(success=False, error_message='No geometry ref')

        if line_geom.GetGeometryType() != ogr.wkbLineString and \
                        line_geom.GetGeometryType() != ogr.wkbMultiLineString:
            line_shape.Destroy()
            return dict(success=False, error_message='Not a linestring/multilinestring')

        for i in range(line_geom.GetPointCount()):
            x, y, z = line_geom.GetX(i), line_geom.GetY(i), line_geom.GetZ(i)

            line_points.append((x, y, z))

        lines_points.append(line_points)

        curr_line = lnLayer.GetNextFeature()

    line_shape.Destroy()

    return dict(success=True, extent=lines_extent, vertices=lines_points)


def parse_ogr_type(ogr_type_str: str) -> 'ogr.OGRFieldType':
    """
    Parse the provided textual field type to return an actual OGRFieldType.

    :param ogr_type_str: the string referring to the ogr field type.
    :type ogr_type_str: str.
    :return: the actural ogr type.
    :rtype: OGRFieldType.
    :raise: Exception.
    """

    if ogr_type_str.endswith("OFTInteger"):
        return ogr.OFTInteger
    elif ogr_type_str.endswith("OFTIntegerList"):
        return ogr.OFTIntegerList
    elif ogr_type_str.endswith("OFTReal"):
        return ogr.OFTReal
    elif ogr_type_str.endswith("OFTRealList"):
        return ogr.OFTRealList
    elif ogr_type_str.endswith("OFTString"):
        return ogr.OFTString
    elif ogr_type_str.endswith("OFTStringList"):
        return ogr.OFTStringList
    elif ogr_type_str.endswith("OFTBinary"):
        return ogr.OFTBinary
    elif ogr_type_str.endswith("OFTDate"):
        return ogr.OFTDate
    elif ogr_type_str.endswith("OFTTime"):
        return ogr.OFTTime
    elif ogr_type_str.endswith("OFTDateTime"):
        return ogr.OFTDateTime
    elif ogr_type_str.endswith("OFTInteger64"):
        return ogr.OFTInteger64
    elif ogr_type_str.endswith("OFTInteger64List"):
        return ogr.OFTInteger64List
    else:
        raise Exception("Debug: not recognized ogr type")


def shapefile_create_def_field(field_def):
    """

    :param field_def:
    :return:
    """

    name = field_def['name']
    ogr_type = parse_ogr_type(field_def['ogr_type'])

    fieldDef = ogr.FieldDefn(name, ogr_type)
    if ogr_type == ogr.OFTString:
        fieldDef.SetWidth(int(field_def['width']))

    return fieldDef


def shapefile_create(path, geom_type, fields_dict_list, crs=None):
    """
    crs_prj4: projection in Proj4 text format
    geom_type = OGRwkbGeometryType: ogr.wkbPoint, ....
    list of:
        field dict: 'name',
                    'type': ogr.OFTString,
                            ogr.wkbLineString,
                            ogr.wkbLinearRing,
                            ogr.wkbPolygon,

                    'width',
    """

    driver = ogr.GetDriverByName("ESRI Shapefile")

    outShapefile = driver.CreateDataSource(str(path))
    if outShapefile is None:
        raise OGRIOException('Unable to save shapefile in provided path')

    if crs is not None:
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromProj4(crs)
        outShapelayer = outShapefile.CreateLayer("layer", spatial_reference, geom_type)
    else:
        outShapelayer = outShapefile.CreateLayer("layer", None, geom_type)

    if not outShapelayer:
        return None, None

    for field_def_params in fields_dict_list:
        field_def = shapefile_create_def_field(field_def_params)
        outShapelayer.CreateField(field_def)

    return outShapefile, outShapelayer


def try_write_point_shapefile(path: str, field_names: List[str], values: List[Tuple], ndx_x_val: int) -> Tuple[bool, str]:
    """
    Add point records in an existing shapefile, filling attribute values.
    The point coordinates, i.e. x, y, z start at ndx_x_val index (index is zero-based) and are
    assumed to be sequential in order (i.e., 0, 1, 2 or 3, 4, 5).

    :param path: the path of the existing shapefile in which to write.
    :type path: string.
    :param field_names: the field names of the attribute table.
    :type field_names: list of strings.
    :param values: the values for each record.
    :type values: list of tuple.
    :param ndx_x_val: the index of the x coordinate. Y and z should follow.
    :type ndx_x_val: int.
    :return: success status and related messages.
    :rtype: tuple of a boolean and a string.
    """

    success = False
    msg = ""

    try:

        dataSource = ogr.Open(path, 1)

        if dataSource is None:
            return False, "Unable to open shapefile in provided path"

        point_layer = dataSource.GetLayer()

        outshape_featdef = point_layer.GetLayerDefn()

        for ndx, pt_vals in enumerate(values):

            # pre-processing for new feature in output layer
            curr_Pt_geom = ogr.Geometry(ogr.wkbPoint)
            curr_Pt_geom.AddPoint(pt_vals[ndx_x_val], pt_vals[ndx_x_val+1], pt_vals[ndx_x_val+2])

            # create a new feature
            curr_pt_shape = ogr.Feature(outshape_featdef)
            curr_pt_shape.SetGeometry(curr_Pt_geom)

            for ndx, fld_nm in enumerate(field_names):

                curr_pt_shape.SetField(fld_nm, pt_vals[ndx])

            # add the feature to the output layer
            point_layer.CreateFeature(curr_pt_shape)

            # destroy no longer used objects
            curr_Pt_geom.Destroy()
            curr_pt_shape.Destroy()

        del outshape_featdef
        del point_layer
        del dataSource

        success = True

    except Exception as e:

        msg = e

    finally:

        return success, msg


def try_write_line_shapefile(path: str, field_names: List[str], values: Dict) -> Tuple[bool, str]:
    """
    Add point records in an existing shapefile, filling attribute values.


    :param path: the path of the existing shapefile in which to write.
    :type path: string.
    :param field_names: the field names of the attribute table.
    :type field_names: list of strings.
    :param values: the values for each record.
    :type values: dict with values made up by two dictionaries.
    :return: success status and related messages.
    :rtype: tuple of a boolean and a string.
    """

    success = False
    msg = ""

    try:

        dataSource = ogr.Open(path, 1)

        if dataSource is None:
            return False, "Unable to open shapefile in provided path"

        line_layer = dataSource.GetLayer()

        outshape_featdef = line_layer.GetLayerDefn()

        for id in sorted(values.keys()):

            # pre-processing for new feature in output layer
            line_geom = ogr.Geometry(ogr.wkbLineString)

            for id_xyz in values[id]["pts"]:
                x, y, z = id_xyz
                line_geom.AddPoint(x, y, z)

            # create a new feature
            line_shape = ogr.Feature(outshape_featdef)
            line_shape.SetGeometry(line_geom)

            for ndx, fld_nm in enumerate(field_names):

                line_shape.SetField(fld_nm, values[id]["vals"][ndx])

            # add the feature to the output layer
            line_layer.CreateFeature(line_shape)

            # destroy no longer used objects
            line_geom.Destroy()
            line_shape.Destroy()

        del outshape_featdef
        del line_layer
        del dataSource

        success = True

    except Exception as e:

        msg = str(e)

    finally:

        return success, msg


def ogr_get_solution_shapefile(path, fields_dict_list):
    """

    :param path:
    :param fields_dict_list:
    :return:
    """

    driver = ogr.GetDriverByName("ESRI Shapefile")

    dataSource = driver.Open(str(path), 0)

    if dataSource is None:
        raise OGRIOException("Unable to open shapefile in provided path")

    point_shapelayer = dataSource.GetLayer()

    prev_solution_list = []
    in_point = point_shapelayer.GetNextFeature()
    while in_point:
        rec_id = int(in_point.GetField('id'))
        x = in_point.GetField('x')
        y = in_point.GetField('y')
        z = in_point.GetField('z')
        dip_dir = in_point.GetField('dip_dir')
        dip_ang = in_point.GetField('dip_ang')
        descript = in_point.GetField('descript')
        prev_solution_list.append([rec_id, x, y, z, dip_dir, dip_ang, descript])
        in_point.Destroy()
        in_point = point_shapelayer.GetNextFeature()

    dataSource.Destroy()

    if os.path.exists(path):
        driver.DeleteDataSource(str(path))

    outShapefile, outShapelayer = shapefile_create(path, ogr.wkbPoint25D, fields_dict_list, crs=None)
    return outShapefile, outShapelayer, prev_solution_list