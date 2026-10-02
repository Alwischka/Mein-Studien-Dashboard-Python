import json
import tkinter as tk
from tkinter import ttk

from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from enum import Enum
from pathlib import Path


# --------------------------------------------------
# Enums
# --------------------------------------------------

class Pruefungsart(Enum):
    PORTFOLIO = "Portfolio"
    KLAUSUR = "Klausur"
    ADVANCED_WORKBOOK = "Advanced Workbook"


class Modulstatus(Enum):
    GEPLANT = "Geplant"
    IN_BEARBEITUNG = "In Bearbeitung"
    IN_BEWERTUNG = "In Bewertung"
    ABGESCHLOSSEN = "Abgeschlossen"


class Studientempo(Enum):
    SCHNELL = "Schnell"
    PLANMAESSIG = "Planmäßig"
    LANGSAM = "Langsam"


# --------------------------------------------------
# Domain-Klassen
# --------------------------------------------------

@dataclass
class Pruefungsleistung:
    art: Pruefungsart
    frist: date | None = None
    leistungsdatum: date | None = None
    note: float | None = None


@dataclass
class Modul:
    name: str
    status: Modulstatus
    pruefungsleistung: Pruefungsleistung
    ects: int
    abschlussdatum: date | None = None
    anerkannt: bool = False

    def __post_init__(self):
        if (
            self.status == Modulstatus.ABGESCHLOSSEN
            and self.abschlussdatum is None
            and not self.anerkannt
        ):
            raise ValueError(
                "Ein abgeschlossenes Modul benötigt ein Abschlussdatum."
            )

        if (
            self.status != Modulstatus.ABGESCHLOSSEN
            and self.abschlussdatum is not None
        ):
            raise ValueError(
                "Ein nicht abgeschlossenes Modul darf kein Abschlussdatum haben."
            )


@dataclass
class Semester:
    nummer: int
    module: list[Modul] = field(default_factory=list)


@dataclass
class Studiengang:
    name: str
    startdatum: date
    geplantes_enddatum: date
    gesamt_ects: int
    gesamt_module: int
    semester: list[Semester] = field(default_factory=list)


# --------------------------------------------------
# Repository
# --------------------------------------------------

class JsonStudienRepository:
    """Speichert und lädt die Studiendaten in einer JSON-Datei."""

    def __init__(self, dateipfad: str):
        self.dateipfad = dateipfad

    def speichere_daten(
        self,
        studiengang: Studiengang
    ) -> None:
        """Speichert einen Studiengang als JSON-Datei."""

        daten = asdict(studiengang)

        with open(
            self.dateipfad,
            "w",
            encoding="utf-8"
        ) as datei:
            json.dump(
                daten,
                datei,
                ensure_ascii=False,
                indent=4,
                default=self._konvertiere_fuer_json
            )

    def lade_daten(self) -> Studiengang:
        """Lädt die Studiendaten aus JSON und erstellt die Objekte neu."""

        with open(
            self.dateipfad,
            "r",
            encoding="utf-8"
        ) as datei:
            daten = json.load(datei)

        semester_liste = []

        for semester_daten in daten["semester"]:
            module = []

            for modul_daten in semester_daten["module"]:
                pruefung_daten = modul_daten["pruefungsleistung"]

                pruefungsleistung = Pruefungsleistung(
                    art=Pruefungsart(
                        pruefung_daten["art"]
                    ),
                    frist=(
                        date.fromisoformat(
                            pruefung_daten["frist"]
                        )
                        if pruefung_daten["frist"] is not None
                        else None
                    ),
                    leistungsdatum=(
                        date.fromisoformat(
                            pruefung_daten["leistungsdatum"]
                        )
                        if pruefung_daten["leistungsdatum"] is not None
                        else None
                    ),
                    note=pruefung_daten["note"]
                )

                modul = Modul(
                    name=modul_daten["name"],
                    status=Modulstatus(
                        modul_daten["status"]
                    ),
                    pruefungsleistung=pruefungsleistung,
                    ects=modul_daten["ects"],
                    abschlussdatum=(
                        date.fromisoformat(
                            modul_daten["abschlussdatum"]
                        )
                        if modul_daten["abschlussdatum"] is not None
                        else None
                    ),
                    anerkannt=modul_daten["anerkannt"]
                )

                module.append(modul)

            semester = Semester(
                nummer=semester_daten["nummer"],
                module=module
            )

            semester_liste.append(semester)

        return Studiengang(
            name=daten["name"],
            startdatum=date.fromisoformat(
                daten["startdatum"]
            ),
            geplantes_enddatum=date.fromisoformat(
                daten["geplantes_enddatum"]
            ),
            gesamt_ects=daten["gesamt_ects"],
            gesamt_module=daten["gesamt_module"],
            semester=semester_liste
        )

    def _konvertiere_fuer_json(self, wert):
        """Konvertiert Datums- und Enum-Werte für die JSON-Speicherung."""

        if isinstance(wert, date):
            return wert.isoformat()

        if isinstance(wert, Enum):
            return wert.value

        raise TypeError(
            f"{type(wert).__name__} kann nicht als JSON gespeichert werden."
        )


# --------------------------------------------------
# Prüfungsleistungen und Module
# --------------------------------------------------

# Projekt: Objektorientierte und funktionale Programmierung mit Python
pruefung_oop = Pruefungsleistung(
    art=Pruefungsart.PORTFOLIO
)

modul_oop = Modul(
    name="Projekt: Objektorientierte und funktionale Programmierung mit Python",
    status=Modulstatus.IN_BEARBEITUNG,
    pruefungsleistung=pruefung_oop,
    ects=5
)


# Einführung in das wissenschaftliche Arbeiten für IT und Technik
pruefung_wissenschaftliches_arbeiten = Pruefungsleistung(
    art=Pruefungsart.PORTFOLIO,
    leistungsdatum=date(2026, 8, 25)
)

modul_wissenschaftliches_arbeiten = Modul(
    name="Einführung in das wissenschaftliche Arbeiten für IT und Technik",
    status=Modulstatus.IN_BEWERTUNG,
    pruefungsleistung=pruefung_wissenschaftliches_arbeiten,
    ects=5
)


# Medizin für Nichtmediziner:innen I
pruefung_medizin = Pruefungsleistung(
    art=Pruefungsart.KLAUSUR,
    leistungsdatum=date(2026, 6, 12),
    note=2.7
)

modul_medizin = Modul(
    name="Medizin für Nichtmediziner:innen I",
    status=Modulstatus.ABGESCHLOSSEN,
    pruefungsleistung=pruefung_medizin,
    ects=5,
    abschlussdatum=date(2026, 7, 10)
)


# Einführung in die Programmierung mit Python
pruefung_python = Pruefungsleistung(
    art=Pruefungsart.KLAUSUR,
    leistungsdatum=date(2026, 7, 17),
    note=2.3
)

modul_python = Modul(
    name="Einführung in die Programmierung mit Python",
    status=Modulstatus.ABGESCHLOSSEN,
    pruefungsleistung=pruefung_python,
    ects=5,
    abschlussdatum=date(2026, 7, 22)
)


# E-Health
pruefung_ehealth = Pruefungsleistung(
    art=Pruefungsart.KLAUSUR,
    leistungsdatum=date(2026, 8, 4),
    note=2.0
)

modul_ehealth = Modul(
    name="E-Health",
    status=Modulstatus.ABGESCHLOSSEN,
    pruefungsleistung=pruefung_ehealth,
    ects=5,
    abschlussdatum=date(2026, 8, 17)
)


# Einführung in die Informatik
pruefung_informatik = Pruefungsleistung(
    art=Pruefungsart.KLAUSUR,
    leistungsdatum=date(2026, 9, 13)
)

modul_informatik = Modul(
    name="Einführung in die Informatik",
    status=Modulstatus.IN_BEWERTUNG,
    pruefungsleistung=pruefung_informatik,
    ects=5
)


# Anatomie und Physiologie - anerkannt
pruefung_anatomie = Pruefungsleistung(
    art=Pruefungsart.KLAUSUR
)

modul_anatomie = Modul(
    name="Anatomie und Physiologie",
    status=Modulstatus.ABGESCHLOSSEN,
    pruefungsleistung=pruefung_anatomie,
    ects=5,
    anerkannt=True
)


# --------------------------------------------------
# Semester und Studiengang
# --------------------------------------------------

semester_1 = Semester(
    nummer=1,
    module=[
        modul_medizin,
        modul_python,
        modul_ehealth,
        modul_anatomie,
        modul_wissenschaftliches_arbeiten,
        modul_informatik,
        modul_oop
    ]
)


studiengang = Studiengang(
    name="Medizinische Informatik",
    startdatum=date(2026, 5, 18),
    geplantes_enddatum=date(2030, 5, 18),
    gesamt_ects=180,
    gesamt_module=35,
    semester=[semester_1]
)


# --------------------------------------------------
# Service-Klasse
# --------------------------------------------------

class DashboardService:
    """Enthält die Berechnungen und Auswertungen für das Dashboard."""

    def zaehle_abgeschlossene_module(
        self,
        studiengang: Studiengang
    ) -> int:
        """Ermittelt die Anzahl der abgeschlossenen Module."""

        anzahl = 0

        for semester in studiengang.semester:
            for modul in semester.module:
                if modul.status == Modulstatus.ABGESCHLOSSEN:
                    anzahl += 1

        return anzahl

    def berechne_studienfortschritt(
        self,
        studiengang: Studiengang
    ) -> float:
        """Berechnet den Studienfortschritt in Prozent."""

        abgeschlossene_module = (
            self.zaehle_abgeschlossene_module(
                studiengang
            )
        )

        return (
            abgeschlossene_module
            / studiengang.gesamt_module
            * 100
        )

    def berechne_prognose_enddatum(
        self,
        studiengang: Studiengang
    ) -> date:
        """Prognostiziert das Studienende anhand des bisherigen Tempos."""

        abgeschlossene_module = []

        for semester in studiengang.semester:
            for modul in semester.module:
                if (
                    modul.status == Modulstatus.ABGESCHLOSSEN
                    and not modul.anerkannt
                    and modul.abschlussdatum is not None
                ):
                    abgeschlossene_module.append(modul)

        abgeschlossene_ects = sum(
            modul.ects
            for modul in abgeschlossene_module
        )

        letztes_abschlussdatum = max(
            modul.abschlussdatum
            for modul in abgeschlossene_module
        )

        anerkannte_ects = 0

        for semester in studiengang.semester:
            for modul in semester.module:
                if modul.anerkannt:
                    anerkannte_ects += modul.ects

        selbst_zu_erarbeiten = (
            studiengang.gesamt_ects
            - anerkannte_ects
        )

        vergangene_tage = (
            letztes_abschlussdatum
            - studiengang.startdatum
        ).days

        prognose_tage = (
            vergangene_tage
            / abgeschlossene_ects
        ) * selbst_zu_erarbeiten

        return (
            studiengang.startdatum
            + timedelta(days=prognose_tage)
        )

    def bestimme_studientempo(
        self,
        studiengang: Studiengang
    ) -> Studientempo:
        """Vergleicht das prognostizierte mit dem geplanten Studienende."""

        prognose_enddatum = (
            self.berechne_prognose_enddatum(
                studiengang
            )
        )

        if (
            prognose_enddatum
            < studiengang.geplantes_enddatum
        ):
            return Studientempo.SCHNELL

        elif (
            prognose_enddatum
            > studiengang.geplantes_enddatum
        ):
            return Studientempo.LANGSAM

        else:
            return Studientempo.PLANMAESSIG

    def berechne_notendurchschnitt(
        self,
        studiengang: Studiengang
    ) -> float | None:
        """Berechnet den Durchschnitt aller vorhandenen Noten."""

        noten = []

        for semester in studiengang.semester:
            for modul in semester.module:
                note = modul.pruefungsleistung.note

                if note is not None:
                    noten.append(note)

        if not noten:
            return None

        return sum(noten) / len(noten)

    def ermittle_fristen(
        self,
        studiengang: Studiengang
    ) -> list[Modul]:
        """Ermittelt maximal drei kommende Prüfungs- und Abgabefristen."""

        module_mit_frist = []

        for semester in studiengang.semester:
            for modul in semester.module:

                if (
                    modul.pruefungsleistung.frist is not None
                    and modul.pruefungsleistung.frist >= date.today()
                    and modul.status in (
                        Modulstatus.GEPLANT,
                        Modulstatus.IN_BEARBEITUNG
                    )
                ):
                    module_mit_frist.append(modul)

        module_mit_frist.sort(
            key=lambda modul: modul.pruefungsleistung.frist
        )

        return module_mit_frist[:3]


# --------------------------------------------------
# Controller
# --------------------------------------------------

class DashboardController:
    """Verbindet Repository und Service und bereitet die Dashboard-Daten vor."""

    def __init__(
        self,
        repository: JsonStudienRepository,
        service: DashboardService
    ):
        self.repository = repository
        self.service = service

    def lade_dashboard_daten(self) -> dict:
        """Lädt und bündelt alle Daten für die Darstellung im Dashboard."""

        studiengang = self.repository.lade_daten()

        return {
            "studiengang": studiengang.name,
            "abgeschlossene_module":
                self.service.zaehle_abgeschlossene_module(
                    studiengang
                ),
            "gesamt_module":
                studiengang.gesamt_module,
            "studienfortschritt":
                self.service.berechne_studienfortschritt(
                    studiengang
                ),
            "notendurchschnitt":
                self.service.berechne_notendurchschnitt(
                    studiengang
                ),
            "studientempo":
                self.service.bestimme_studientempo(
                    studiengang
                ),
            "prognose_enddatum":
                self.service.berechne_prognose_enddatum(
                    studiengang
                ),
            "geplantes_enddatum":
                studiengang.geplantes_enddatum,
            "fristen":
                self.service.ermittle_fristen(
                    studiengang
                )
        }


# --------------------------------------------------
# View
# --------------------------------------------------

class DashboardView:
    """Stellt die Dashboard-Daten grafisch mit tkinter dar."""

    def zeige_dashboard(
        self,
        daten: dict
    ) -> None:
        """Erzeugt und zeigt das Studien-Dashboard."""

        fenster = tk.Tk()
        fenster.title("Mein Studien-Dashboard")
        fenster.geometry("620x600")

        # Titel
        titel = tk.Label(
            fenster,
            text="MEIN STUDIEN-DASHBOARD",
            font=("Arial", 18, "bold")
        )
        titel.pack(pady=(20, 15))

        # Studienfortschritt
        fortschritt_frame = tk.Frame(
            fenster,
            relief="groove",
            borderwidth=1
        )
        fortschritt_frame.pack(
            fill="x",
            padx=20,
            pady=5
        )

        tk.Label(
            fortschritt_frame,
            text="STUDIENFORTSCHRITT",
            font=("Arial", 12, "bold")
        ).pack(pady=(15, 10))

        tk.Label(
            fortschritt_frame,
            text=(
                f"{daten['abgeschlossene_module']} / "
                f"{daten['gesamt_module']} Module"
            ),
            font=("Arial", 11)
        ).pack(pady=5)

        fortschrittsbalken = ttk.Progressbar(
            fortschritt_frame,
            orient="horizontal",
            length=280,
            mode="determinate",
            maximum=100,
            value=daten["studienfortschritt"]
        )
        fortschrittsbalken.pack(pady=5)

        tk.Label(
            fortschritt_frame,
            text=f"{daten['studienfortschritt']:.1f} %".replace(".", ",")
        ).pack(pady=(5, 15))

        # Studientempo und Notendurchschnitt
        mitte_frame = tk.Frame(fenster)
        mitte_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        tempo_frame = tk.Frame(
            mitte_frame,
            relief="groove",
            borderwidth=1
        )
        tempo_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5)
        )

        tk.Label(
            tempo_frame,
            text="STUDIENTEMPO",
            font=("Arial", 11, "bold")
        ).pack(pady=(15, 25))

        tk.Label(
            tempo_frame,
            text=daten["studientempo"].value.upper(),
            font=("Arial", 13)
        ).pack(pady=(0, 25))

        note_frame = tk.Frame(
            mitte_frame,
            relief="groove",
            borderwidth=1
        )
        note_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(5, 0)
        )

        tk.Label(
            note_frame,
            text="NOTENDURCHSCHNITT",
            font=("Arial", 11, "bold")
        ).pack(pady=(15, 5))

        canvas = tk.Canvas(
            note_frame,
            width=100,
            height=90,
            highlightthickness=0
        )
        canvas.pack(pady=(0, 10))

        canvas.create_oval(
            25,
            10,
            75,
            60,
            width=2
        )

        note = daten["notendurchschnitt"]

        if note is None:
            note_text = "-"
        else:
            note_text = f"{note:.2f}".replace(".", ",")

        canvas.create_text(
            50,
            35,
            text=note_text,
            font=("Arial", 12, "bold")
        )

        # Prüfungs- und Abgabefristen
        fristen_frame = tk.Frame(
            fenster,
            relief="groove",
            borderwidth=1
        )
        fristen_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(5, 20)
        )

        tk.Label(
            fristen_frame,
            text="PRÜFUNGS- UND ABGABEFRISTEN",
            font=("Arial", 11, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        if daten["fristen"]:

            for modul in daten["fristen"]:

                frist = modul.pruefungsleistung.frist
                tage = (frist - date.today()).days

                zeile = tk.Frame(fristen_frame)
                zeile.pack(
                    fill="x",
                    padx=15,
                    pady=5
                )

                tk.Label(
                    zeile,
                    text=modul.name,
                    anchor="w",
                    width=38
                ).pack(
                    side="left"
                )

                tk.Label(
                    zeile,
                    text=frist.strftime("%d.%m.%Y"),
                    width=12
                ).pack(
                    side="left"
                )

                tk.Label(
                    zeile,
                    text=f"{tage} Tage",
                    width=10
                ).pack(
                    side="left"
                )

        else:

            tk.Label(
                fristen_frame,
                text="Keine anstehenden Fristen"
            ).pack(
                anchor="w",
                padx=15,
                pady=5
            )

        fenster.mainloop()


# --------------------------------------------------
# App
# --------------------------------------------------

class DashboardApp:
    """Steuert den Start des Dashboards."""

    def __init__(
        self,
        controller: DashboardController,
        view: DashboardView
    ):
        self.controller = controller
        self.view = view

    def start(self) -> None:
        """Lädt die Dashboard-Daten und öffnet die grafische Oberfläche."""

        daten = (
            self.controller.lade_dashboard_daten()
        )

        self.view.zeige_dashboard(
            daten
        )


# --------------------------------------------------
# Programmstart
# --------------------------------------------------

if __name__ == "__main__":

    dateipfad = "studiengang.json"

    repository = JsonStudienRepository(
        dateipfad
    )

    # Startdaten nur speichern,
    # wenn noch keine JSON-Datei vorhanden ist
    if not Path(dateipfad).exists():
        repository.speichere_daten(
            studiengang
        )

    service = DashboardService()

    controller = DashboardController(
        repository=repository,
        service=service
    )

    view = DashboardView()

    app = DashboardApp(
        controller=controller,
        view=view
    )

    app.start()