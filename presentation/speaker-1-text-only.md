# Govorec 1 — Samo besedilo

---

## Prosojnica 1 — Naslovnica

Dobro jutro. Predstavljamo: Štetje 4-ciklov v polno dinamičnih grafih — z vidika cikličnih stikov.

Jaz sem [tvoje ime]. Z menoj so [Govorec 2], [Govorec 3] in [Govorec 4].

V petnajstih minutah vas želimo prepričati, da je ta članek vreden vašega časa. Začnimo.

---

## Prosojnica 2 — Motivacijski primer

Štirje računi. Z računa a gre nakazilo na b, z b na c, s c na d, in z d nazaj na a.

Rdeče puščice sledijo 4-ciklu v grafu transakcij. Sklenjena zanka plačil. To je značilen vzorec pri odkrivanju goljufij — denar zapusti račun in se po verigi posrednikov vrne nazaj.

Formalno gre za ciklično konjunktivno poizvedbo: štiri relacije, sklenjene v zanko. Število rezultatov poizvedbe je natanko število 4-ciklov v grafu.

Enaka oblika se pojavlja povsod. Cikli citatov v akademskih mrežah. Skupine z vzajemnim sledenjem na družbenih omrežjih. Priporočilne zanke v grafih izdelkov.

In pri tem se graf neprestano spreminja.

Kaj to pomeni za algoritem, če se graf nenehno spreminja?

---

## Prosojnica 3 — Polno dinamično okolje

Vsaka nova transakcija doda eno povezavo. Nekatere se razveljavijo — to so brisanja. Po vsaki posodobitvi mora sistem sporočiti natančno število 4-ciklov.

Pri velikih grafih je ponovno računanje od začetka predrago. Potrebujemo hitre posodobitve pri vsaki spremembi.

In tu naredimo ostro razliko. Strošek, ki ga merimo, je čas najpočasnejše posodobitve — ne povprečje čez celotno zaporedje.

Podatkovne baze so občutljive na repne zakasnitve. Ena sama sekundna posodobitev je v produkciji incident — tudi če je povprečje hitro. Amortizirane meje takšne izstopajoče primere skrijejo. Meje v najslabšem primeru ne.

Cilj je torej oster: biti hitrejši od ponovnega izračuna od začetka, in to z zagotovilom v najslabšem primeru za vsako posamezno posodobitev.

Kako dobro to dejansko zmore literatura?

---

## Prosojnica 4 — Pokrajina

Trije majhni vzorci. Tri najboljše znane meje za posodobitev v najslabšem primeru.

Trikotniki — tri-cikli — koren iz m. Čist, naraven eksponent.

4-klike — linearno v m. Spet čist eksponent.

In 4-cikli — naš vzorec — m na dve tretjini. Nenavaden eksponent. Niti kvadratni koren, niti linearno.

Vse do lani je ta meja dveh tretjin veljala kot najboljši znani rezultat — in mnogi so verjeli, da je tudi končna.

Zato [Govorcu 2] izročam vprašanje: zakaj so 4-cikli obstali pri dveh tretjinah — in kaj se je spremenilo?
