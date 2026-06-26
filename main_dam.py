import tkinter as tk
from tkinter import messagebox

from Gauss_Seidel import Gauss_Seidel
from gui_inputs import get_inputs_from_gui
from visualization import visualize_results
from comparison import show_comparison_window
from helpers import (auto_step_lines, register_figure_for_save, ask_and_save_all)
import helpers

repetitions = 30000  # Gauss-Seidel
Precision_Gauss_Seidel = 1e-10

def run_one_case(root):
    (L, d, dx, dy, H1, H2, Ananti_user, Katanti_user, K, soil, Gs, e) = get_inputs_from_gui(root)

    Ananti = L - Ananti_user
    Katanti = L - Katanti_user

    helpers.hydraulic_conductivity = K
    helpers.cross_sectional_area = L * d

    step_lines = auto_step_lines(H1, H2, target_lines=10)
    invisible_lines = 0.5 * step_lines

    def critical_hydraulic_gradient(Gs, e):
        i_cr = (Gs - 1) / (1 + e)
        return i_cr

    i_cr = critical_hydraulic_gradient(Gs, e)

    u, u1, L, gap_start, gap_end, rows, cols, Din_1, Din_2, k = Gauss_Seidel(L, d, dx, dy, H1, H2, Ananti, Katanti,repetitions, Precision_Gauss_Seidel)

    soil_type_text = f"Τύπος εδάφους: {soil} (Gs = {Gs:.2f}, e = {e:.2f})"

    i_exit, Q1, Q2, fig = visualize_results(u, L, d, dx, dy,step_lines, rows, cols,Din_1, Din_2,gap_start, gap_end,soil_type_text,iterations=len(u1),i_cr=i_cr,FS=1.0,H1=H1, H2=H2, invisible_lines=invisible_lines)

    FS = None
    if i_exit is not None:
        FS = i_cr / i_exit
        print(f"\nΚρίσιμη κλίση i_cr = {i_cr:.3f}")
        print(f"Κλίση εξόδου (flow net) i_exit = {i_exit:.3f}")
        print(f"Συντελεστής ασφαλείας FS = {FS:.3f}\n")

    register_figure_for_save(fig, "flownet_single.png")

    return {
        "L": L, "d": d, "dx": dx, "dy": dy,
        "H1": H1, "H2": H2,
        "Ananti": Ananti, "Katanti": Katanti,
        "Ananti_user": Ananti_user,    # ← αυτή
        "Katanti_user": Katanti_user,  # ← και αυτή
        "K": K,
        "A": L * d,
        "soil": soil, "Gs": Gs, "e": e,
        "i_cr": i_cr, "i_exit": i_exit, "FS": FS,
        "Q1": Q1, "Q2": Q2,
        "u": u, "rows": rows, "cols": cols,
        "gap_start": gap_start, "gap_end": gap_end,
        "Din_1": Din_1, "Din_2": Din_2,
        "fig": fig,
        "step_lines": step_lines,
        "invisible_lines": invisible_lines,}

# ===========================================================
# MAIN
# ===========================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    # 1ο σενάριο
    res1 = run_one_case(root)
    res2 = None

    ans = messagebox.askyesno(
        "Νέο σενάριο",
        "Θέλεις να τρέξεις νέο σενάριο με διαφορετικές παραμέτρους;")

    if ans:
        res2 = run_one_case(root)
        show_comparison_window(root, res1, res2)

    # ΕΔΩ: μόλις τελειώσουν τα runs και έχουν ανοιχτεί όλα τα figures,ρωτάμε για αποθήκευση.
    ask_and_save_all(root, res1, res2)