import matplotlib.pyplot as plt

from visualization import visualize_results
from helpers import register_figure_for_save, ask_and_save_all


# ===========================================================
# ΜΟΝΟ figure σύγκρισης 2 flow nets (χωρίς Tk παράθυρο)
# ===========================================================
def show_comparison_window(root, res1, res2):
    # δύο flow nets δίπλα-δίπλα
    fig_comp, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig_comp.suptitle("Σύγκριση flow nets δύο σεναρίων")

    fig_comp.subplots_adjust(
        left=0.06,
        right=0.98,
        bottom=0.08,
        top=0.90,
        wspace=0.30
    )

    # Σενάριο 1
    visualize_results(
        res1["u"], res1["L"], res1["d"], res1["dx"], res1["dy"],
        res1["step_lines"], res1["rows"], res1["cols"],
        res1["Din_1"], res1["Din_2"],
        res1["gap_start"], res1["gap_end"],
        f"Σενάριο 1: {res1['soil']}",
        iterations=len(res1["u"][0]),
        i_cr=res1["i_cr"],
        FS=res1["FS"] if res1["FS"] is not None else 1.0,
        H1=res1["H1"], H2=res1["H2"],
        invisible_lines=res1["invisible_lines"],
        ax=ax1
    )

    # Σενάριο 2
    visualize_results(
        res2["u"], res2["L"], res2["d"], res2["dx"], res2["dy"],
        res2["step_lines"], res2["rows"], res2["cols"],
        res2["Din_1"], res2["Din_2"],
        res2["gap_start"], res2["gap_end"],
        f"Σενάριο 2: {res2['soil']}",
        iterations=len(res2["u"][0]),
        i_cr=res2["i_cr"],
        FS=res2["FS"] if res2["FS"] is not None else 1.0,
        H1=res2["H1"], H2=res2["H2"],
        invisible_lines=res2["invisible_lines"],
        ax=ax2
    )

    register_figure_for_save(fig_comp, "flownet_comparison.png")
    fig_comp.show()