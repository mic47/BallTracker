Sledovanie guličiek na videu:

Odporúčam si prečítať najskôr celé README.txt, až potom skúšať program.

INSTALACIA

Aby to fungovalo, potrebuješ mať nainštalovaný python (2.7), numpy a opencv (+
binding na python).  Pre linux to znamená nainštalovať si balíčky python,
pyton-numpy a python-opencv. Pre windows to znamená nainštalovať si nasledovné
veci:

Python:
http://www.python.org/ftp/python/2.7.3/python-2.7.3.msi

Numpy:
http://sourceforge.net/projects/numpy/files/NumPy/1.7.0/numpy-1.7.0-win32-superpack-python2.7.exe/download

OpenCV:
http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.4/OpenCV-2.4.4.exe/download
Toto posledne iba spusti, co ti rozbali archiv. Najdi v tom subor
opencv\build\python\2.7\cv2.pyd a skopiruj ho do C:\Python27\Lib\site-packages
(ak si instaloval do standardnych adresarov). 

ZAKLADNE POUZITIE

Program treba spustit z príkazového riadku. Má 2 parametre:
* Meno suboru s videom
* Meno výstupného súbory (odporúča sa koncovka .cvs , potom to vie excel otvoriť)

Príklad (predpokladáme, že si uložil súbor tracker.py do toho istého adresára
ako video): spusti cmd (Start->run napis cmd). Otvori sa ti konzola. Presun sa
do adresara s videami: 

cd <adresar s videami>

Napíš do konzoly toto:

C:\Python27\python.exe tracker.py video.avi data.csv

Toto otvorí dve okná, jedno na nastavovanie všelijakých parametrov, druhé s
videom. Video tam vidíš 4 krát (v štyroch kvadrantoch):

2. kvadrant obsahuje originálne video

4. kvadrant obsahuje frame z videa ktorý obsahuje len pozadie (žiadne guličky
ani ruky) -- ak to tak nie je, tak si zapätaj číslo framu ktorý obsahuje len
pozadie

3. kvadrant obsahuje rozdiel medzi pozadím a videom (v ideálnom prípade je
všetko čierne, okrem vecí čo nie sú na pozadí) 

1. kvadrant obsahuje dáta z 3. kvadrantu tak, že čokoľvek jasnejšie ako nejaká
konštanta je biele a všetko ostatné je čierne. V tomto kvadrante by guličky
mali byť biele a všetko ostatné čierne (v ideálnom prípade).

1. aj 2. kvadrant navyše obsahujú aj momentálne detegované objekty aj s ich
dráhami.

Nad videami sú dve posuvné lišty. Prvá ukazuje v ktorom frame sme (nedá sa to
meniť, ale vidíš kde vo videu si a číslo framu), druhá hovorí o rýchlosti
prehrávajúceho videa (skús si to ponastavovať a uvidíš).

Druhé okno obsahuje rôzne parametre, ktoré si môžeš nastavovať a v prvom okne
budeš vydieť čo robia (vysvetlím ich neskôr).

Program buď vypneš pomocou klávesy escape, alebo počkáš kým prejde cez celé
video. Na konci to zapíše do výstupného súboru (v príklade to je data.csv) 
dráhy guličiek.

Navyše program vypíše do konzoly parametre, s ktorými sa dá spustiť tak, že
parametre budú nastavené tak ako si nastavil počas tohto behu programu.

VYSTUPNY SUBOR

Vystupny súbor je tabuľka. Prvý stĺpec obsahuje číslo framu v ktorom sme
detegovali nejaký objekt (framy ktoré neobsahujú žiadny objekt tam nie sú),
druhý stĺpec obsahuje čas ktorý zodpovedá tomu framu. Potom nasledujú 3 stĺpce
pre každý detegovaný objekt: X, Y, priemer

AKO PROGRAM FUNGUJE

Táto časť je dôležitá aby sme vedeli čo znamenajú jednotlivé parametre na
nastavovanie. Je možné, že na rôznych videách bude treba prestavovať parametre.

1.) Najskôr program extrahuje frame ktorý obsahuje len pozadie (číslo framu je
parameter programu).

2.) Potom každý obrázok z videa spracuje nasledovne (všetko sa robí v čierno
bielej): 

2.1) Zosvetli ho imageMult krát (výsledok sa zobrazuje v 2.  kvadrante).  

2.2) Odrátaj odváhované pozadie (váhujeme podla rozdielu svetelnosti obrazov).
Výsledok sa zobrazuje v 3. kvadrante.  

2.3) Binarizuj obrázok: čokolvek svetelnejšie ako binaryThreshold je biele,
ostatné je čierne 

2.4) Nájdi objekty na obrázku. Pre každý objekt: 

2.4.1) Vypočítam ako veľmi sa podobá na kruh. Ak je to viac ako
ballRatioThreshold, zahoď objekt.  

2.4.2) Ak má objekt plochu viac ako ballMaxVolume, zahoď ho.  

2.4.3) Ak má objekt plochu menšiu ako ballMinVolume, zahoď ho.  

2.4.4) Ak som objekt ešte nezahodil, idem si ho zapamätať: 

2.4.4.1) Nájdem najbližší objekt v predchádzajúcich framoch.  Ak je tento
objekt vzdialený viac ako trackerMaxDistance, tak som našiel nový objekt. Ak to
nie je nový objekt, tak si zaznamenám novú polohu.

2.4.5) Ak som objekt nevidel trackerMaxMissingFrames framov, považujem ho za
odstránený z plochy. Ak si pre neho pamätám aspoň trackerMinLivespan, tak si ho
uložím, ináč ho zahodím, lebo objekty s veľmi krátkou históriou sú asi chybné 
detekcie.

Body 1 - 2.4 riešia ako nájsť objekty. Nájdu veľa kandidátov, ale veľa z nich
nie sú tie objekty ktoré nás zaujímavé.  Body 2.4.1 - 2.4.4 filtrujú nájdené
objekty na tie, ktoré už asi naozaj sú tie čo chceme. Bod 2.4.4.1 vytvára
históriu pohybov jednotlivých objektov a bod 2.4.5 by mal odstrániť posledné
chybné detekcie. Samozrejme, nejaké chybné detekcie sa asi ešte nájdu a možno aj
niektoré veci minieme.

PARAMETRE PROGRAMU

Ak chceme výpis všetkých možných parametrov, napíšeme
C:\Python27\python.exe tracker.py --help

Popis jednotlivých parametrov (každý z nich má prednastavené hodnoty, tak že
fungujú dobre na videu MARS.MP4, pre iné videá to možno treba nastaviť ináč):

--emptyFrame N
Číslo framu N ktorý obsahuje frame bez guličiek a rúk (len
pozadie). Ak toto bude nastavené zle, program nebude fungova5 korektne.

--binaryThreshold X 
Všetko s jasom nad X bude biele, ostatné bude čierne. 
  
--imageMult X
X krát zosvetliť vstupný obrázok. Ak sú videá svetlé, treba tento parameter
znížiť (ak je to vysoké, tak veľmi biele farby pretečú do čiernej).

--ballRatioThreshold X
Ak je to nula, tak za objekt považujeme iba dokonalé kruhy zobrazené v 1.
kvadrante.  Čím je to väčšie, tým nedokonalejšie kruhy dovolíme. V praxi sa mi
osvedčila hodnota 0.4

--ballMinVolume X
Objekty ktoré majú menšiu plochu ako X budeme ignorovať.

--ballMaxVolume X
Objekty ktoré majú väčšiu plochu ako X budeme ignorovať.
  
--trackerMinLivespan X
Ak objekt nezaznamenáme aspoň X krát, tak ho nedáme do výstupného súboru (lebo
pravdepodobne to je niečo iné, ako sme chceli)
  
--trackerMaxDistance X
Ako najviac sa môže posunúť objekt medzi framami (aby ak jeden objekt zmizne a
vzápätí sa objaví iný niekde úplne inde, aby sme ich nepovažovali za ten istý
objekt).

--trackerMaxMissingFrames X
Ak objekt nedetegujeme viac ako X framov, predpokladáme že bol odstránený z
plochy.

--speed X
Rozdiel medzi zobrazeými framami je X milisekúnd (Ale ak to počíta5 nebude
stíhať, tak to bude viac ako X milisekúnd)

--singleWindow 
Nastavenia parametrov budú v tom istom okne ako video.

--noGUI
Chceme iba spracovať video, necheme otvárať žiadne okná (takto je to výrazne
rýchlejšie, ale nevidíš čo sa deje).

--skip SKIP [SKIP ...]
Toto chce párny počet argumentov. Sú to intervaly framov, ktoré preskočiť
(napríklad ak tam nie je nič zaujímavé)


Príklad:

Parametre môžeme dávať v ľubovoľnom poradí. Napríklad chceme objekty s
minimálnou plochou 10, vstupné obrázky chceme zosvetliť iba 2.5 krát a chceme
preskočič framy 0 až 800 a 1400 až 4000, tak napíšeme:

C:\Python27\python.exe tracker.py --imageMult 2.5 video.avi data.csv --ballMinVolume 10 --skip 0 800 1400 4000

Ak by sme nechceli žiadne okná a chceme len výstupný súbor, tak napíšeme:

C:\Python27\python.exe tracker.py --imageMult 2.5 video.avi data.csv --ballMinVolume 10 --skip 0 800 1400 4000 --noGUI


NA ČO SI DAŤ POZOR

1.) Ak sa výrazne zmenia podmienky počas videa (svetelnosť, veľkosť guličiek,
...) tak to môže prestať fungovať. Také videá odporúčam rozdeliť na viaceré s
rovnakou svetelnosťou (či niečím iným) a na každom videu nájsť vhodné
parametre.  Možno časom spravím verziu kde to nebude problém, ale nespoliehal
by som sa na to.

2.) Nie všetko vo výstupe budú naozaj guličky. Síce by sme mali odfiltrovať
náhodný šum, ale stále sa tam môžu byť ešte nejaké veci ako napríklad
stacionárne objekty a podobne.

3.) Ak sa gulička dotkne veľkej strednej gule, tak častu ju program prestane
detegovať.

4.) Niekedy sa stane, že chvíľku nedetegujeme guličku (asi kvôli tieňu), tak
zvyšok trajektórie bude ako nový objekt.
