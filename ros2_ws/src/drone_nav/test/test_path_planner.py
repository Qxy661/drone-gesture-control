"""Path planner unit tests"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from drone_nav.path_planner import GridMap, AStarPlanner, RRTPlanner, RRTStarPlanner
from drone_nav.coordinate_utils import enu_to_ned, ned_to_enu, gps_to_enu


def test_astar_simple():
    m = GridMap(20, 20, 0.1)
    planner = AStarPlanner(m)
    path = planner.plan((0, 0), (19, 19))
    assert path is not None
    assert path[0] == (0, 0)
    assert path[-1] == (19, 19)
    print(f"  A* clear grid: {len(path)} waypoints")

def test_astar_with_obstacle():
    m = GridMap(20, 20, 0.1)
    # Partial wall at x=10, y=0..14 (gap at y=15..19)
    for y in range(15):
        m.set_obstacle(10, y)
    planner = AStarPlanner(m)
    path = planner.plan((0, 10), (19, 10))
    assert path is not None
    assert all(m.is_free(x, y) for x, y in path)
    print(f"  A* with wall: {len(path)} waypoints")

def test_astar_no_solution():
    m = GridMap(20, 20, 0.1)
    # Complete wall
    for y in range(20):
        m.set_obstacle(10, y)
    m.set_obstacle(0, 0)  # start blocked
    planner = AStarPlanner(m)
    path = planner.plan((0, 0), (19, 19))
    assert path is None
    print("  A* blocked: correctly returned None")

def test_rrt_finds_path():
    m = GridMap(50, 50, 0.1)
    planner = RRTPlanner(m, step_size=0.5, max_iter=3000)
    path = planner.plan((0.5, 0.5), (4.5, 4.5))
    assert path is not None
    print(f"  RRT clear: {len(path)} waypoints")

def test_rrt_star_finds_path():
    m = GridMap(50, 50, 0.1)
    planner = RRTStarPlanner(m, step_size=0.5, max_iter=3000)
    path = planner.plan((0.5, 0.5), (4.5, 4.5))
    assert path is not None
    print(f"  RRT* clear: {len(path)} waypoints")

def test_coordinate_conversion():
    x, y, z = 1.0, 2.0, 3.0
    xn, yn, zn = enu_to_ned(x, y, z)
    xe, ye, ze = ned_to_enu(xn, yn, zn)
    assert abs(xe - x) < 1e-6
    assert abs(ye - y) < 1e-6
    assert abs(ze - z) < 1e-6
    print("  ENU<->NED: OK")

def test_gps_conversion():
    lat, lon, alt = 39.9042, 116.4074, 50.0
    ref_lat, ref_lon, ref_alt = 39.9040, 116.4070, 0.0
    x, y, z = gps_to_enu(lat, lon, alt, ref_lat, ref_lon, ref_alt)
    print(f"  GPS->ENU: ({x:.1f}, {y:.1f}, {z:.1f}) meters from ref")


if __name__ == "__main__":
    print("=== Path Planner Tests ===")
    test_astar_simple()
    test_astar_with_obstacle()
    test_astar_no_solution()
    test_rrt_finds_path()
    test_rrt_star_finds_path()
    test_coordinate_conversion()
    test_gps_conversion()
    print("=== ALL TESTS PASSED ===")
