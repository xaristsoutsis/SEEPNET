def compute_exit_gradient_piping(u, dx, dy, gap_end, rows,ax=None,toe_offset_cols=1,bottom_offset_rows=1):

    rows_u, cols_u = u.shape

    # 1) στήλη toe (κατάντι)
    col_toe = gap_end + toe_offset_cols
    col_toe = max(1, min(cols_u - 2, col_toe))

    # 2) κάτω ζώνη κοντά στο αδιαπέρατο
    row_bottom = bottom_offset_rows          # π.χ. 1 κελί πάνω από το κάτω όριο
    row_top    = row_bottom + 1              # το αμέσως από πάνω κελί

    if row_top >= rows:
        print("[exit_piping] row_top >= rows → δεν μπορώ να υπολογίσω i_exit.")
        return None, None, None

    # 3) heads & μήκος
    h_top    = u[row_top, col_toe]
    h_bottom = u[row_bottom, col_toe]

    delta_h = abs(h_bottom - h_top)
    delta_l = (row_top - row_bottom) * dy

    if delta_l == 0:
        print("[exit_piping] delta_l = 0 → δεν μπορώ να υπολογίσω i_exit.")
        return None, None, None

    i_exit = delta_h / delta_l
    return i_exit, (row_top, col_toe), (row_bottom, col_toe)