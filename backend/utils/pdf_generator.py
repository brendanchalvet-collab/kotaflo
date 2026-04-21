"""
Générateur PDF devis — style épuré.
"""
from fpdf import FPDF
from datetime import datetime


# ===== PALETTE =====
BLUE      = (37,  99,  235)
DARK      = (31,  41,  55)
GRAY      = (107, 114, 128)
GRAY_LITE = (229, 231, 235)
WHITE     = (255, 255, 255)

# Largeurs colonnes tableau devis normal : Désignation, TVA, Qté+Unité, Prix HT, Montant HT
COL_W = [82, 14, 22, 34, 34]       # total = 186 mm
COL_X = [10]
for _w in COL_W[:-1]:
    COL_X.append(COL_X[-1] + _w)

# Largeurs colonnes tableau avenant (+ colonne Différence)
COL_W_AV = [66, 12, 18, 28, 28, 34]   # total = 186 mm
COL_X_AV = [10]
for _w in COL_W_AV[:-1]:
    COL_X_AV.append(COL_X_AV[-1] + _w)


_CHAR_MAP = {"—": "-", "–": "-", "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"'}

def _s(v):
    """Convertit en str et remplace les caractères hors latin-1 non supportés par Helvetica."""
    s = str(v) if v is not None else ""
    for src, dst in _CHAR_MAP.items():
        s = s.replace(src, dst)
    return s


def _date(s):
    if not s:
        return ""
    try:
        return datetime.fromisoformat(str(s)).strftime("%d/%m/%Y")
    except Exception:
        return str(s)


def _eur(n):
    try:
        return f"{float(n):,.2f} EUR".replace(",", " ")
    except Exception:
        return "0.00 EUR"


def _quote_ref(quote, parent_quote_number=None):
    """Construit la référence structurée d'un devis ou avenant."""
    try:
        year = datetime.fromisoformat(str(quote.get("created_at", ""))).year
    except Exception:
        year = datetime.utcnow().year
    t  = quote.get("tenant_id", "")
    cl = quote.get("client_id", "")
    j  = quote.get("job_id", "")

    if quote.get("parent_quote_id"):
        pnum = parent_quote_number or quote.get("parent_quote_id", "")
        anum = quote.get("avenant_number", 1)
        return f"AV-{year}-{t}-{cl}-{j}-{pnum}-{anum}"
    else:
        qnum = quote.get("quote_number") or quote.get("id", "")
        return f"DEV-{year}-{t}-{cl}-{j}-{qnum}"


def _invoice_ref(invoice):
    """Construit la référence structurée d'une facture."""
    try:
        year = datetime.fromisoformat(str(invoice.get("created_at", ""))).year
    except Exception:
        year = datetime.utcnow().year
    cl   = invoice.get("client_id", "")
    j    = invoice.get("job_id", "")
    num  = invoice.get("invoice_number") or invoice.get("id", "")
    pfx  = "AC" if invoice.get("invoice_type") == "deposit" else "FI"
    return f"{pfx}-{year}-{cl}-{j}-{num}"


def _merge_avenant_lines(lines):
    """Fusionne les paires Suppression/Modification pour l'affichage PDF.
    La ligne Suppression est absorbée dans la ligne Modification correspondante
    via l'attribut _old_ht. Les suppressions sans modification restent telles quelles."""
    supp_map = {}   # suffix → old_ht (valeur absolue)
    for l in lines:
        d = str(l.get("designation") or "")
        if d.startswith("Suppression - "):
            suffix  = d[len("Suppression - "):]
            old_ht  = abs(float(l.get("quantity", 1)) * float(l.get("unit_price", 0)))
            supp_map[suffix] = old_ht

    result = []
    for l in lines:
        d = str(l.get("designation") or "")
        if d.startswith("Suppression - "):
            suffix = d[len("Suppression - "):]
            # On ne garde la suppression que si elle n'a PAS de modification associée
            if f"Modification - {suffix}" not in [str(x.get("designation") or "") for x in lines]:
                result.append(l)
        elif d.startswith("Modification - "):
            suffix = d[len("Modification - "):]
            merged = dict(l)
            if suffix in supp_map:
                merged["_old_ht"] = supp_map[suffix]
            result.append(merged)
        else:
            result.append(l)
    return result


class QuotePDF(FPDF):

    def __init__(self, company, client, quote, lines, job=None,
                 signer_name=None, signed_at=None, parent_amount=None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.company        = company
        self.client         = client
        self.quote          = quote
        self.lines          = lines
        self.job            = job or {}
        self.signer_name    = signer_name or ""
        self.signed_at      = signed_at or ""
        self.parent_amount  = parent_amount  # montant HT du devis parent (pour avenants)
        self.set_margins(10, 10, 10)
        self.set_auto_page_break(auto=True, margin=18)
        self.add_page()
        self._build()

    # ===== FOOTER =====
    def footer(self):
        self.set_y(-14)
        self.set_draw_color(*GRAY_LITE)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        parts = []
        c = self.company
        if _s(c.get("siret")):
            parts.append(f"SIRET : {_s(c.get('siret'))}")
        if _s(c.get("tva_number")):
            parts.append(f"TVA : {_s(c.get('tva_number'))}")
        if _s(c.get("insurance_info")):
            parts.append(_s(c.get("insurance_info")))
        parts.append(f"Page {self.page_no()}")
        self.set_font("Helvetica", "", 6.5)
        self.set_text_color(*GRAY)
        self.cell(0, 4, "  ·  ".join(parts), align="C")

    # ===== HEADER =====
    def _header_block(self):
        c = self.company
        name = _s(c.get("company_name") or c.get("name")) or "Mon Entreprise"

        # ── Gauche : infos entreprise ──
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*BLUE)
        self.cell(100, 8, name, ln=False)

        # ── Droite : bloc DEVIS / AVENANT ──
        is_avenant = bool(self.quote.get("parent_quote_id"))
        if is_avenant:
            av_num  = self.quote.get("avenant_number", 1)
            doc_lbl = f"AVENANT N\u00b0{av_num}"
            self.set_font("Helvetica", "B", 14)
        else:
            doc_lbl = "DEVIS"
            self.set_font("Helvetica", "B", 20)
        self.set_xy(100, 10)
        self.set_text_color(*BLUE)
        self.cell(96, 8, doc_lbl, align="R", ln=True)

        # Infos contact (gauche)
        self.set_x(10)
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(*GRAY)
        contact = [
            _s(c.get("address")),
            " ".join(filter(None, [_s(c.get("zip_code")), _s(c.get("city"))])),
            _s(c.get("phone")),
            _s(c.get("email")),
            _s(c.get("website")),
        ]
        y_left = 19
        for line in contact:
            if line.strip():
                self.set_xy(10, y_left)
                self.cell(100, 4.5, line)
                y_left += 4.5

        # Infos devis (droite)
        is_avenant = bool(self.quote.get("parent_quote_id"))
        ref        = _quote_ref(self.quote, self.quote.get("parent_quote_number"))
        items_r = [
            ("", ref),
            ("Date :", _date(self.quote.get("created_at"))),
            ("Expire le :", _date(self.quote.get("expiry_date"))),
            ("Paiement :", _s(self.quote.get("payment_terms")) or "Comptant"),
        ]
        if is_avenant:
            # Référence du devis parent
            parent_num = self.quote.get("parent_quote_number") or self.quote.get("parent_quote_id", "")
            try:
                year = datetime.fromisoformat(str(self.quote.get("created_at", ""))).year
            except Exception:
                year = datetime.utcnow().year
            parent_ref = f"DEV-{year}-{self.quote.get('tenant_id','')}-{self.quote.get('client_id','')}-{self.quote.get('job_id','')}-{parent_num}"
            items_r.append(("Ref. devis :", parent_ref))
        y_right = 20
        for label, val in items_r:
            if not val:
                continue
            self.set_xy(120, y_right)
            self.set_font("Helvetica", "B" if not label else "", 8.5)
            self.set_text_color(*GRAY if label else DARK)
            self.cell(30, 4.5, label, align="R")
            self.set_font("Helvetica", "B" if not label else "", 8.5)
            self.set_text_color(*DARK)
            self.cell(50, 4.5, val, align="R", ln=True)
            y_right += 4.5

        # Ligne séparatrice fine
        y_sep = max(y_left, y_right) + 3
        self.set_draw_color(*BLUE)
        self.set_line_width(0.4)
        self.line(10, y_sep, 200, y_sep)
        self.set_y(y_sep + 5)

    # ===== ADRESSES =====
    def _addresses_block(self):
        cl  = self.client
        job = self.job

        # Adresse de facturation = client
        client_name = _s(cl.get("name")) or "—"
        client_addr = _s(cl.get("address"))
        client_city = " ".join(filter(None, [_s(cl.get("zip_code")), _s(cl.get("city"))]))
        client_country = _s(cl.get("country")) or "FRANCE"

        # Adresse de chantier = projet (si renseignée) sinon adresse client
        job_name  = _s(job.get("title")) or client_name
        job_addr  = _s(job.get("address")) or client_addr

        y = self.get_y()

        # ── Gauche : Adresse du chantier ──
        self.set_xy(10, y)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*GRAY)
        self.cell(90, 4, "Adresse du chantier")

        self.set_xy(10, y + 5)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*DARK)
        self.cell(90, 5, job_name)

        dy = y + 11
        for val in [job_addr]:
            if val.strip():
                self.set_xy(10, dy)
                self.set_font("Helvetica", "", 8.5)
                self.set_text_color(*GRAY)
                self.cell(90, 4.5, val)
                dy += 4.5

        # ── Droite : Adresse de facturation ──
        self.set_xy(110, y)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*GRAY)
        self.cell(90, 4, "Adresse de facturation")

        self.set_xy(110, y + 5)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*DARK)
        self.cell(90, 5, client_name)

        dy = y + 11
        for val in [client_addr, client_city, client_country]:
            if val.strip():
                self.set_xy(110, dy)
                self.set_font("Helvetica", "", 8.5)
                self.set_text_color(*GRAY)
                self.cell(90, 4.5, val)
                dy += 4.5

        self.set_y(y + 32)

    # ===== TABLEAU =====
    def _table_block(self):
        is_avenant    = bool(self.quote.get("parent_quote_id"))
        display_lines = _merge_avenant_lines(self.lines) if is_avenant else list(self.lines)

        # Colonnes : 6 pour avenant (avec Différence), 5 pour devis normal
        if is_avenant:
            headers = ["Designation", "TVA", "Qte.", "Prix unit. HT", "Montant HT", "Difference"]
            cw, cx  = COL_W_AV, COL_X_AV
        else:
            headers = ["Designation", "TVA", "Qte.", "Prix unit. HT", "Montant HT"]
            cw, cx  = COL_W, COL_X

        # En-tête
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*DARK)
        y = self.get_y()
        for i, h in enumerate(headers):
            self.set_xy(cx[i], y)
            self.cell(cw[i], 6, h, align="L" if i == 0 else "R")
        self.set_y(y + 6)
        self.set_draw_color(*DARK)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 196, self.get_y())
        self.ln(1)

        # Lignes
        for line in display_lines:
            desig      = _s(line.get("designation"))
            desc       = _s(line.get("description"))
            tva_rate   = float(line.get("tva_rate", 10))
            qty        = float(line.get("quantity", 1))
            unit       = _s(line.get("unit") or "U")
            unit_price = float(line.get("unit_price", 0))
            total_ht   = qty * unit_price
            qty_str    = str(int(qty)) if qty == int(qty) else f"{qty:.2f}"
            old_ht     = line.get("_old_ht")   # présent sur les lignes modification fusionnées

            y = self.get_y()

            # Désignation bold
            self.set_xy(cx[0], y)
            self.set_font("Helvetica", "B", 8.5)
            self.set_text_color(*DARK)
            self.cell(cw[0], 6, desig)

            # Colonnes numériques communes
            self.set_font("Helvetica", "", 8.5)
            qty_unit_str = f"{qty_str} {unit}".strip() if unit and unit != "U" else qty_str
            for val, col in [
                (f"{tva_rate:.1f}%", 1),
                (qty_unit_str,       2),
                (_eur(unit_price),   3),
                (_eur(total_ht),     4),
            ]:
                self.set_xy(cx[col], y)
                self.cell(cw[col], 6, val, align="R")

            # Colonne Différence (avenant uniquement)
            if is_avenant and old_ht is not None:
                delta = total_ht - old_ht
                sign  = "+" if delta >= 0 else ""
                diff_str = f"{sign}{_eur(delta)}"
                self.set_font("Helvetica", "B", 8.5)
                self.set_text_color(*(BLUE if delta >= 0 else (220, 38, 38)))
                self.set_xy(cx[5], y)
                self.cell(cw[5], 6, diff_str, align="R")
                self.set_text_color(*DARK)

            self.set_y(y + 6)

            # Description en italique gris
            if desc.strip():
                self.set_xy(cx[0] + 2, self.get_y())
                self.set_font("Helvetica", "I", 7.5)
                self.set_text_color(*GRAY)
                self.multi_cell(cw[0] - 2, 4, desc, border=0)
                self.set_text_color(*DARK)

            # Trait séparateur gris
            self.set_draw_color(160, 160, 160)
            self.set_line_width(0.2)
            self.line(10, self.get_y(), 196, self.get_y())
            self.ln(1)

        self.ln(2)

    # ===== TOTAUX =====
    def _totals_block(self):
        total_ht = 0.0
        tva_map  = {}
        for l in self.lines:
            ht   = float(l.get("quantity", 1)) * float(l.get("unit_price", 0))
            rate = float(l.get("tva_rate", 10))
            total_ht += ht
            tva_map[rate] = tva_map.get(rate, 0.0) + ht * (rate / 100)

        total_tva = sum(tva_map.values())
        total_ttc = total_ht + total_tva

        x_l, x_v, w_l, w_v = 120, 163, 41, 33

        def row(label, value, bold=False, big=False):
            sz = 9.5 if big else 8.5
            self.set_x(x_l)
            self.set_font("Helvetica", "B" if bold else "", sz)
            self.set_text_color(*DARK)
            self.cell(w_l, 5.5, label)
            self.set_font("Helvetica", "B" if bold else "", sz)
            self.cell(w_v, 5.5, value, align="R", ln=True)

        row("Total HT", _eur(total_ht), bold=True)
        for rate, tva_amt in sorted(tva_map.items()):
            base = sum(
                float(l.get("quantity", 1)) * float(l.get("unit_price", 0))
                for l in self.lines if float(l.get("tva_rate", 10)) == rate
            )
            row(f"TVA {rate:.1f}% (base {_eur(base)})", _eur(tva_amt))

        # Trait + Total TTC
        y = self.get_y() + 1
        self.set_draw_color(*BLUE)
        self.set_line_width(0.4)
        self.line(x_l, y, 196, y)
        self.set_y(y + 2)
        self.set_x(x_l)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*BLUE)
        self.cell(w_l, 7, "Total TTC")
        self.cell(w_v, 7, _eur(total_ttc), align="R", ln=True)

        # Nouveau total devis (avenant uniquement)
        if self.parent_amount is not None:
            new_total_ht = float(self.parent_amount) + total_ht
            self.ln(3)
            self.set_x(x_l)
            self.set_font("Helvetica", "", 8.5)
            self.set_text_color(*GRAY)
            self.cell(w_l, 5, "Montant devis initial HT")
            self.cell(w_v, 5, _eur(self.parent_amount), align="R", ln=True)
            self.set_x(x_l)
            self.cell(w_l, 5, "Delta avenant HT")
            self.cell(w_v, 5, (("+" if total_ht >= 0 else "") + _eur(total_ht)), align="R", ln=True)
            y2 = self.get_y() + 1
            self.set_draw_color(*BLUE)
            self.line(x_l, y2, 196, y2)
            self.set_y(y2 + 2)
            self.set_x(x_l)
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*BLUE)
            self.cell(w_l, 6, "Nouveau total devis HT")
            self.cell(w_v, 6, _eur(new_total_ht), align="R", ln=True)

        self.ln(6)

    # ===== PAIEMENT =====
    def _payment_block(self):
        c = self.company

        # Trait séparateur
        self.set_draw_color(*GRAY_LITE)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 196, self.get_y())
        self.ln(4)

        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*DARK)
        self.cell(0, 5, "Informations de paiement", ln=True)
        self.ln(1)

        items = []
        if _s(c.get("iban")):
            items.append(("IBAN", _s(c.get("iban"))))
        if _s(c.get("bic")):
            items.append(("BIC",  _s(c.get("bic"))))
        if _s(c.get("rge_number")):
            items.append(("RGE", _s(c.get("rge_number"))))

        for label, val in items:
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*GRAY)
            self.cell(22, 5, f"{label} :")
            self.set_font("Helvetica", "", 8)
            self.set_text_color(*DARK)
            self.cell(0, 5, val, ln=True)

        if self.quote.get("notes") and _s(self.quote.get("notes")).strip():
            self.ln(2)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*GRAY)
            self.multi_cell(0, 4.5, _s(self.quote.get("notes")))

        # Mention signature (uniquement si pas encore signé)
        if not self.signer_name:
            self.ln(3)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*GRAY)
            self.multi_cell(0, 4.5,
                'A renvoyer signe avec la mention : "Lu et approuve, bon pour accord"')

    # ===== BLOC SIGNATURE ÉLECTRONIQUE =====
    def _signature_block(self):
        """Affiché uniquement sur le PDF signé."""
        if not self.signer_name:
            return

        GREEN      = (22, 163, 74)
        GREEN_LITE = (240, 253, 244)
        GREEN_BORD = (187, 247, 208)

        try:
            from datetime import datetime
            dt = datetime.fromisoformat(str(self.signed_at).replace("Z", ""))
            signed_date = dt.strftime("%d/%m/%Y \u00e0 %H:%M")
        except Exception:
            signed_date = str(self.signed_at)

        self.ln(6)

        # Boîte verte
        x, y, w, h = 10, self.get_y(), 186, 26
        self.set_fill_color(*GREEN_LITE)
        self.set_draw_color(*GREEN_BORD)
        self.set_line_width(0.4)
        self.rect(x, y, w, h, style="FD")

        # Titre
        self.set_xy(x + 4, y + 3)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*GREEN)
        self.cell(0, 5, "Signature electronique")

        # Mention
        self.set_xy(x + 4, y + 9)
        self.set_font("Helvetica", "I", 8.5)
        self.set_text_color(31, 41, 55)
        self.cell(0, 5, "Lu et approuve, bon pour accord")

        # Signataire + date
        self.set_xy(x + 4, y + 15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 5, f"Signe par : {self.signer_name}   |   Date : {signed_date}")

    # ===== BUILD =====
    def _build(self):
        self._header_block()
        self._addresses_block()
        self._table_block()
        self._totals_block()
        self._payment_block()
        self._signature_block()


def generate_quote_pdf(company, client, quote, lines, job=None,
                       signer_name=None, signed_at=None, parent_amount=None):
    pdf = QuotePDF(company, client, quote, lines, job=job or {},
                   signer_name=signer_name, signed_at=signed_at,
                   parent_amount=parent_amount)
    return bytes(pdf.output())


# ─────────────────────────────────────────────────────────────
#  FACTURE PDF (acompte & finale)
# ─────────────────────────────────────────────────────────────

def _tva_map_from_lines(lines):
    """Retourne {tva_rate: tva_amount} calculé sur les lignes du devis."""
    tva = {}
    for l in lines:
        ht   = float(l.get("quantity", 1)) * float(l.get("unit_price", 0))
        rate = float(l.get("tva_rate", 10))
        tva[rate] = tva.get(rate, 0.0) + ht * rate / 100
    return tva


class InvoicePDF(FPDF):

    def __init__(self, company, client, invoice, quote, lines,
                 deposit_invoice=None, job=None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.company         = company
        self.client          = client
        self.invoice         = invoice
        self.quote           = quote or {}
        self.lines           = lines
        self.deposit_invoice = deposit_invoice or {}
        self.job             = job or {}
        self.inv_type        = invoice.get("invoice_type", "standard")
        self.set_margins(10, 10, 10)
        self.set_auto_page_break(auto=True, margin=18)
        self.add_page()
        self._build()

    # ── FOOTER ──
    def footer(self):
        self.set_y(-14)
        self.set_draw_color(*GRAY_LITE)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        parts = []
        c = self.company
        if _s(c.get("siret")):      parts.append(f"SIRET : {_s(c.get('siret'))}")
        if _s(c.get("tva_number")): parts.append(f"TVA : {_s(c.get('tva_number'))}")
        if _s(c.get("insurance_info")): parts.append(_s(c.get("insurance_info")))
        parts.append(f"Page {self.page_no()}")
        self.set_font("Helvetica", "", 6.5)
        self.set_text_color(*GRAY)
        self.cell(0, 4, "  ·  ".join(parts), align="C")

    # ── HEADER ──
    def _header_block(self):
        c    = self.company
        name = _s(c.get("company_name") or c.get("name")) or "Mon Entreprise"
        inv  = self.invoice
        tid  = _s(inv.get("tenant_id", ""))
        iid  = _s(inv.get("id", ""))

        TITLES = {
            "deposit":  "FACTURE D'ACOMPTE",
            "final":    "FACTURE FINALE",
            "standard": "FACTURE",
        }
        doc_title = TITLES.get(self.inv_type, "FACTURE")
        doc_num   = f"FAC-{tid}-{iid}"

        # Gauche : entreprise
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*BLUE)
        self.cell(100, 8, name, ln=False)

        # Droite : type de facture
        self.set_xy(130, 10)
        self.set_font("Helvetica", "B", 14)
        self.cell(70, 8, doc_title, align="R", ln=True)

        # Infos contact entreprise (gauche)
        self.set_x(10)
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(*GRAY)
        contact = [
            _s(c.get("address")),
            " ".join(filter(None, [_s(c.get("zip_code")), _s(c.get("city"))])),
            _s(c.get("phone")), _s(c.get("email")),
        ]
        y_left = 19
        for line in contact:
            if line.strip():
                self.set_xy(10, y_left)
                self.cell(100, 4.5, line)
                y_left += 4.5

        # Infos document (droite)
        ref_devis = f"DEV-{_s(self.quote.get('tenant_id', ''))}-{_s(self.quote.get('id', ''))}" \
            if self.quote.get("id") else ""
        items_r = [
            ("", doc_num),
            ("Date :", _date(inv.get("created_at"))),
            ("Echéance :", _date(inv.get("due_date"))),
            ("Réf. devis :", ref_devis),
        ]
        y_right = 20
        for label, val in items_r:
            if not val:
                continue
            self.set_xy(120, y_right)
            self.set_font("Helvetica", "B" if not label else "", 8.5)
            self.set_text_color(*GRAY if label else DARK)
            self.cell(30, 4.5, label, align="R")
            self.set_font("Helvetica", "B" if not label else "", 8.5)
            self.set_text_color(*DARK)
            self.cell(50, 4.5, val, align="R", ln=True)
            y_right += 4.5

        y_sep = max(y_left, y_right) + 3
        self.set_draw_color(*BLUE)
        self.set_line_width(0.4)
        self.line(10, y_sep, 200, y_sep)
        self.set_y(y_sep + 5)

    # ── ADRESSES ──
    def _addresses_block(self):
        cl  = self.client
        job = self.job

        client_name    = _s(cl.get("name")) or "—"
        client_addr    = _s(cl.get("address"))
        client_city    = " ".join(filter(None, [_s(cl.get("zip_code")), _s(cl.get("city"))]))
        client_country = _s(cl.get("country")) or "FRANCE"
        job_name       = _s(job.get("title")) or client_name
        job_addr       = _s(job.get("address")) or client_addr

        y = self.get_y()

        for x, title, lines_data in [
            (10,  "Adresse du chantier",   [job_name, job_addr]),
            (110, "Adresse de facturation", [client_name, client_addr, client_city, client_country]),
        ]:
            self.set_xy(x, y)
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(*GRAY)
            self.cell(90, 4, title)

            dy = y + 5
            for i, val in enumerate(lines_data):
                if val.strip():
                    self.set_xy(x, dy)
                    self.set_font("Helvetica", "B" if i == 0 else "", 8.5 if i == 0 else 8)
                    self.set_text_color(*DARK if i == 0 else GRAY)
                    self.cell(90, 4.5, val)
                    dy += 4.5

        self.set_y(y + 30)

    # ── TABLEAU ACOMPTE ──
    def _deposit_table(self):
        inv    = self.invoice
        quote  = self.quote
        pct    = float(inv.get("deposit_percent", 0))
        ht     = float(inv.get("amount", 0))

        # Recalculer la TVA proportionnellement
        tva_map  = _tva_map_from_lines(self.lines)
        total_tva_quote = sum(tva_map.values())
        ratio    = ht / float(quote.get("amount", 1)) if quote.get("amount") else 0
        tva_dep  = round(total_tva_quote * ratio, 2)
        ttc      = round(ht + tva_dep, 2)

        ref = f"DEV-{_s(quote.get('tenant_id', ''))}-{_s(quote.get('id', ''))}"
        label = f"Acompte {pct:.0f}% sur devis {ref}"
        if quote.get("title"):
            label += f" - {_s(quote.get('title'))}"

        # En-tête tableau
        headers = ["Désignation", "HT", "TVA", "TTC"]
        widths  = [120, 22, 22, 22]
        xs      = [10, 130, 152, 174]
        y = self.get_y()
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*DARK)
        for i, h in enumerate(headers):
            self.set_xy(xs[i], y)
            self.cell(widths[i], 6, h, align="L" if i == 0 else "R")
        self.set_y(y + 6)
        self.set_draw_color(*DARK)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 196, self.get_y())
        self.ln(2)

        # Ligne unique
        y = self.get_y()
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*DARK)
        self.set_xy(xs[0], y)
        self.multi_cell(widths[0] - 5, 5, label, border=0)
        row_h = max(10, self.get_y() - y)

        for i, val in enumerate([_eur(ht), _eur(tva_dep), _eur(ttc)]):
            self.set_xy(xs[i + 1], y + (row_h - 5) / 2)
            self.set_font("Helvetica", "", 8.5)
            self.cell(widths[i + 1], 5, val, align="R")

        self.set_y(y + row_h + 1)
        self.set_draw_color(160, 160, 160)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 196, self.get_y())
        self.ln(3)

        # Totaux
        self._totals_simple(ht, tva_dep, ttc)

    # ── TABLEAU FINALE ──
    def _final_table(self):
        quote   = self.quote
        dep_inv = self.deposit_invoice
        dep_ttc = 0.0
        dep_ref = ""

        if dep_inv:
            dep_ht  = float(dep_inv.get("amount", 0))
            tva_map_q = _tva_map_from_lines(self.lines)
            ratio     = dep_ht / float(quote.get("amount", 1)) if quote.get("amount") else 0
            dep_tva   = sum(tva_map_q.values()) * ratio
            dep_ttc   = round(dep_ht + dep_tva, 2)
            dep_ref   = f"FAC-{_s(dep_inv.get('tenant_id',''))}-{_s(dep_inv.get('id',''))}"

        # Réutiliser le même tableau que les devis
        HEADERS = ["Designation", "TVA", "Qte.", "Prix unit. HT", "Montant HT"]
        y = self.get_y()
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*DARK)
        for i, h in enumerate(HEADERS):
            self.set_xy(COL_X[i], y)
            self.cell(COL_W[i], 6, h, align="L" if i == 0 else "R")
        self.set_y(y + 6)
        self.set_draw_color(*DARK)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 196, self.get_y())
        self.ln(1)

        for line in self.lines:
            desig      = _s(line.get("designation"))
            desc       = _s(line.get("description"))
            tva_rate   = float(line.get("tva_rate", 10))
            qty        = float(line.get("quantity", 1))
            unit_price = float(line.get("unit_price", 0))
            total_ht   = qty * unit_price
            qty_str    = str(int(qty)) if qty == int(qty) else f"{qty:.2f}"

            y = self.get_y()
            self.set_xy(COL_X[0], y)
            self.set_font("Helvetica", "B", 8.5)
            self.set_text_color(*DARK)
            self.cell(COL_W[0], 6, desig)
            self.set_font("Helvetica", "", 8.5)
            for i, (val, col) in enumerate([
                (f"{tva_rate:.1f}%", 1), (qty_str, 2),
                (_eur(unit_price), 3), (_eur(total_ht), 4),
            ]):
                self.set_xy(COL_X[col], y)
                self.cell(COL_W[col], 6, val, align="R")
            self.set_y(y + 6)
            if desc.strip():
                self.set_xy(COL_X[0] + 2, self.get_y())
                self.set_font("Helvetica", "I", 7.5)
                self.set_text_color(*GRAY)
                self.multi_cell(COL_W[0] - 2, 4, desc, border=0)
                self.set_text_color(*DARK)
            self.set_draw_color(160, 160, 160)
            self.set_line_width(0.2)
            self.line(10, self.get_y(), 196, self.get_y())
            self.ln(1)

        self.ln(2)

        # Totaux + déduction acompte
        total_ht  = sum(float(l.get("quantity", 1)) * float(l.get("unit_price", 0)) for l in self.lines)
        tva_map   = _tva_map_from_lines(self.lines)
        total_tva = sum(tva_map.values())
        total_ttc = total_ht + total_tva
        reste     = round(total_ttc - dep_ttc, 2)

        x_l, x_v, w_l, w_v = 110, 163, 51, 33

        def _row(label, value, bold=False, big=False, color=DARK):
            sz = 9.5 if big else 8.5
            self.set_x(x_l)
            self.set_font("Helvetica", "B" if bold else "", sz)
            self.set_text_color(*color)
            self.cell(w_l, 5.5, label)
            self.set_font("Helvetica", "B" if bold else "", sz)
            self.cell(w_v, 5.5, value, align="R", ln=True)

        _row("Total HT", _eur(total_ht), bold=True)
        for rate, tva_amt in sorted(tva_map.items()):
            base = sum(float(l.get("quantity",1))*float(l.get("unit_price",0))
                       for l in self.lines if float(l.get("tva_rate",10)) == rate)
            _row(f"TVA {rate:.1f}% (base {_eur(base)})", _eur(tva_amt))

        y = self.get_y() + 1
        self.set_draw_color(*BLUE)
        self.set_line_width(0.3)
        self.line(x_l, y, 196, y)
        self.set_y(y + 2)
        _row("Total TTC", _eur(total_ttc), bold=True, big=False)

        if dep_ttc:
            _row(f"Acompte versé ({dep_ref})", f"- {_eur(dep_ttc)}", color=GRAY)
            y2 = self.get_y() + 1
            self.set_draw_color(*BLUE)
            self.set_line_width(0.4)
            self.line(x_l, y2, 196, y2)
            self.set_y(y2 + 2)
            self.set_x(x_l)
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(*BLUE)
            self.cell(w_l, 7, "Reste a payer")
            self.cell(w_v, 7, _eur(reste), align="R", ln=True)
        else:
            self.set_x(x_l)
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(*BLUE)
            self.cell(w_l, 7, "Total TTC")
            self.cell(w_v, 7, _eur(total_ttc), align="R", ln=True)

        self.ln(6)

    def _totals_simple(self, ht, tva, ttc):
        x_l, x_v, w_l, w_v = 120, 163, 41, 33

        def _row(label, value, bold=False, big=False):
            sz = 9.5 if big else 8.5
            self.set_x(x_l)
            self.set_font("Helvetica", "B" if bold else "", sz)
            self.set_text_color(*DARK)
            self.cell(w_l, 5.5, label)
            self.set_font("Helvetica", "B" if bold else "", sz)
            self.cell(w_v, 5.5, value, align="R", ln=True)

        _row("Total HT", _eur(ht), bold=True)
        _row("TVA",      _eur(tva))
        y = self.get_y() + 1
        self.set_draw_color(*BLUE)
        self.set_line_width(0.4)
        self.line(x_l, y, 196, y)
        self.set_y(y + 2)
        self.set_x(x_l)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*BLUE)
        self.cell(w_l, 7, "Total TTC")
        self.cell(w_v, 7, _eur(ttc), align="R", ln=True)
        self.ln(6)

    # ── NOTES ──
    def _notes_block(self):
        notes = _s(self.invoice.get("notes")).strip()
        if not notes:
            return
        self.ln(2)
        self.set_draw_color(*GRAY_LITE)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 196, self.get_y())
        self.ln(3)
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*DARK)
        self.cell(0, 5, "Description des travaux", ln=True)
        self.ln(1)
        self.set_font("Helvetica", "I", 8.5)
        self.set_text_color(*GRAY)
        self.multi_cell(0, 5, notes)
        self.ln(2)

    # ── PAIEMENT ──
    def _payment_block(self):
        c = self.company
        self.set_draw_color(*GRAY_LITE)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 196, self.get_y())
        self.ln(4)
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*DARK)
        self.cell(0, 5, "Informations de paiement", ln=True)
        self.ln(1)
        for label, key in [("IBAN", "iban"), ("BIC", "bic"), ("RGE", "rge_number")]:
            val = _s(c.get(key))
            if val:
                self.set_font("Helvetica", "B", 8)
                self.set_text_color(*GRAY)
                self.cell(22, 5, f"{label} :")
                self.set_font("Helvetica", "", 8)
                self.set_text_color(*DARK)
                self.cell(0, 5, val, ln=True)

    # ── BUILD ──
    def _build(self):
        self._header_block()
        self._addresses_block()
        if self.inv_type == "deposit":
            self._deposit_table()
        elif self.inv_type == "final":
            self._final_table()
        else:
            self._final_table()   # Standard = même que finale sans déduction
        self._notes_block()
        self._payment_block()


def generate_invoice_pdf(company, client, invoice, quote, lines,
                         deposit_invoice=None, job=None):
    pdf = InvoicePDF(company, client, invoice, quote, lines,
                     deposit_invoice=deposit_invoice, job=job or {})
    return bytes(pdf.output())
