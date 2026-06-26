def Gauss_Seidel(L, d, dx, dy, H1, H2, Ananti, Katanti, repetitions,Precision_Gauss_Seidel):
    import numpy as np
    Din_1 = H1 + d
    Din_2 = H2 + d

    gap_start_Meters = (L - Ananti)
    gap_end_Meters   = (L - Katanti)

    gap_start = int((L - Ananti) / dx) + 1
    gap_end   = int((L - Katanti) / dx) + 1

    cols = int(L / dx) + 1
    rows = int(d / dy) + 1



    u = np.zeros((rows, cols))
    u[:, :] = (Din_1 + Din_2) / 2

    # Οριακές συνθήκες πάνω ορίου (επιφάνεια)
    for j in range(cols):
        x_position = j * dx
        if x_position < gap_start_Meters:
            u[0, j] = Din_1
        elif x_position == gap_start_Meters:
            u[0, j] = Din_1
        elif gap_start_Meters < x_position < gap_end_Meters:
            u[0, j] = 0.0
        elif x_position >= gap_end_Meters:
            u[0, j] = Din_2

    # Αριστερό/δεξί όριο
    u[:, 0]  = Din_1
    u[:, -1] = Din_2

    u1 = []

    print(f"\nΔιαστάσεις πλέγματος: {rows} x {cols}")
    print(f"Βήμα οριζόντιο (dx): {dx}, Βήμα κάθετο (dy): {dy}")
    print(f"Φράγμα: {gap_end_Meters - gap_start_Meters}m "
          f"από {gap_start_Meters}m μέχρι {gap_end_Meters}m")

    for k in range(repetitions):
        u_old = u.copy()

        # Εσωτερικοί κόμβοι
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                u[i, j] = 0.25 * (
                    u[i - 1, j] + u[i + 1, j] +
                    u[i, j - 1] + u[i, j + 1]
                )

        # Κάτω από το φράγμα
        for j in range(gap_start, gap_end - 1):
            u[0, j] = 0.25 * ((2 * u[1, j]) + u[0, j - 1] + u[0, j + 1])

        # Αδιαπέρατο κάτω όριο
        for j in range(1, cols - 1):
            u[-1, j] = 0.25 * (
                (2 * u[-2, j]) + u[-1, j - 1] + u[-1, j + 1]
            )

        u1.append(float(round(u[1, 1], 4)))

        convergence_error = np.max(np.abs(u - u_old))
        if k % 5000 == 0 and k != 0:
            print(f"Επανάληψη {k}: Απόσταση Σύγκλισης = {convergence_error:.6e}, "
                  f"u[1,1] = {u[1,1]:.8f}")

        if convergence_error < Precision_Gauss_Seidel:
            print(f"\n✅ Σύγκλιση επιτεύχθηκε στην επανάληψη {k} "
                  f"(σφάλμα {convergence_error:.6e})")
            break

    print("\nΤελικός πίνακας:")
    for i in range(rows):
        line = "["
        for j in range(cols):
            line += f"{u[i, j]:8.4f}"
            if j < cols - 1:
                line += " "
        line += "]"
        print(line)
    print(f"Αριθμός επαναλήψεων για σύγκλιση: {len(u1)}")

    return u, u1, L, gap_start, gap_end, rows, cols, Din_1, Din_2,k