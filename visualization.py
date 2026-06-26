import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

from Gap_Lines import Gap_Lines, Plot_Gap_Lines
from Flow_Lines import Flow_Lines
from Flow_Rate import Flow_Rate_1, Flow_Rate_2_Columns
from Exit_Gradient import compute_exit_gradient_piping
import helpers



def visualize_results(u, L, d, dx, dy,step_lines, rows, cols, Din_1, Din_2, gap_start, gap_end,soil_type_text, iterations,i_cr,FS, H1, H2,invisible_lines, ax=None):
    created_fig = False
    if ax is None:
        aspect = (L / d)
        fig, ax = plt.subplots(figsize=(14, 14 / aspect))
        created_fig = True
    else:
        fig = ax.figure

    plt.sca(ax)

    im = ax.imshow( u,cmap='jet', aspect='auto',vmin=min(Din_1, Din_2),vmax=max(Din_1, Din_2),origin='upper', extent=[0, L / dx, 0, d / dy])

    # --- Auto-scaled ticks ---
    tick_step_x = helpers.auto_tick_step(L)
    tick_step_y = helpers.auto_tick_step(d)

    x_tick_positions = np.arange(0, cols, tick_step_x / dx)
    x_tick_labels = (x_tick_positions * dx).astype(int)
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels)

    y_tick_positions = np.arange(0, rows, tick_step_y / dy)
    y_tick_labels = (y_tick_positions * dy).astype(int)
    ax.set_yticks(y_tick_positions)
    ax.set_yticklabels(y_tick_labels)

    cbar = fig.colorbar(im,ax=ax,orientation='horizontal',fraction=0.046,pad=0.10)
    cbar.set_label('Δυναμικό (m)')

    ax.set_title('Κατανομή Δυναμικού κάτω από Φράγμα')
    ax.set_xlabel(f"Συνολικό Μήκος: {L} μέτρα")
    ax.set_ylabel(f"Βάθος Αδιαπέρατου: {d} μέτρα")

    # Ισοδυναμικές
    plt.sca(ax)
    Points_For_Each_Line, Lines_XY_Points = Gap_Lines(u, step_lines, rows, cols, Din_1, Din_2, invisible_lines)
    Plot_Gap_Lines(Points_For_Each_Line, rows)

    # Γραμμές ροής
    plt.sca(ax)
    Flow_Lines( rows, cols, Lines_XY_Points, gap_start, helpers.How_Many_Flow_Lines, helpers.n_interpolations)

    # Παροχές
    # 1η μέθοδος: ισοδυναμικές
    mean_du_1, mean_distance_1 = Flow_Rate_1(cols, rows, Points_For_Each_Line, u, dx, dy, helpers.n_interpolations)

    # Αν για κάποιο λόγο δεν έχει τεθεί το A, υπολόγισέ το ως L*d
    if helpers.cross_sectional_area is None:
        helpers.cross_sectional_area = L * d

    K_day = helpers.hydraulic_conductivity         # m/day (από τον χρήστη)
    K_sec = K_day / 86400.0                        # m/s
    A = helpers.cross_sectional_area               # m²

    Q_1 = K_sec * A * (mean_du_1 / mean_distance_1)   # m³/s

    # 2η μέθοδος: στήλες κατάντι
    mean_du_2, distance_2 = Flow_Rate_2_Columns(u, gap_end, 1.0, dx)
    Q_2 = K_sec * A * (mean_du_2 / distance_2)        # m³/s

    # Κλίση εξόδου
    plt.sca(ax)
    i_exit_piping, pt_top, pt_bot = compute_exit_gradient_piping(u, dx, dy, gap_end, rows, ax=ax,toe_offset_cols=1,bottom_offset_rows=1 )

    # Τραπέζιο φράγματος (σε κόμβους)
    x_base_left  = gap_start - 1
    x_base_right = gap_end
    base_length_nodes = x_base_right - x_base_left
    dam_height_nodes = 1.5 * (H1 / dy)

    y_base = d / dy
    y_top  = y_base + dam_height_nodes

    BL = (x_base_left, y_base)
    BR = (x_base_right, y_base)
    TL = (x_base_left, y_top)
    TR = (x_base_right - (0.85 * base_length_nodes), y_top)
    SQ_D_R = (x_base_right, y_base)
    curve_rise = dam_height_nodes * 0.15
    SQ_U_R = (x_base_right, y_base + curve_rise)

    x1, y1 = TR
    x2, y2 = SQ_U_R
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    vx, vy = x2 - x1, y2 - y1
    nx, ny = -vy, vx
    norm = np.hypot(nx, ny)
    if norm > 0:
        nx, ny = nx / norm, ny / norm
    h_curve = base_length_nodes * 0.1
    TR_2_in = (mx - nx * h_curve, my - ny * h_curve)

    verts = [BR, BL, TL, TR, TR_2_in, SQ_U_R, SQ_D_R, BR]
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO,
             Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CLOSEPOLY]

    path = Path(verts, codes)
    patch = PathPatch(path, facecolor='tan', edgecolor='black', alpha=1, zorder=6)
    ax.add_patch(patch)

    # Νερά ανάντι / κατάντι
    y_water_upstream   = (d + H1) / dy - 1
    y_water_downstream = (d + H2) / dy - 1

    x_upstream_start   = 0
    x_upstream_end     = gap_start 
    

    x_downstream_start = (gap_end + gap_start)/2
    x_downstream_end   = cols - 1

    ax.hlines(y_water_upstream, x_upstream_start, x_upstream_end,
              colors='dodgerblue', linewidth=2)
    ax.hlines(y_water_downstream, x_downstream_start, x_downstream_end,
              colors='dodgerblue', linewidth=2)

    ax.fill_between([x_upstream_start, x_upstream_end],
                    y_base, y_water_upstream,
                    color='dodgerblue', alpha=0.6)

    ax.fill_between([x_downstream_start, x_downstream_end],
                    y_base, y_water_downstream,
                    color='dodgerblue', alpha=0.6)

    text_offset_y = dam_height_nodes * 0.05 + 0.5
    ax.text((x_upstream_start + x_upstream_end) / 2, y_water_upstream + text_offset_y,
            f'H1 = {H1} m', color='deepskyblue', ha='center')

    x_mid_down = (x_downstream_start + x_downstream_end) / 2
    ax.text(x_mid_down, y_water_downstream + text_offset_y,
            f'H2 = {H2} m', color='dodgerblue', ha='center')

    fig.tight_layout()

    if created_fig:
        fig.show()

    return i_exit_piping, Q_1, Q_2, fig