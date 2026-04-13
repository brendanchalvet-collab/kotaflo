import os

def print_tree(path, indent=""):
    if not os.path.exists(path):
        print(f"⚠️ Dossier introuvable : {path}")
        return
    entries = sorted(os.listdir(path))
    for entry in entries:
        full_path = os.path.join(path, entry)
        print(indent + entry)
        if os.path.isdir(full_path):
            print_tree(full_path, indent + "    ")

# chemin corrigé vers ton dossier réel
dossier_a_explorer = r"C:\Users\brend\OneDrive\Documents\BUSINESS\CELERITAS LABS\03 - CLIENTS\N001 - Artisans\Saas - artisans"

print_tree(dossier_a_explorer)