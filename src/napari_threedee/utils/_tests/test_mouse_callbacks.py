from dataclasses import dataclass
from typing import Tuple, List

import numpy as np

from napari_threedee.utils.mouse_callbacks import add_point_on_plane

@dataclass
class MockEvent:
    position: np.ndarray
    view_direction: np.ndarray
    modifiers: List[str]


def test_add_point_on_plane(make_napari_viewer):
    """Test adding points on a plane with the same scale"""
    # set up the viewer
    viewer = make_napari_viewer()
    viewer.dims.ndisplay = 3

    # set up image layer
    rng = np.random.default_rng(seed=42)
    image = rng.random((20, 20, 20))
    image_layer = viewer.add_image(
        image,
        scale=(1, 1, 1),
        depiction="plane",
        plane={
            'position': (10, 10, 10),
            'normal': (1, 0, 0),
            'thickness': 10,
        },
    )

    # set up points layer
    points_layer = viewer.add_points(ndim=3, scale=(1, 1, 1))

    # add the point
    event = MockEvent(
        position=np.array([12, 10, 10]),
        view_direction=np.array([-1, 0, 0]),
        modifiers=["Alt"]
    )
    add_point_on_plane(
        viewer=viewer,
        event=event,
        points_layer=points_layer,
        image_layer=image_layer,
        replace_selected=False,
    )

    # check the point
    expected_point = np.array([[10, 10, 10]])
    actual_points = points_layer.data
    np.testing.assert_array_equal(actual_points, expected_point)


def test_add_point_on_plane_same_scale(make_napari_viewer):
    """Test adding points on a plane when the layers have same non-[1, 1, 1] scale"""
    # set up the viewer
    viewer = make_napari_viewer()
    viewer.dims.ndisplay = 3

    # set up image layer
    rng = np.random.default_rng(seed=42)
    image = rng.random((10, 40, 40))
    image_layer = viewer.add_image(
        image,
        scale=(2, 0.5, 0.5),
        depiction="plane",
        plane={
            'position': (5, 10, 10), # note this is pixel/data coords
            'normal': (1, 0, 0),
            'thickness': 10,
        },
    )

    # set up points layer
    points_layer = viewer.add_points(ndim=3, scale=(2, 0.5, 0.5))

    # add the point, the event is in scaled coordinates
    event = MockEvent(
        position=np.array([12, 5, 5]),
        view_direction=np.array([-1, 0, 0]),
        modifiers=["Alt"]
    )
    add_point_on_plane(
        viewer=viewer,
        event=event,
        points_layer=points_layer,
        image_layer=image_layer,
        replace_selected=False,
    )

    # check the point, it should be in Point data coordinates
    # because scales are the same, the Point will be located at
    # plane.position z-slice and de-scaled even.position y, x
    expected_point = np.array([[5, 10, 10]])
    actual_points = points_layer.data
    np.testing.assert_array_equal(actual_points, expected_point)


def test_add_point_on_plane_different_scale(make_napari_viewer):
    """Test adding points on a plane when the layers don't have the same scale"""
    # set up the viewer
    viewer = make_napari_viewer()
    viewer.dims.ndisplay = 3

    # set up image layer
    rng = np.random.default_rng(seed=42)
    image = rng.random((10, 40, 40))
    image_layer = viewer.add_image(
        image,
        scale=(2, 0.5, 0.5),
        depiction="plane",
        plane={
            'position': (5, 10, 10),
            'normal': (1, 0, 0),
            'thickness': 10,
        },
    )

    # set up points layer
    points_layer = viewer.add_points(ndim=3, scale=(1, 1, 1))

    # add the point
    event = MockEvent(
        position=np.array([12, 5, 5]),
        view_direction=np.array([-1, 0, 0]),
        modifiers=["Alt"]
    )
    add_point_on_plane(
        viewer=viewer,
        event=event,
        points_layer=points_layer,
        image_layer=image_layer,
        replace_selected=False,
    )

    # check the point, it will be in Point data coordinates
    # (scaled) world coords will be de-scaled by Points scale, so 
    # the world position on the plane should be returned
    expected_point = np.array([[10, 5, 5]])
    actual_points = points_layer.data
    np.testing.assert_array_equal(actual_points, expected_point)