import geopandas as gpd
from typing import Union


def clip_gdf(
    gdf: gpd.GeoDataFrame,
    min_x: Union[None, float] = None,
    min_y: Union[None, float] = None,
    max_x: Union[None, float] = None,
    max_y: Union[None, float] = None,
    clip_mask: Union[None, gpd.GeoDataFrame, gpd.GeoSeries] = None,
) -> gpd.GeoDataFrame:
    """This function will return the intersected features of the gdf geodataframe intersecting with a mask clip mask, or boundaries for x and y values

    Args:
        gdf (gpd.GeoDataFrame): input geodataframe
        min_x (Union[None,float], optional):  minimum x coordinate boundary of intersecting polygons to plot. Defaults to None.
        min_y (Union[None,float], optional): maximum x coordinate boundary of intersecting polygons to plot. Defaults to None.
        max_x (Union[None,float], optional): minimum y coordinate boundary of intersecting polygons to plot Defaults to None.
        max_y (Union[None,float], optional): maximum y coordinate boundary of intersecting polygons to plot. Defaults to None.
        clip_mask (Union[None, gpd.GeoDataFrame, gpd.GeoSeries], optional): mask polygon data to clip the dataset to, overrides min_x, max_x, min_y, max_y. Defaults to None.

    Returns:
        gpd.GeoDataFrame: output geodataframe that is the intersection of gdf, and the boundaries defined.
    """

    if isinstance(clip_mask, (gpd.GeoDataFrame, gpd.GeoSeries)) == True:
        if type(clip_mask) == gpd.GeoSeries:
            clip_mask = gpd.GeoDataFrame(geometry=clip_mask)
        return gpd.sjoin(gdf, clip_mask, how="inner", lsuffix="")

    else:
        return gdf.cx[min_x:max_x, min_y:max_y]
