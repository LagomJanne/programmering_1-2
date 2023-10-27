import sqlite3
import tkinter as tk
import random

# Create an SQLite database and a table
conn = sqlite3.connect("glosor.db")
c = conn.cursor()

# Create a table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS glosor (
    id INTEGER PRIMARY KEY,
    ord TEXT,
    oversattning TEXT
)''')

# Save changes to the database
conn.commit()

# Function to fill the database with glossary entries

def fyll_databas():
    glosor_att_lagga_till = [
        ("dog", "hund"),
        ("cat", "katt"),
        ("car", "bil"),
        ("book", "bok"),
        ("sun", "sol")
    ]

    for ord, oversattning in glosor_att_lagga_till:
        c.execute("INSERT INTO glosor (ord, oversattning) VALUES (?, ?)", (ord, oversattning))

    conn.commit()

# Check if glossary entries already exist in the database
c.execute("SELECT COUNT(*) FROM glosor")
antal_glosor = c.fetchone()[0]

if antal_glosor == 0:
    fyll_databas()

# Function to randomly select a word that hasn't been shown yet
def slumpa_nytt_ord(visade_glosor):
    c.execute("SELECT * FROM glosor WHERE ord NOT IN ({}) ORDER BY RANDOM() LIMIT 1".format(
        ",".join(["?"] * len(visade_glosor))), tuple(visade_glosor))
    row = c.fetchone()
    return row

# Global variables
visade_glosor = []
totalt_antal_glosor = antal_glosor
antal_ratt = 0
antal_fel = 0
ratt_svar = ""
lagg_till_visad = True

# Function to check the answer
def kontrollera_svar():
    global antal_ratt, antal_fel
    svar = entry.get()
    korrekt_oversattning = ratt_svar

    if svar == korrekt_oversattning:
        svar_label.config(text="Rätt!", fg="green")
        antal_ratt += 1
    else:
        svar_label.config(text="Fel! Rätt svar är: " + korrekt_oversattning, fg="red")
        antal_fel += 1

    entry.delete(0, "end")
    entry.config(state=tk.DISABLED)
    kontrollera_knapp.config(state=tk.DISABLED)
    nasta_knapp.config(state=tk.NORMAL)

# Function to show a new word
def nytt_los():
    if len(visade_glosor) == totalt_antal_glosor:
        # All glossary entries have been shown, show the result
        ord_label.config(text="Alla glosor är klara!")
        resultat_text = f"Antal rätt: {antal_ratt}\nAntal fel: {antal_fel}"
        resultat_label.config(text=resultat_text)
    else:
        # Show a new glossary entry that hasn't been shown yet
        row = slumpa_nytt_ord(visade_glosor)
        visade_glosor.append(row[1])
        global ratt_svar
        ratt_svar = row[2]
        ord_label.config(text=row[1])
        entry.delete(0, "end")
        svar_label.config(text="", fg="black")
        entry.config(state=tk.NORMAL)
        kontrollera_knapp.config(state=tk.NORMAL)
        nasta_knapp.config(state=tk.DISABLED)

# Function to start over the game
def borja_om():
    global visade_glosor, antal_ratt, antal_fel
    visade_glosor = []
    antal_ratt = 0
    antal_fel = 0
    nytt_los()
    resultat_label.config(text="")

# Function to add a glossary entry to the database
def lagg_till_glosa():
    ord = nytt_ord_entry.get()
    oversattning = ny_oversattning_entry.get()

    if ord and oversattning:
        c.execute("INSERT INTO glosor (ord, oversattning) VALUES (?, ?)", (ord, oversattning))
        conn.commit()
        nytt_ord_entry.delete(0, "end")
        ny_oversattning_entry.delete(0, "end")

# Function to remove a glossary entry from the database
def ta_bort_glosa():
    selected_glosa = glossary_listbox.get(tk.ACTIVE)
    if selected_glosa:
        c.execute("DELETE FROM glosor WHERE ord=?", (selected_glosa,))
        conn.commit()
        uppdatera_glossary_listbox()

# Function to update the glossary entries
def uppdatera_glosor():
    c.execute("SELECT * FROM glosor")
    glosor = c.fetchall()
    return glosor

# Function to update the glossary listbox
def uppdatera_glossary_listbox():
    glossary_listbox.delete(0, tk.END)
    glosor = uppdatera_glosor()
    for glosa in glosor:
        glossary_listbox.insert(tk.END, glosa[1])

# Function to show or hide the ability to add and remove glossary entries
def toggle_editing():
    global lagg_till_visad
    lagg_till_visad = not lagg_till_visad

    if lagg_till_visad:
        visa_redigering_knapp.config(text="Dölj Redigering")
        nytt_ord_entry.pack()
        ny_oversattning_entry.pack()
        lagg_till_knapp.pack()
        ta_bort_knapp.pack()
        glossary_listbox.pack()
    else: 
        visa_redigering_knapp.config(text="Visa Redigering")
        nytt_ord_entry.pack_forget()
        ny_oversattning_entry.pack_forget()
        lagg_till_knapp.pack_forget()
        ta_bort_knapp.pack_forget()
        glossary_listbox.pack_forget()






#funktioner för att uppdatera gloslistan efter redigering
def update_glosor():
    c.execute("SELECT COUNT(*) FROM glosor")
    antal_glosor = c.fetchone()[0]
    conn.commit()

def update_glossary():
    glossary_listbox.delete(0, tk.END)
    glosor = uppdatera_glosor()
    for glosa in glosor:
        glossary_listbox.insert(tk.END, glosa[1])



# Create the main window
root = tk.Tk()
root.title("Glosor Tränare")
# Create GUI elements
ord_label = tk.Label(root, text="", font=("Arial", 24))
entry = tk.Entry(root, font=("Arial", 16))
entry.config(state=tk.DISABLED)
svar_label = tk.Label(root, text="", font=("Arial", 16))
kontrollera_knapp = tk.Button(root, text="Kontrollera", command=kontrollera_svar)
nasta_knapp = tk.Button(root, text="Nästa", command=nytt_los)
resultat_label = tk.Label(root, text="", font=("Arial", 16))
resultat_label.pack()
atersta_ll_knapp = tk.Button(root, text="Börja om", command=lambda: [borja_om(), update_glosor(), update_glossary()])
visa_redigering_knapp = tk.Button(root, text="Visa Redigering", command=toggle_editing)


nytt_ord_entry = tk.Entry(root, font=("Arial", 16))
ny_oversattning_entry = tk.Entry(root, font=("Arial", 16))
lagg_till_knapp = tk.Button(root, text="Lägg till glosa", command=lambda: [lagg_till_glosa(), update_glossary()])

glossary_listbox = tk.Listbox(root, font=("Arial", 16))
glossary_listbox.config(selectmode=tk.SINGLE)
ta_bort_knapp = tk.Button(root, text="Ta bort glosa", command=ta_bort_glosa)

lagga_till_frame = tk.Frame(root)
skrivrutan_frame = tk.Frame(root)
lagg_till_ta_bort_frame = tk.Frame(root)



# GUI
ord_label.pack(pady=20)
entry.pack(pady=10)
entry.focus_set()
svar_label.pack(pady=10)
kontrollera_knapp.pack()
nasta_knapp.pack()
atersta_ll_knapp.pack()
nasta_knapp.config(state=tk.DISABLED)
visa_redigering_knapp.pack()


nytt_ord_entry.pack(pady=10)
ny_oversattning_entry.pack(pady=10)
lagg_till_knapp.pack()

lagga_till_frame.pack()
skrivrutan_frame.pack()
lagg_till_ta_bort_frame.pack()

glossary_listbox.pack(pady=20)
ta_bort_knapp.pack_forget()


uppdatera_glossary_listbox()

toggle_editing()  # Hide editing from the start

# Randomly select the first word at the start
nytt_los()

# Ensure that you close the database connection when the program is closed
root.protocol("WM_DELETE_WINDOW", lambda: conn.close())

# Start the tkinter event loop
root.mainloop()
