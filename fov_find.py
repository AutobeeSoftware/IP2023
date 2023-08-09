
import numpy as np
##################
# Prepare
w, h = 1280, 720 #### ??
fx, fy = 1027.3, 1026.9 #### ??

# Go
fov_x = np.rad2deg(2 * np.arctan2(w, 2 * fx))
fov_y = np.rad2deg(2 * np.arctan2(h, 2 * fy))
print(fov_x)
print(fov_y)
##############