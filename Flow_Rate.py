How_Many_Flow_Lines = 4
n_interpolations = 100

def Flow_Rate_1(cols, rows, Points_For_Each_Line, u, dx, dy,n_interpolations):
    import numpy as np
    import math
    
    # 1) Πάρε τις 2 ΜΙΚΡΟΤΕΡΕΣ ισοδυναμικές
    sorted_keys_asc = sorted(Points_For_Each_Line.keys())
    two_smallest_keys = sorted_keys_asc[:2]
    dense_points_two_lines = {}

    for line_value in two_smallest_keys:
        xy_points = Points_For_Each_Line[line_value]
        if len(xy_points) < 2:
            continue

        dense_between = []
        for j in range(len(xy_points) - 1):
            iA, xA_interp, _, _, _ = xy_points[j]
            iB, xB_interp, _, _, _ = xy_points[j + 1]

            yA = float(iA)
            yB = float(iB)

            for k in range(1, n_interpolations + 1):
                t = k / (n_interpolations + 1)
                x_t = xA_interp + t * (xB_interp - xA_interp)
                y_t = yA        + t * (yB        - yA)
                dense_between.append((x_t, y_t))

        full_dense = []
        for j in range(len(xy_points) - 1):
            iA, xA_interp, _, _, _ = xy_points[j]
            full_dense.append((xA_interp, float(iA)))
            for k in range(n_interpolations):
                full_dense.append(dense_between[j * n_interpolations + k])
        i_last, x_last_interp, _, _, _ = xy_points[-1]
        full_dense.append((x_last_interp, float(i_last)))

        # bilinear interpolation στο u (όπως πριν, δεν πειράζουμε εδώ)
        dense_with_potential = []
        for (x_t, y_t) in full_dense:
            x0 = int(np.floor(x_t))
            y0 = int(np.floor(y_t))
            x1 = x0 + 1
            y1 = y0 + 1

            if x0 < 0: x0 = 0
            if y0 < 0: y0 = 0
            if x1 >= cols: x1 = cols - 1
            if y1 >= rows: y1 = rows - 1

            if x0 == x1 and y0 == y1:
                u_interp = u[y0, x0]
            else:
                dx_loc = x_t - x0
                dy_loc = y_t - y0
                u00 = u[y0, x0]
                u10 = u[y0, x1]
                u01 = u[y1, x0]
                u11 = u[y1, x1]
                u_x0 = u00 * (1 - dx_loc) + u10 * dx_loc
                u_x1 = u01 * (1 - dx_loc) + u11 * dx_loc
                u_interp = u_x0 * (1 - dy_loc) + u_x1 * dy_loc
            dense_with_potential.append((x_t, y_t, u_interp))
        dense_points_two_lines[line_value] = dense_with_potential

    line_values = sorted(dense_points_two_lines.keys())
    if len(line_values) < 2:
        print("Δεν υπάρχουν δύο γραμμές με πυκνωμένα σημεία.")
        return 0.0, 0.0

    line1 = line_values[0]
    line2 = line_values[1]
    pts1 = dense_points_two_lines[line1]
    pts2 = dense_points_two_lines[line2]
    pts1_sorted = sorted(pts1, key=lambda p: (p[0], p[1]))  # (x, y, u)
    pts2_sorted = sorted(pts2, key=lambda p: (p[0], p[1]))
    n = min(len(pts1_sorted), len(pts2_sorted))

    distances = []
    for i in range(n):
        x1, y1, _ = pts1_sorted[i]
        x2, y2, _ = pts2_sorted[i]
        # διαφορές σε ΚΟΜΒΟΥΣ
        dx_nodes = x2 - x1
        dy_nodes = y2 - y1
        # μετατροπή σε ΜΕΤΡΑ
        dx_m = dx_nodes * dx
        dy_m = dy_nodes * dy

        dist_m = math.hypot(dx_m, dy_m)
        distances.append(dist_m)

    if distances:
        mean_distance = sum(distances) / len(distances)
    else:
        mean_distance = 0.0
    mean_du = line2 - line1
    return mean_du, mean_distance


def Flow_Rate_2_Columns(u, gap_end, target_L_m, dx, ax=None):

    import numpy as np
    rows, cols = u.shape
    # Υπολογισμός διαθέσιμου μήκους κατάντι από το gap_end
    remaining_length_m = (cols - 1 - gap_end) * dx

    if remaining_length_m <= 0:
        # Δεν υπάρχει καθόλου χώρος κατάντι
        target_L_m = dx  # έστω 1 βήμα
    else:
        # Πάρε π.χ. 20% του διαθέσιμου μήκους
        target_L_m = 0.2 * remaining_length_m

        # Περιορισμός σε λογικό εύρος
        target_L_m = max(0.5, min(target_L_m, 5.0))


    # μετατροπή μέτρων -> κόμβοι
    Dist = int(round(target_L_m / dx))
    if Dist < 1:
        Dist = 1

    j1 = gap_end
    j2 = gap_end + Dist

    if j2 >= cols:
        print(f"⚠️ j2 = {j2} εκτός πλέγματος (cols = {cols}). Μείωσε το target_L_m ή άλλαξε το πλέγμα.")
        return 0.0, 0.0

    Distance_2 = Dist * dx  # πραγματική L σε m

    du_list = []
    for i in range(rows):
        u1 = u[i, j1]
        u2 = u[i, j2]
        du_list.append(u1 - u2)

    if not du_list:
        print("Δεν βρέθηκαν κόμβοι για υπολογισμό Δφ.")
        return 0.0, 0.0

    mean_du = float(np.mean(du_list))
    return mean_du, Distance_2