# 🌊 Seepage Flow Net Analysis — Ανάλυση Διήθησης κάτω από Φράγμα

Εργαλείο αριθμητικής ανάλυσης της **υπόγειας ροής (seepage)** κάτω από υδραυλικό
φράγμα. Το πρόγραμμα επιλύει την εξίσωση Laplace του δυναμικού με τη μέθοδο
**Gauss–Seidel**, κατασκευάζει αυτόματα το **δίκτυο ροής (flow net)**, τις
ισοδυναμικές γραμμές και γραμμές ροής, και υπολογίζει τα κρίσιμα μεγέθη
σχεδιασμού: **παροχή διήθησης**, **κλίση εξόδου** και **συντελεστή ασφαλείας
έναντι διασωλήνωσης (piping)**.

> Αναπτύχθηκε στο πλαίσιο διπλωματικής εργασίας στον τομέα Συγκοινωνιακών και 
> Υδραυλικών έργων του τμήματος Αγρονόμων και Τοπογράφων Μηχανικών στο 
> Αριστοτέλειο Πανεπιστήμιο Θεσσαλονίκης

---

## ✨ Δυνατότητες

- **Αριθμητική επίλυση πεδίου δυναμικού** με τη μέθοδο Gauss–Seidel σε πλέγμα
  πεπερασμένων διαφορών, με ρυθμιζόμενα κριτήρια σύγκλισης και ακρίβειας.
- **Αυτόματη κατασκευή flow net**:
  - ισοδυναμικές γραμμές (equipotential lines),
  - γραμμές ροής (flow lines) με αλγόριθμο που διατηρεί την **ορθογωνικότητα**
    ως προς τις ισοδυναμικές.
- **Υπολογισμός παροχής διήθησης Q** με δύο ανεξάρτητες μεθόδους
  (γεωμετρία flow net & κατάντι στήλες δυναμικού) για διασταύρωση αποτελεσμάτων.
- **Έλεγχος ασφαλείας έναντι piping**: κρίσιμη υδραυλική κλίση `i_cr`,
  κλίση εξόδου `i_exit` και συντελεστής ασφαλείας `FS = i_cr / i_exit`.
- **Γραφικό περιβάλλον εισαγωγής δεδομένων (GUI)** με προεπιλεγμένους τύπους
  εδάφους (Χονδρόκοκκο / Μικτό / Λεπτόκοκκο) ή προσαρμοσμένες παραμέτρους
  (`Gs`, `e`).
- **Σύγκριση δύο σεναρίων** δίπλα-δίπλα, με συγκεντρωτικό πίνακα δεικτών
  και επισήμανση των διαφορών.
- **Εξαγωγή αποτελεσμάτων** σε εικόνες PNG υψηλής ανάλυσης, οργανωμένες
  αυτόματα σε φακέλους ανά εκτέλεση.

---

## 📸 Παράδειγμα εξόδου

Το πρόγραμμα παράγει το πλήρες δίκτυο ροής πάνω στην κατανομή του δυναμικού,
μαζί με τη γεωμετρία του φράγματος και τις στάθμες νερού ανάντι / κατάντι.

<img width="1963" height="2067" alt="flownet_single" src="https://github.com/user-attachments/assets/d544a246-bd27-4077-8683-cf8433f7f770" />


---

## 🧮 Θεωρητικό υπόβαθρο

Η ροή θεωρείται μόνιμη και διδιάστατη σε ισότροπο, ομογενές μέσο και διέπεται
από την εξίσωση Laplace του υδραυλικού δυναμικού:
∂²φ/∂x² + ∂²φ/∂y² = 0


Η αριθμητική επίλυση γίνεται με τον τύπο των πεπερασμένων διαφορών (μέσος όρος
γειτονικών κόμβων) και επαναληπτική σύγκλιση Gauss–Seidel. Από το πεδίο
δυναμικού προκύπτουν:

| Μέγεθος | Σύμβολο | Περιγραφή |
|---|---|---|
| Παροχή διήθησης | `Q` | Q = k · A · (Δφ / ΔL) |
| Κρίσιμη κλίση | `i_cr` | i_cr = (Gs − 1) / (1 + e) |
| Κλίση εξόδου | `i_exit` | υπολογισμένη στο κατάντι πόδι |
| Συντελεστής ασφαλείας | `FS` | FS = i_cr / i_exit |

---

## ⚙️ Εγκατάσταση

Απαιτείται **Python 3.9+**.

▶️ Εκτέλεση


python main_dam.py

1) Συμπλήρωσε τις παραμέτρους στο παράθυρο εισαγωγής (γεωμετρία, στάθμες νερού,
τύπος εδάφους, υδραυλική αγωγιμότητα K).

3) Το πρόγραμμα εμφανίζει το flow net και τυπώνει στο τερματικό τα Q, i_exit
και FS.

Προαιρετικά εκτελείς δεύτερο σενάριο για σύγκριση.
Στο τέλος επιλέγεις αν θα αποθηκευτούν όλα τα διαγράμματα σε PNG.


🗂️ Δομή του κώδικα

Αρχείο	Ρόλος

main_dam.py	Κεντρικό script — ενορχήστρωση σεναρίων
gui_inputs.py	Γραφικό περιβάλλον εισαγωγής δεδομένων (tkinter)
Gauss_Seidel.py	Επίλυση πεδίου δυναμικού με πεπερασμένες διαφορές
Gap_Lines.py	Υπολογισμός & σχεδίαση ισοδυναμικών γραμμών
Flow_Lines.py	Κατασκευή γραμμών ροής με ορθογωνικότητα
Flow_Rate.py	Υπολογισμός παροχής διήθησης (2 μέθοδοι)
Exit_Gradient.py	Υπολογισμός κλίσης εξόδου (piping)
visualization.py	Σύνθεση & απεικόνιση του flow net
comparison.py	Σύγκριση δύο σεναρίων δίπλα-δίπλα
helpers.py	Βοηθητικές συναρτήσεις & αποθήκευση εικόνων


📌 Παραδοχές & Περιορισμοί
Μόνιμη, διδιάστατη ροή σε ισότροπο και ομογενές έδαφος.
Οριζόντιο αδιαπέρατο υπόβαθρο σε σταθερό βάθος.
Η ακρίβεια εξαρτάται από την πυκνότητα του πλέγματος (dx, dy).






# 🌊 Seepage Flow Net Analysis — Under-Dam Seepage Solver

A numerical tool for analyzing **groundwater seepage beneath a hydraulic dam**.
The program solves the Laplace equation for the hydraulic potential using the
**Gauss–Seidel** method, automatically constructs the **flow net** —
equipotential lines and flow lines — and computes the key design quantities:
**seepage flow rate**, **exit gradient**, and **factor of safety against
piping**.

> Developed as part of a diploma thesis in Geotechnical / Hydraulic Engineering.

---

## ✨ Features

- **Numerical potential-field solver** using the Gauss–Seidel method on a
  finite-difference grid, with configurable convergence and accuracy criteria.
- **Automatic flow net generation**:
  - equipotential lines,
  - flow lines built with an algorithm that preserves **orthogonality** to the
    equipotentials.
- **Seepage flow rate Q** computed with two independent methods
  (flow-net geometry & downstream potential columns) for cross-validation.
- **Piping safety check**: critical hydraulic gradient `i_cr`, exit gradient
  `i_exit`, and factor of safety `FS = i_cr / i_exit`.
- **Graphical input interface (GUI)** with preset soil types
  (Coarse / Mixed / Fine-grained) or custom parameters (`Gs`, `e`).
- **Two-scenario comparison** side by side, with a summary table of indicators
  highlighting the differences.
- **Result export** to high-resolution PNG images, automatically organized into
  per-run folders.

---

## 📸 Example output

The program renders the full flow net over the potential distribution, together
with the dam geometry and upstream / downstream water levels.

> _Add a screenshot here, e.g.:_
> `![Flow net](docs/flownet_example.png)`

---

## 🧮 Theoretical background

Flow is assumed steady-state and two-dimensional in an isotropic, homogeneous
medium, governed by the Laplace equation of the hydraulic potential:
∂²φ/∂x² + ∂²φ/∂y² = 0



The equation is solved numerically with the finite-difference scheme (average of
neighboring nodes) and iterative Gauss–Seidel convergence. From the potential
field, the following are derived:

| Quantity | Symbol | Description |
|---|---|---|
| Seepage flow rate | `Q` | Q = k · A · (Δφ / ΔL) |
| Critical gradient | `i_cr` | i_cr = (Gs − 1) / (1 + e) |
| Exit gradient | `i_exit` | evaluated at the downstream toe |
| Factor of safety | `FS` | FS = i_cr / i_exit |

---

## ⚙️ Installation

Requires **Python 3.9+**.

```bash
git clone https://github.com/<username>/<repo>.git
cd <repo>
pip install numpy matplotlib

tkinter ships with most Python installations.
On some Linux distributions, install it with sudo apt install python3-tk.

▶️ Usage

python main_dam.py

Fill in the parameters in the input window (geometry, water levels, soil type,
hydraulic conductivity K).

The program displays the flow net and prints Q, i_exit, and FS to the
terminal.

Optionally run a second scenario for comparison.

At the end, choose whether to save all diagrams as PNG.


🗂️ Project structure

File	Role

main_dam.py	Main script — scenario orchestration

gui_inputs.py	Graphical data-input interface (tkinter)

Gauss_Seidel.py	Potential-field solver (finite differences)

Gap_Lines.py	Computation & plotting of equipotential lines

Flow_Lines.py	Flow-line construction with orthogonality

Flow_Rate.py	Seepage flow rate computation (2 methods)

Exit_Gradient.py	Exit gradient (piping) computation

visualization.py	Flow-net composition & rendering

comparison.py	Side-by-side comparison of two scenarios

helpers.py	Utility functions & image export

📌 Assumptions & limitations

Steady-state, two-dimensional flow in an isotropic and homogeneous soil.
Horizontal impermeable boundary at a fixed depth.
Accuracy depends on grid density (dx, dy).




