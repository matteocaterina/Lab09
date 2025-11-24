from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi
        self.tour_disponibili = []
        self.tour_attrazioni = []
        self.max_giorni = None
        self.max_budget = None

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """
        # TODO

        self.tour_attrazioni = TourDAO.get_tour_attrazioni()

        for id in self.tour_attrazioni:
            id_tour = id['id_tour']
            id_attrazione = id['id_attrazione']

            tour = self.tour_map.get(id_tour)
            attrazione = self.attrazioni_map.get(id_attrazione)

            if attrazione and tour:
                tour.attrazioni.add(attrazione)
                attrazione.tour.add(tour)


    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1
        # TODO

        self.max_giorni = None if max_giorni is None else int(max_giorni)
        self.max_budget = None if max_budget is None else float(max_budget)

        self.tour_disponibili = [tour for tour in self.tour_map.values() if tour.id_regione == id_regione]

        self._ricorsione(0, [], 0, 0, 0, set())


        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):

        # SE HO VALUTATO TUTTI I TOUR, CONTROLLO SE IL PACCHETTO CORRENTE È IL MIGLIORE
        if start_index == len(self.tour_disponibili):
            if valore_corrente > self._valore_ottimo:
                self._valore_ottimo = valore_corrente
                self._costo = costo_corrente
                self._pacchetto_ottimo = pacchetto_parziale.copy()
            return

        #SALTO IL TOUR CORRENTE
        self._ricorsione(
            start_index + 1,
            pacchetto_parziale,
            durata_corrente,
            costo_corrente,
            valore_corrente,
            attrazioni_usate,
        )

        #INCLUDO IL TOUR CORRENTE
        tour = self.tour_disponibili[start_index]
        attrazioni_nuove = [attrazione for attrazione in tour.attrazioni if attrazione not in attrazioni_usate]

        if attrazioni_nuove:
            nuova_durata = durata_corrente + tour.durata_giorni
            nuovo_costo = costo_corrente + tour.costo
            nuovo_valore = valore_corrente + sum(a.valore_culturale for a in attrazioni_nuove)

            # VERIFICA VINCOLI DEL BUDGET E DELLA DURATA, SE OK PROSEGUO
            if (self.max_giorni is None or nuova_durata <= self.max_giorni) and (
                    self.max_budget is None or nuovo_costo <= self.max_budget
            ):
                # CREO UNA COPIA DEL SET DELLE ATTRAZIONI PRIMA DI AGGIUNGERE LE NUOVE
                nuova_attrazioni_usate = attrazioni_usate.copy()
                for attrazione in attrazioni_nuove:
                    nuova_attrazioni_usate.add(attrazione)  # AGGIUNGO LE ATTRAZIONI ALLA COPIA

                pacchetto_parziale.append(tour)
                self._ricorsione(
                    start_index + 1,
                    pacchetto_parziale,
                    nuova_durata,
                    nuovo_costo,
                    nuovo_valore,
                    nuova_attrazioni_usate
                )

                # BACKTRACKING: RIMUOVO IL TOUR DALLA LISTA
                pacchetto_parziale.pop()
