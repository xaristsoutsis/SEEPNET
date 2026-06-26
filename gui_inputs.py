import tkinter as tk
from tkinter import ttk
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass
def get_inputs_from_gui(root):
    L_default = 46
    d_default = 23
    dx_default = 0.5
    dy_default = 0.5
    H1_default = 7
    H2_default = 2
    Ananti_default = 15
    Katanti_default = 31
    hydraulic_conductivity_default = 8.5  # αρχική τιμή σε m/day (ενδεικτική)

    soil_default = "Χονδρόκοκκο"
    Gs_default = 2.65
    e_default = 0.50

    # dict με ιδιότητες εδαφών
    SOIL_PROPS = {
        "Χονδρόκοκκο": (2.65, 0.50),
        "Μικτό":       (2.70, 0.70),
        "Λεπτόκοκκο":  (2.75, 0.90),}

    result = {
        "L": L_default,
        "d": d_default,
        "dx": dx_default,
        "dy": dy_default,
        "H1": H1_default,
        "H2": H2_default,
        "Ananti": Ananti_default,
        "Katanti": Katanti_default,
        "K": hydraulic_conductivity_default,
        "soil": soil_default,
        "Gs": Gs_default,
        "e": e_default,
    }

    win = tk.Toplevel(root)
    win.title("Ρυθμίσεις Προβλήματος Φράγματος")

    win.tk.call('tk', 'scaling', 1.8)  # δοκίμασε 1.3, 1.4, 1.5

    win_w = 700
    win_h = 750

    win.geometry(f"{win_w}x{win_h}")
    win.minsize(win_w, win_h)

    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w - win_w) // 2
    y = (screen_h - win_h) // 2
    win.geometry(f"{win_w}x{win_h}+{x}+{y}")

    pad = {'padx': 8, 'pady': 6}
    style = ttk.Style(win)
    style.configure("TLabel", font=("Arial", 12))   # γενικό μέγεθος label
    style.configure("TButton", font=("Arial", 12))
    style.configure("TEntry", font=("Arial", 12))
    style.configure("TCombobox", font=("Arial", 12))

    ttk.Label(
        win,
        text="Γεωμετρικά Χαρακτηριστικά",
        font=("Arial", 18, "bold")
    ).grid(row=0, column=0, columnspan=2, pady=(11, 7))


    ttk.Label(win, text="Συνολικό Μήκος L (m):").grid(
        row=1, column=0, **pad, sticky="e")
    entry_L = ttk.Entry(win)
    entry_L.insert(0, str(L_default))
    entry_L.grid(row=1, column=1, **pad)

    ttk.Label(win, text="Βάθος Αδιαπέρατου d (m):").grid(
        row=2, column=0, **pad, sticky="e")
    entry_d = ttk.Entry(win)
    entry_d.insert(0, str(d_default))
    entry_d.grid(row=2, column=1, **pad)

    ttk.Label(win, text="Οριζόντιο βήμα dx (m):").grid(
        row=3, column=0, **pad, sticky="e")
    entry_dx = ttk.Entry(win)
    entry_dx.insert(0, str(dx_default))
    entry_dx.grid(row=3, column=1, **pad)

    ttk.Label(win, text="Κατακόρυφο βήμα dy (m):").grid(
        row=4, column=0, **pad, sticky="e")
    entry_dy = ttk.Entry(win)
    entry_dy.insert(0, str(dy_default))
    entry_dy.grid(row=4, column=1, **pad)

    ttk.Label(win, text="Ύψος Νερού Ανάντι H1 (m):").grid(
        row=5, column=0, **pad, sticky="e")
    entry_H1 = ttk.Entry(win)
    entry_H1.insert(0, str(H1_default))
    entry_H1.grid(row=5, column=1, **pad)

    ttk.Label(win, text="Ύψος Νερού Κατάντι H2 (m):").grid(
        row=6, column=0, **pad, sticky="e")
    entry_H2 = ttk.Entry(win)
    entry_H2.insert(0, str(H2_default))
    entry_H2.grid(row=6, column=1, **pad)

    ttk.Label(win, text="Μήκος ανάντι ζώνης (m):").grid(
        row=7, column=0, **pad, sticky="e")
    entry_Ananti = ttk.Entry(win)
    entry_Ananti.insert(0, str(Ananti_default))
    entry_Ananti.grid(row=7, column=1, **pad)

    ttk.Label(win, text="Μήκος κατάντι ζώνης (L=0→Lmax) (m):").grid(
        row=8, column=0, **pad, sticky="e")
    entry_Katanti = ttk.Entry(win)
    entry_Katanti.insert(0, str(Katanti_default))
    entry_Katanti.grid(row=8, column=1, **pad)

    # K σε m/day
    ttk.Label(win, text="K (m/day):").grid(
        row=9, column=0, **pad, sticky="e")
    entry_K = ttk.Entry(win)
    entry_K.insert(0, str(hydraulic_conductivity_default))
    entry_K.grid(row=9, column=1, **pad)

    ttk.Label(
        win,
        text="Τύπος εδάφους",
        font=("Arial", 12, "bold")
    ).grid(row=10, column=0, columnspan=2, pady=(10, 4))

    soil_var = tk.StringVar(value=soil_default)
    ttk.Label(win, text="Επιλογή:").grid(
        row=11, column=0, **pad, sticky="e")
    soil_combo = ttk.Combobox(
        win,
        textvariable=soil_var,
        values=["Χονδρόκοκκο", "Μικτό", "Λεπτόκοκκο", "Custom"],
        state="readonly"
    )
    soil_combo.grid(row=11, column=1, **pad)

    ttk.Label(win, text="Gs:").grid(
        row=12, column=0, **pad, sticky="e")
    entry_Gs = ttk.Entry(win)
    entry_Gs.insert(0, str(Gs_default))
    entry_Gs.grid(row=12, column=1, **pad)

    ttk.Label(win, text="e:").grid(
        row=13, column=0, **pad, sticky="e")
    entry_e = ttk.Entry(win)
    entry_e.insert(0, str(e_default))
    entry_e.grid(row=13, column=1, **pad)

    # αρχικά κλειδωμένα
    entry_Gs.configure(state="disabled")
    entry_e.configure(state="disabled")

    def on_soil_change(event=None):
        choice = soil_var.get()

        if choice == "Custom":
            # Ανοίγουν για ελεύθερη εισαγωγή
            entry_Gs.configure(state="normal")
            entry_e.configure(state="normal")
            return

        # Για τις standard επιλογές ενημερώνουμε αυτόματα και τα κλειδώνουμε
        Gs_val, e_val = SOIL_PROPS.get(choice, (Gs_default, e_default))

        entry_Gs.configure(state="normal")
        entry_e.configure(state="normal")

        entry_Gs.delete(0, tk.END)
        entry_Gs.insert(0, str(Gs_val))

        entry_e.delete(0, tk.END)
        entry_e.insert(0, str(e_val))

        entry_Gs.configure(state="disabled")
        entry_e.configure(state="disabled")

    soil_combo.bind("<<ComboboxSelected>>", on_soil_change)

    def on_submit():
        try:
            result["L"] = float(entry_L.get() or L_default)
            result["d"] = float(entry_d.get() or d_default)
            result["dx"] = float(entry_dx.get() or dx_default)
            result["dy"] = float(entry_dy.get() or dy_default)
            result["H1"] = float(entry_H1.get() or H1_default)
            result["H2"] = float(entry_H2.get() or H2_default)
            result["Ananti"] = float(entry_Ananti.get() or Ananti_default)
            result["Katanti"] = float(entry_Katanti.get() or Katanti_default)
            # K σε m/day (ό,τι έγραψε ο χρήστης ή default)
            result["K"] = float(entry_K.get() or hydraulic_conductivity_default)

            soil_choice = soil_var.get()
            result["soil"] = soil_choice

            if soil_choice in SOIL_PROPS:
                Gs_val, e_val = SOIL_PROPS[soil_choice]
                result["Gs"] = Gs_val
                result["e"] = e_val
            elif soil_choice == "Custom":
                result["Gs"] = float(entry_Gs.get() or Gs_default)
                result["e"] = float(entry_e.get() or e_default)

        except ValueError:
            return

        win.destroy()

    btn = ttk.Button(win, text="Εκτέλεση", command=on_submit)
    btn.grid(row=14, column=0, columnspan=2, pady=10)

    win.grab_set()
    root.wait_window(win)

    return (
        result["L"], result["d"], result["dx"], result["dy"],
        result["H1"], result["H2"], result["Ananti"], result["Katanti"],
        result["K"], result["soil"], result["Gs"], result["e"])