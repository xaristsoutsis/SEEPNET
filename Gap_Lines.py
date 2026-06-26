def Gap_Lines(u, step_lines, rows, cols, Din_1, Din_2,invisible_lines):
    import numpy as np
    surface_min = min(Din_1, Din_2)
    surface_max = max(Din_1, Din_2)

    # -----------------------------
    # 1) ΟΡΑΤΕΣ ισοδυναμικές (step_lines)
    # -----------------------------
    min_rounded_vis = np.ceil(surface_min / step_lines) * step_lines
    max_rounded_vis = np.floor(surface_max / step_lines) * step_lines
    Lines = np.arange(min_rounded_vis, max_rounded_vis + step_lines, step_lines)
    Lines = [L for L in Lines if L != min_rounded_vis and L != max_rounded_vis]
  

    Points_For_Each_Line = {}
    for line_value in Lines:
        points_for_this_line = []
        for i in range(rows):
            for j in range(cols - 1):
                val1 = u[i, j]
                val2 = u[i, j + 1]
                if (val1 - line_value) * (val2 - line_value) < 0:
                    ratio = (line_value - val1) / (val2 - val1)
                    x_interp = j + ratio
                    points_for_this_line.append((i, x_interp, line_value, val1, val2))
        Points_For_Each_Line[line_value] = points_for_this_line
    print(f"\n Οι Γραμμές Δυναμικού που θα σχεδιαστούν είναι: {[float(L) for L in Lines]}")

    # -----------------------------
    # 2) ΑΟΡΑΤΕΣ ισοδυναμικές (invisible_lines) ΜΟΝΟ για Flow_Lines
    # -----------------------------
    min_rounded_inv = np.ceil(surface_min / invisible_lines) * invisible_lines
    max_rounded_inv = np.floor(surface_max / invisible_lines) * invisible_lines
    Inv_Lines = np.arange(min_rounded_inv, max_rounded_inv + invisible_lines, invisible_lines)
    Inv_Lines = [L for L in Inv_Lines if L != min_rounded_inv and L != max_rounded_inv]
    print(f" Οι Γραμμές που θα χρησιμοποιηθούν στις Flow Lines είναι: {[float(L) for L in Inv_Lines]}\n")

    Lines_XY_Points = {}
    for line_value in Inv_Lines:
        xy_points_this_line = []
        for i in range(rows):
            for j in range(cols - 1):
                val1 = u[i, j]
                val2 = u[i, j + 1]
                if (val1 - line_value) * (val2 - line_value) < 0:
                    ratio = (line_value - val1) / (val2 - val1)
                    x_interp = j + ratio
                    xy_points_this_line.append((x_interp, i))
        Lines_XY_Points[line_value] = xy_points_this_line

    return Points_For_Each_Line, Lines_XY_Points

def Plot_Gap_Lines(Points_For_Each_Line, rows):
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import numpy as np

    line_values = sorted(Points_For_Each_Line.keys())
    n_lines = len(line_values)

    base_cmap = cm.get_cmap('tab10', n_lines)

    for idx, line_value in enumerate(line_values):
        points = Points_For_Each_Line[line_value]
        if len(points) < 2:
            continue

        # ταξινόμηση κατά i (κάθετη διεύθυνση)
        points_sorted = sorted(points, key=lambda p: p[0])
        x_coords = [p[1] for p in points_sorted]
        y_coords = [rows - 1 - p[0] for p in points_sorted]

        color = base_cmap(idx)

        # index για το label (προς το "τέλος" της ισοδυναμικής)
        mid_idx = int(0.7 * len(x_coords))
        mid_idx = max(1, min(len(x_coords) - 2, mid_idx))

        # πόσα σημεία αφαιρούμε γύρω από το label για να δημιουργηθεί κενό
        gap_half_width = 1

        left_end = max(0, mid_idx - gap_half_width)
        right_start = min(len(x_coords), mid_idx + gap_half_width + 1)

        # αριστερό μέρος μέχρι πριν το κενό
        if left_end > 1:
            plt.plot(x_coords[:left_end], y_coords[:left_end], '-',color=color,linewidth=2,alpha=0.9)

        # δεξί μέρος μετά το κενό
        if right_start < len(x_coords) - 1:
            plt.plot(x_coords[right_start:], y_coords[right_start:],'-', color=color,linewidth=2,alpha=0.9 )

        # υπολογισμός θέσης label στο ΚΕΝΤΡΟ του κενού
        x_top_gap    = x_coords[mid_idx - gap_half_width]
        y_top_gap    = y_coords[mid_idx - gap_half_width]
        x_bottom_gap = x_coords[mid_idx + gap_half_width]
        y_bottom_gap = y_coords[mid_idx + gap_half_width]

        xm = 0.5 * (x_top_gap + x_bottom_gap)
        ym = 0.5 * (y_top_gap + y_bottom_gap)

        # γωνία από τα δύο άκρα του κενού (ώστε να ταιριάζει με τη γραμμή)
        dx_line = x_bottom_gap - x_top_gap
        dy_line = y_bottom_gap - y_top_gap
        angle = np.degrees(np.arctan2(dy_line, dx_line))
        angle = -angle * 0.5

        plt.text( xm, ym, f"{line_value:.1f}", color="black",fontsize=10,ha="center", va="center",rotation=angle,rotation_mode="anchor",weight='bold')