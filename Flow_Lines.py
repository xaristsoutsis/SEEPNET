def extend_flowline_to_boundary(flow_line, rows, cols):

    if len(flow_line) < 2:
        return flow_line

    (x_prev, y_prev) = flow_line[-2]
    (x_last, y_last) = flow_line[-1]

    # αν είναι ήδη πολύ κοντά σε κάποιο όριο, μην κάνεις τίποτα
    y_surface = rows - 1
    eps = 1e-6
    if (abs(y_last - y_surface) < eps or
        abs(y_last - 0) < eps or
        abs(x_last - 0) < eps or
        abs(x_last - (cols - 1)) < eps):
        return flow_line

    dx = x_last - x_prev
    dy = y_last - y_prev

    # αν δεν έχουμε κατεύθυνση, σταμάτα
    if abs(dx) < eps and abs(dy) < eps:
        return flow_line

    # κλίση m, χειρισμός κατακόρυφης
    vertical = abs(dx) < eps
    if not vertical:
        m = dy / dx

    candidates = []

    # helper για να κρατάμε μόνο τα "μπροστά" σημεία
    def is_ahead(x_t, y_t):
        vx = x_t - x_last
        vy = y_t - y_last
        dot = vx * dx + vy * dy
        return dot > 0  # θετικό: ίδια κατεύθυνση

    # 1) Τομή με επιφάνεια y = rows - 1
    if not vertical and abs(m) > eps:
        y_t = y_surface
        x_t = x_last + (y_t - y_last) / m
        if 0 - eps <= x_t <= (cols - 1) + eps and is_ahead(x_t, y_t):
            candidates.append((x_t, y_t))

    # 2) Τομή με κάτω y = 0
    if not vertical and abs(m) > eps:
        y_t = 0
        x_t = x_last + (y_t - y_last) / m
        if 0 - eps <= x_t <= (cols - 1) + eps and is_ahead(x_t, y_t):
            candidates.append((x_t, y_t))

    # 3) Τομή με δεξιά x = cols - 1
    x_t = cols - 1
    if not vertical:
        y_t = y_last + m * (x_t - x_last)
    else:
        # κατακόρυφη προς τα πάνω ή κάτω
        if dy > 0:
            y_t = y_surface
        else:
            y_t = 0
    if 0 - eps <= y_t <= y_surface + eps and is_ahead(x_t, y_t):
        candidates.append((x_t, y_t))

    # 4) Τομή με αριστερά x = 0
    x_t = 0
    if not vertical:
        y_t = y_last + m * (x_t - x_last)
        if 0 - eps <= y_t <= y_surface + eps and is_ahead(x_t, y_t):
            candidates.append((x_t, y_t))
    # (για καθαρά κατακόρυφη, αριστερά/δεξιά δεν έχουν νόημα, τα καλύψαμε παραπάνω)

    if not candidates:
        # αν για κάποιο λόγο δεν βρέθηκε τίποτα, μην πειράξεις τη γραμμή
        return flow_line

    # διάλεξε το πιο κοντινό "μπροστά" σημείο
    x_target, y_target = min(
        candidates,
        key=lambda p: (p[0] - x_last) ** 2 + (p[1] - y_last) ** 2
    )

    extended = list(flow_line)
    extended.append((x_target, y_target))
    return extended


def Flow_Lines(rows, cols, Lines_XY_Points, gap_start,
               How_Many_Flow_Lines, n_interpolations):
    import math
    import matplotlib.pyplot as plt

    # ------------------------------------------------------------
    # 1) Start points στην επιφάνεια (σε κόμβους)
    # ------------------------------------------------------------
    start_points_nodes = []
    concentration = 0.8  # μπορείς να το αλλάζεις ελεύθερα
    x_min = gap_start * (1.0 - concentration)
    x_max = gap_start
    spacing_nodes = (x_max - x_min) / (How_Many_Flow_Lines + 1)

    for k in range(1, How_Many_Flow_Lines + 1):
        x_node = x_min + k * spacing_nodes
        y_node = rows - 1
        start_points_nodes.append((x_node, y_node))

    # ------------------------------------------------------------
    # 2) Αντιστροφή y όλων των σημείων (για να ταιριάζει με origin='lower')
    # ------------------------------------------------------------
    all_y = [p[1] for line in Lines_XY_Points.values() for p in line]
    Y_max = max(all_y + [rows - 1])

    for linevalue in Lines_XY_Points:
        Lines_XY_Points[linevalue] = [
            (x, Y_max - y) for x, y in Lines_XY_Points[linevalue]
        ]

    sorted_line_values = sorted(Lines_XY_Points.keys(), reverse=True)

    flow_lines = []

    # ------------------------------------------------------------
    # 3) Για κάθε start point, χτίσε μία γραμμή ροής
    # ------------------------------------------------------------
    for sp_idx, start_point in enumerate(start_points_nodes):
        current_points = [start_point]
        current_source = start_point

        for line_idx, line_value in enumerate(sorted_line_values):
            xy_points = Lines_XY_Points[line_value]
            if len(xy_points) < 2:
                continue

            # --------------------------------------------------------
            # Πύκνωση ισοδυναμικής (γραμμική παρεμβολή)
            # --------------------------------------------------------
            dense_between = []
            for j in range(len(xy_points) - 1):
                xA, yA = xy_points[j]
                xB, yB = xy_points[j + 1]
                for k in range(1, n_interpolations + 1):
                    t = k / (n_interpolations + 1)
                    x_t = xA + t * (xB - xA)
                    y_t = yA + t * (yB - yA)
                    dense_between.append((x_t, y_t))

            full_dense = []
            for j in range(len(xy_points) - 1):
                full_dense.append(xy_points[j])
                for k in range(n_interpolations):
                    full_dense.append(dense_between[j * n_interpolations + k])
            full_dense.append(xy_points[-1])
            xy_points = full_dense

            # --------------------------------------------------------
            # iso_points & iso_slopes
            # --------------------------------------------------------
            iso_points = []
            iso_slopes = []
            for j in range(len(xy_points) - 1):
                xA, yA = xy_points[j]
                xB, yB = xy_points[j + 1]
                iso_points.append((xA, yA))
                if xB != xA:
                    iso_slope = (yB - yA) / (xB - xA)
                else:
                    iso_slope = float('inf')
                iso_slopes.append(iso_slope)
            iso_points.append(xy_points[-1])

            # --------------------------------------------------------
            # Slopes από current_source προς iso_points
            # --------------------------------------------------------
            start_to_iso_slopes = []
            for x_iso, y_iso in iso_points[:-1]:
                if x_iso != current_source[0]:
                    slope_to_iso = (y_iso - current_source[1]) / (x_iso - current_source[0])
                else:
                    slope_to_iso = float('inf')
                start_to_iso_slopes.append(slope_to_iso)

            # --------------------------------------------------------
            # Γινόμενα κλίσεων & γωνίες
            # --------------------------------------------------------
            perpendicular_products = []
            angles_before_interp = []
            for j in range(len(start_to_iso_slopes)):
                if iso_slopes[j] != float('inf') and start_to_iso_slopes[j] != float('inf'):
                    product = iso_slopes[j] * start_to_iso_slopes[j]
                    angle_rad = math.atan(
                        abs((iso_slopes[j] - start_to_iso_slopes[j]) /
                            (1 + iso_slopes[j] * start_to_iso_slopes[j]))
                    )
                    angle_deg = math.degrees(angle_rad)
                    angle_from_perpendicular = abs(90 - angle_deg)
                else:
                    if (iso_slopes[j] == float('inf') and start_to_iso_slopes[j] == 0) or \
                       (start_to_iso_slopes[j] == float('inf') and iso_slopes[j] == 0):
                        product = -1
                        angle_from_perpendicular = 0
                    else:
                        product = float('inf')
                        angle_from_perpendicular = float('inf')

                perpendicular_products.append(product)
                angles_before_interp.append(angle_from_perpendicular)

            # --------------------------------------------------------
            # Επιλογή σημείου με product ~ -1 (ορθογωνικότητα)
            # --------------------------------------------------------
            if perpendicular_products:
                valid_idx = [i for i, p in enumerate(perpendicular_products)
                             if abs(p) != float('inf')]
                if valid_idx:
                    retry = True
                    max_retries = 20
                    retry_count = 0

                    while retry and retry_count < max_retries:
                        # Φίλτρο κλίσεων
                        slope_threshold = 3.0
                        good_valid_idx = [
                            i for i in valid_idx
                            if i < len(start_to_iso_slopes)
                            and abs(start_to_iso_slopes[i]) < slope_threshold
                        ]
                        if not good_valid_idx:
                            good_valid_idx = valid_idx[:]

                        # 1ο / τελευταίο επίπεδο: διαφορετικό score
                        is_first_level = (line_idx == 0)
                        is_last_level  = (line_idx == len(sorted_line_values) - 1)

                        def score(i):
                            x_iso, y_iso = iso_points[i]
                            dx = x_iso - current_source[0]
                            dy = y_iso - current_source[1]
                            dist2 = dx * dx + dy * dy
                            perp_err = abs(perpendicular_products[i] + 1.0)

                            if is_first_level:
                                # πιο δυνατό βάρος στην απόσταση στο 1ο βήμα
                                return perp_err + 0.1 * dist2
                            elif is_last_level:
                                # πολύ δυνατό βάρος στην απόσταση στο ΤΕΛΕΥΤΑΙΟ
                                return perp_err + 0.5 * dist2
                            else:
                                return perp_err + 0.01 * dist2

                        closest_idx = min(good_valid_idx, key=score)

                        if closest_idx == 0:
                            j0, j1 = 0, 1
                        elif closest_idx >= len(iso_points) - 1:
                            j0, j1 = len(iso_points) - 2, len(iso_points) - 1
                        else:
                            j0, j1 = closest_idx, closest_idx + 1

                        x1, y1 = iso_points[j0]
                        x2, y2 = iso_points[j1]
                        p1 = perpendicular_products[j0]
                        p2 = perpendicular_products[j1]

                        if p2 != p1:
                            t_raw = (-1 - p1) / (p2 - p1)
                        else:
                            t_raw = 0.5

                        if abs(t_raw) > 2.0:
                            t_clamped = 0.5
                        else:
                            t_clamped = max(0.25, min(0.75, t_raw))
                        t = t_clamped

                        x_interp = x1 + t * (x2 - x1)
                        y_interp = y1 + t * (y2 - y1)

                        angle1 = angles_before_interp[j0]
                        angle2 = angles_before_interp[j1]
                        final_angle = angle1 + t * (angle2 - angle1)
                        perpendicular_angle = 90 - final_angle
                        angle_error = abs(90 - perpendicular_angle)

                        # Όρια γωνίας: πιο χαλαρό στο 1ο, λίγο ειδικό στο τελευταίο
                        if is_first_level:
                            angle_limit_here = 30.0
                        elif is_last_level:
                            angle_limit_here = 30.0  # πολύ αυστηρή ορθογωνικότητα στην έξοδο
                        else:
                            angle_limit_here = 25.0

                        if angle_error <= angle_limit_here:
                            retry = False
                        else:
                            retry_count += 1
                            if len(valid_idx) > 1:
                                valid_idx = valid_idx[1:]
                            else:
                                retry = False

                    # Αν βρέθηκε σημείο
                    new_point = (x_interp, y_interp)
                    current_points.append(new_point)
                    current_source = new_point

        flow_lines.append(current_points)

    # ------------------------------------------------------------
    # 4) Επέκταση μέχρι επιφάνεια/πλευρές
    # ------------------------------------------------------------
    extended_flow_lines = []
    for fl in flow_lines:
        extended_fl = extend_flowline_to_boundary(fl, rows, cols)
        extended_flow_lines.append(extended_fl)
    flow_lines = extended_flow_lines

    # ------------------------------------------------------------
    # 5) Σχεδίαση
    # ------------------------------------------------------------
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')

    # Start points
    ax.plot(
        [p[0] for p in start_points_nodes],
        [p[1] for p in start_points_nodes],
        'v',
        color='black',
        markersize=5,
        label='Start Points')

    # Γραμμές ροής
    for flow_line in flow_lines:
        x_coords = [p[0] for p in flow_line]
        y_coords = [p[1] for p in flow_line]
        ax.plot(
            x_coords,
            y_coords,
            '--',
            color='black',
            linewidth=2
        )
        for point in flow_line[1:]:
            ax.plot(point[0], point[1], 'o', color='black', markersize=1)