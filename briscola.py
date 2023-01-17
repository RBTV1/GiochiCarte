import random
from classes import Giocatore, Mazzo, Carta, si_o_no
from collections import defaultdict

class GiocatoreBriscola(Giocatore):
    def __init__(self, nome) -> None:
        super().__init__(nome)
        self.punti = 0
        self.dict_punti = {1: 11, 3: 10, 10: 4, 9: 3, 8: 2}
        self.carte_vinte = []

    def aggiungi_carte_vinte(self, carte_vinte: list or dict):
        assert len(set(carte_vinte)) == len(carte_vinte), "Una carta tra quelle vinte si ripete"
        
        self.carte_vinte += [carta for carta in carte_vinte]

    def conta_punti(self):
        punti_totali = 0
        for carta in self.carte_vinte:
            try:
                punti_totali += self.dict_punti[int(carta.key[1:])]
            except:
                pass
        return punti_totali

class Briscola():
    def __init__(self) -> None:
        self.mazzo = Mazzo()
        self.mazzo.assegna_punti(dict_punti = {
            1: 11, 
            3: 10, 
            10: 4, 
            9: 3, 
            8: 2})

        self.init_giocatori()
        while input("Volete iniziare? (s/n) ").lower()[0] != 's':
            pass
        self.init_distribuisci_carte()
        self.pesca_briscola()
        self.chi_inizia()

        while len(self.mazzo.carte) > 0 or len(self.giocatori[self.giocatore_iniziale].carte_in_mano) > 0:
            self.turno()
            self.check_ultimo_turno()
        
        self.conta_punti_giocatori()
        print("Fine partita!")
        print(f"Complimenti {self.vincitore}")

    def init_giocatori(self):
        self.giocatori = {}
        self.numero_giocatori = int(input("In quanti volete giocare?"))
        self.contro_AI = False

        assert isinstance(self.numero_giocatori, int), "Non ho mai sentito mezze persone giocare a briscola. Metti un numero intero pls."

        if self.numero_giocatori == 1:
            self.contro_AI = si_o_no(
                "Sei da solo: vuoi giocare contro l'AI? (s/n) ", 
                "Ottimo, allora in bocca al lupo!", 
                "Allora nada. Ricomincia il gioco se ti va.")
            
            print("Initializing AI...")
            self.giocatori["Giocatore"] = GiocatoreBriscola(nome="Giocatore")
            self.giocatori["AI"] = GiocatoreBriscola(nome='AI')

            return None

        elif self.numero_giocatori == 3:
            coppe_2 = self.mazzo.togli_carta(Carta("Coppe", 2))
            print(f"Dato che siete in 3 tolgo il 2 di Coppe, che e' la piu' inutile")

        elif self.numero_giocatori in [2,4]:
            print(f"Ottimo, siete {self.numero_giocatori} giocatori")
            
        elif self.numero_giocatori == 5:
            print("Mi dispiace ma non si puo' giocare per il momento a Briscola chiamata")
        
        elif self.numero_giocatori > 5:
            print("Il numero massimo di giocatori e' 4")      

        else:
            raise ValueError("Non so come interpretare questo valore. Inserisci un numero intero tra 1 e 4.")    

        print("Ora inserite i vostri nomi\n")
        if self.numero_giocatori == 4:
            print("Comincia la squadra 1\n")
            self.squadre = defaultdict(list)
            squadra_id = 1

        for i, giocatore in enumerate(range(self.numero_giocatori), start=1):
            if self.numero_giocatori == 4 and i == 3:
                print("Ora la squadra 2\n")
                squadra_id = 2
            nome = input(f"Giocatore {i}: ")
            self.giocatori[nome] = GiocatoreBriscola(nome=nome)
            self.squadre[f'squadra{squadra_id}'].append(nome)

        print(f"\nBenvenuti: {[nome for nome in self.giocatori.keys()]}")

    def init_distribuisci_carte(self):
        print("\nInizio a distribuire le carte\n")
        for i in range(3):
            self.giocatori_pescano()

    def pesca_briscola(self):
        self.carta_fondo = self.mazzo.pesca_carta()
        self.seme_briscola = self.carta_fondo.seme
        print(f"La carta sul fondo e' un {self.carta_fondo}")
        print(f"Il seme di briscola quindi e' {self.seme_briscola}\n")

    def check_ultimo_turno(self):
        if len(self.mazzo.carte) == self.numero_giocatori-1:
            print("Attenzione giocatori, questo e' l'ultimo giro!")

    def turno(self):
        # print(len(self.mazzo.carte))
        ordine_giocatori = self.set_ordine_giocatori()
        [print(self.giocatori[giocatore].nome, self.giocatori[giocatore].carte_in_mano) 
               for giocatore in ordine_giocatori]
        print("")
        
        carte_giocate = []
        for i, giocatore in enumerate(ordine_giocatori):
            mossa_sbagliata = True
            opzioni = list(range(len(self.giocatori[giocatore].carte_in_mano)))

            while mossa_sbagliata:
                carta_id = input(f"{self.giocatori[giocatore]}: scegli una delle tue carte (opzioni: {opzioni}) ")
                try:
                    carta_id = int(carta_id)
                    if carta_id in opzioni:
                        mossa_sbagliata = False
                    else:
                        print(f"Plesae metti solo una delle seguenti opzioni: {opzioni}")
                except:
                    print("C'e' qualche errore nell'input")

            carte_giocate.append(self.giocatori[giocatore].usa_carta(carta_id))
            print(carte_giocate[i])

        id_giocatore_vincente = self.chi_prende_la_mano(carte_giocate)
        giocatore_vincente = ordine_giocatori[id_giocatore_vincente]
        print(f"Prende la mano {giocatore_vincente}\n")
        self.giocatore_iniziale = giocatore_vincente

        self.giocatori[giocatore_vincente].aggiungi_carte_vinte(carte_giocate)
        ordine_giocatori = self.set_ordine_giocatori()
        if len(self.mazzo.carte) > 0:
            self.giocatori_pescano(ordine_giocatori)

    def giocatori_pescano(self, ordine_giocatori=None):
        if ordine_giocatori is None:
            ordine_giocatori = self.giocatori.keys()
        for giocatore in ordine_giocatori:
            if len(self.mazzo.carte) == 0:
                self.giocatori[giocatore].pesca_carta_fondo(self.carta_fondo) 
            else:
                self.giocatori[giocatore].pesca_carta(self.mazzo)

    def chi_prende_la_mano(self, carte_giocate):
        carta_vincente = carte_giocate[0]
        id_giocatore_vincente = 0
        for i, carta in enumerate(carte_giocate[1:], start=1):
            if carta_vincente.seme == self.seme_briscola:
                if carta.seme == self.seme_briscola and carta.punti > carta_vincente.punti:
                    carta_vincente = carta
                    id_giocatore_vincente = i
            elif carta.seme == self.seme_briscola:
                carta_vincente = carta
                id_giocatore_vincente = i
            elif carta.seme != self.seme_briscola and carta_vincente.seme == carta.seme:
                if carta.punti > carta_vincente.punti:
                    carta_vincente = carta
                    id_giocatore_vincente = i

        return id_giocatore_vincente

    def chi_inizia(self):
        giocatori = list(self.giocatori.keys())
        random.shuffle(giocatori)
        self.giocatore_iniziale = giocatori[0]
        print(f"\nInizia {self.giocatore_iniziale}!")

    def set_ordine_giocatori(self):
        list_giocatori = list(self.giocatori.keys())
        for id_inizio, nome in enumerate(list_giocatori):
            if nome == self.giocatore_iniziale:
                break
        ordine_giocatori = list_giocatori[id_inizio:] + list_giocatori[:id_inizio]
        return ordine_giocatori

    def conta_punti_giocatori(self):
        punti_giocatori = {}

        if self.numero_giocatori == 4:
            for squadra_id, squadra in self.squadre.items():
                punti_squadra = 0
                for giocatore_id in squadra:
                    punti_squadra += self.giocatori[giocatore_id].conta_punti()
                punti_giocatori[squadra_id] = punti_squadra
        else:
            for nome, giocatore in self.giocatori.items():
                punti_giocatori[nome] = giocatore.conta_punti()

        print(punti_giocatori)
        
        if len(set(punti_giocatori.values())) != len(punti_giocatori.values()):
            self.vincitore = "Pareggio"
        else:
            self.vincitore = max(punti_giocatori, key=punti_giocatori.get)

    def __repr__(self) -> str:
        return f"Gioco di Briscola con {self.numero_giocatori} giocatori"


if __name__ == '__main__':
    briscola = Briscola()