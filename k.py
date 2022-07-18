import gps
import bmx055
import calibration

gps.open_gps()
lat2 = 35.9237822
lon2 = 139.91122508
direction = calibration.calculate_direction(lon2, lat2)
goal_distance = direction['distance']
print(int(goal_distance))