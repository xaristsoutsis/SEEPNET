import numpy as np
import matplotlib.pyplot as plt
import os
from tkinter import messagebox


How_Many_Flow_Lines = 4
n_interpolations = 100

# Το A θα υπολογίζεται δυναμικά ως L*d (m²) για κάθε σενάριο
cross_sectional_area   = None   # A (m²)

# Η K δίνεται από τον χρήστη σε m/day (gui_inputs -> main_dam)
# και μέσα στους υπολογισμούς η Q θα βγαίνει σε m³/s.
hydraulic_conductivity = None   # K (m/day)

FIGURES_TO_SAVE = []   # λίστα (fig, default_name)
ASKED_SAVE_ONCE = False

def auto_step_lines(H1, H2, target_lines=10):
    """
    Υπολογίζει αυτόματα το βήμα ισοδυναμικών γραμμών
    ώστε να υπάρχουν περίπου target_lines γραμμές στο διάγραμμα.
    Στρογγυλοποιεί σε "ωραίο" αριθμό (1, 2, 5, 10, 20, 50, ...).
    """
    delta_h = abs(H1 - H2)
    if delta_h == 0:
        return 1.0
    raw_step = delta_h / target_lines
    magnitude = 10 ** np.floor(np.log10(raw_step))
    candidates = [1 * magnitude, 2 * magnitude, 5 * magnitude, 10 * magnitude]
    best = min(candidates, key=lambda s: abs(delta_h / s - target_lines))
    return float(best)


def auto_tick_step(total_length, target_ticks=7):
    """
    Υπολογίζει αυτόματα το βήμα των ticks στους άξονες
    ώστε να υπάρχουν περίπου target_ticks ticks.
    Στρογγυλοποιεί σε "ωραίο" αριθμό.
    """
    if total_length == 0:
        return 1.0
    raw = total_length / target_ticks
    magnitude = 10 ** np.floor(np.log10(raw))
    candidates = [1 * magnitude, 2 * magnitude, 5 * magnitude, 10 * magnitude]
    best = min(candidates, key=lambda s: abs(total_length / s - target_ticks))
    return float(best)


# ===========================================================
# Βοηθητικές συναρτήσεις παραμετρικής ανάλυσης
# ===========================================================
def compute_downstream_uplift(res):
    """
    Υπολογίζει ένα αντιπροσωπευτικό uplift κατάντι από τον πίνακα u.
    Παίρνουμε μέση τιμή δυναμικού σε μια στενή λωρίδα γύρω από το toe κατάντι.
    """
    u = res["u"]
    rows = res["rows"]
    cols = res["cols"]
    gap_end = res["gap_end"]

    col_toe = int(gap_end)
    col_toe = max(0, min(cols - 1, col_toe))

    r_bottom = rows - 1
    r_top = max(0, rows - 4)

    strip = u[r_top:r_bottom+1, col_toe]
    uplift = float(np.mean(strip))
    return uplift

def compute_mean_gradient(res):
    """Μέση υδραυλική κλίση i_mean = ΔH / L_base (μήκος βάσης φράγματος)"""
    base_m = (res["gap_end"] - res["gap_start"]) * res["dx"]
    dh = res["H1"] - res["H2"]
    if base_m > 0:
        return dh / base_m
    return 0.0


def compute_upstream_uplift(res):
    """Μέσο δυναμικό στο ανάντι πόδι φράγματος"""
    u = res["u"]
    rows = res["rows"]
    col_toe = int(res["gap_start"])
    col_toe = max(0, min(res["cols"] - 1, col_toe))
    r_bottom = rows - 1
    r_top = max(0, rows - 4)
    strip = u[r_top:r_bottom+1, col_toe]
    return float(np.mean(strip))

# ===========================================================
# Αποθήκευση figures
# ===========================================================
def unique_png_path(base_dir, base_name):
    """Επιστρέφει μοναδικό path (π.χ. flownet_single.png, flownet_single_1.png, ...)"""
    name, ext = os.path.splitext(base_name)
    i = 1
    path = os.path.join(base_dir, base_name)
    while os.path.exists(path):
        path = os.path.join(base_dir, f"{name}_{i}{ext}")
        i += 1
    return path


def register_figure_for_save(fig, default_name):
    """Καταχώρηση figure για μαζική αποθήκευση στο τέλος."""
    FIGURES_TO_SAVE.append((fig, default_name))


def ask_and_save_all(parent_window, res1=None, res2=None):
    """
    Ρωτά μία φορά και αποθηκεύει όλα τα fig σε PNG.
    Αν δοθούν res1,res2, φτιάχνει και PNG με πίνακα σύγκρισης.
    """
    global ASKED_SAVE_ONCE
    if ASKED_SAVE_ONCE:
        return

    # ===== 1. Πίνακας σύγκρισης σε PNG =====
    if res1 is not None and res2 is not None:
        fig_txt, ax_txt = plt.subplots(figsize=(9, 5))
        ax_txt.axis("off")

        def mark_values(v1, v2, larger_is_better=True, fmt="{:.4f}", digits=4):
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                if digits == 0:
                    s1 = f"{int(v1)}"
                    s2 = f"{int(v2)}"
                else:
                    s1 = fmt.format(v1)
                    s2 = fmt.format(v2)
            else:
                s1 = str(v1)
                s2 = str(v2)

            up = "↑"
            down = "↓"
            if larger_is_better:
                if v1 > v2:
                    s1 = s1 + f" {up}"
                    s2 = s2 + f" {down}"
                elif v2 > v1:
                    s1 = s1 + f" {down}"
                    s2 = s2 + f" {up}"
            else:
                if v1 < v2:
                    s1 = s1 + f" {up}"
                    s2 = s2 + f" {down}"
                elif v2 < v1:
                    s1 = s1 + f" {down}"
                    s2 = s2 + f" {up}"
            return s1, s2

        L1 = f"{res1['L']:.1f}"

        # Τρία λογικά blocks με "τίτλους" ως σειρές-κεφαλίδες
        data = [
            # Block 1: Εδαφικά / Υδραυλικά
            ["Εδαφικά / Υδραυλικά\n      Χαρακτηριστικά", "", ""],
            ["Τύπος εδάφους",    res1['soil'],              res2['soil']           ],
            ["K (m/day)",        f"{res1['K']}",            f"{res2['K']}"         ],

            # Block 2: Γεωμετρικά όρια πεδίου ροής και φράγματος
            ["  Γεωμετρικά Όρια Πεδίου Ροής \n           και Φράγματος", "", ""],
            ["L (m)",            L1,                        f"{res2['L']:.1f}"       ],
            ["d (m)",            f"{res1['d']}",            f"{res2['d']}"           ],
            ["H1 (m)",           f"{res1['H1']}",           f"{res2['H1']}"          ],
            ["H2 (m)",           f"{res1['H2']}",           f"{res2['H2']}"          ],
            ["Ανάντι (m)",       f"{res1['Ananti_user']}",  f"{res2['Ananti_user']}" ],
            ["Κατάντι (m)",      f"{res1['Katanti_user']}", f"{res2['Katanti_user']}"],

            # Block 3: Αποτελέσματα ροής και ασφάλειας
            ["  Αποτελέσματα Παροχών\n            και Ασφάλειας", "", ""],
            ["Q1 (m³/s)",        f"{res1['Q1']:.4f}",       f"{res2['Q1']:.4f}"    ],
            ["Q2 (m³/s)",        f"{res1['Q2']:.4f}",       f"{res2['Q2']:.4f}"    ],
            ["i_exit ",          f"{res1['i_exit']:.4f}" if res1['i_exit'] is not None else "-",
                                 f"{res2['i_exit']:.4f}" if res2['i_exit'] is not None else "-" ],
            ["FS ",              f"{res1['FS']:.3f}",       f"{res2['FS']:.3f}"    ],
        ]

        col_labels = ["Μέγεθος", "Σενάριο 1", "Σενάριο 2"]

        table = ax_txt.table(cellText=data, colLabels=col_labels,loc="center", cellLoc="center" )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.1, 1.3)

        # Styling κεφαλίδων στήλης
        for (r, c), cell in table.get_celld().items():
            if r == 0:
                cell.set_facecolor("#333333")
                cell.set_text_props(color="white", weight="bold")
            else:
                cell.set_facecolor("white")

        # Γραμμές τίτλων blocks (1η, 4η, 11η σειρά δεδομένων)
        block_header_rows = [1, 4, 11]
        for r in block_header_rows:
            # όλη η γραμμή
            for c in range(0, 3):
                cell = table[r, c]
                cell.set_facecolor("#dddddd")
                cell.set_text_props(weight="bold", ha="left" if c == 0 else "center")
            # στήλες 1-2 κενές
            table[r, 1].get_text().set_text("")
            table[r, 2].get_text().set_text("")
                    # Μεγαλύτερο ύψος για τις γραμμές τίτλων ώστε να χωράνε καλύτερα τα γράμματα
        for r in block_header_rows:
            for c in range(0, 3):
                cell = table[r, c]
                # default height ~ 0.1–0.12, πάμε σε κάτι πιο μεγάλο
                cell.set_height(0.18)


        # Bold + κίτρινο στις γεωμετρικές του 2ου σεναρίου που άλλαξαν
        geom_rows = {
            5: "L",
            6: "d",
            7: "H1",
            8: "H2",
            9: "Ananti",
            10: "Katanti",
            }
        for r, key in geom_rows.items():
            if res1[key] != res2[key]:
                cell2 = table[r, 2]
                cell2.set_facecolor("white")
                cell2.set_text_props(weight="bold", color="black")

        # Χρώμα + βελάκι μόνο στη στήλη "Σενάριο 2" για FS, Q1, Q2
        def color_and_arrow(row_idx, v1, v2, better_when_lower, is_q=True):
            v1 = float(v1)
            v2 = float(v2)

            improved = v2 < v1 if better_when_lower else v2 > v1
            color = "green" if improved else "red"

            if v2 > v1:
                arrow = "↑"
            elif v2 < v1:
                arrow = "↓"
            else:
                arrow = ""

            cell2 = table[row_idx, 2]
            base_txt = f"{v2:.4f}" if is_q else f"{v2:.3f}"
            cell2.get_text().set_text(f"{base_txt} {arrow}")
            cell2.set_text_props(weight="bold", color=color)
            cell2.set_facecolor("#d0f0c0" if improved else "#f8cccc")

        # δείκτες (σειρές στο data): Q1=12, Q2=13, i_exit=14, FS=15
        color_and_arrow(12, res1["Q1"],    res2["Q1"],    better_when_lower=True,  is_q=True)
        color_and_arrow(13, res1["Q2"],    res2["Q2"],    better_when_lower=True,  is_q=True)
        if res1["i_exit"] is not None and res2["i_exit"] is not None:
            color_and_arrow(14, res1["i_exit"], res2["i_exit"], better_when_lower=True,  is_q=True)
        color_and_arrow(15, res1["FS"],    res2["FS"],    better_when_lower=False, is_q=False)

        ax_txt.set_title("Σύγκριση δύο σεναρίων", fontsize=12, pad=10)
        fig_txt.tight_layout()
        register_figure_for_save(fig_txt, "comparison_table.png")

    # ===== 2. Αποθήκευση όλων των figures σε νέο run_x φάκελο =====
    if not FIGURES_TO_SAVE:
        ASKED_SAVE_ONCE = True
        return

    unique = []
    seen_figs = set()
    for fig, base_name in FIGURES_TO_SAVE:
        if id(fig) not in seen_figs:
            seen_figs.add(id(fig))
            unique.append((fig, base_name))
    FIGURES_TO_SAVE[:] = unique

    base_dir = os.path.expanduser("~/Desktop/dam_png")
    os.makedirs(base_dir, exist_ok=True)

    i = 1
    while True:
        run_dir = os.path.join(base_dir, f"run_{i}")
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)
            break
        i += 1

    save_all = messagebox.askyesno(
        "Αποθήκευση διαγραμμάτων",
        "Θέλεις να αποθηκεύσεις ΟΛΑ τα διαγράμματα (μαζί με τη σύγκριση) "
        f"σε νέο φάκελο μέσα στο dam_png (run_{i});",
        parent=parent_window
    )
    if save_all:
        for fig, base_name in FIGURES_TO_SAVE:
            path = unique_png_path(run_dir, base_name)
            fig.savefig(path, dpi=300, bbox_inches="tight")
        messagebox.showinfo(
            "Αποθήκευση",
            f"Οι εικόνες αποθηκεύτηκαν στον φάκελο:\n{run_dir}",
            parent=parent_window
        )

    ASKED_SAVE_ONCE = True
    