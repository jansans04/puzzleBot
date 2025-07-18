# PuzzleBot
Aquest projecte ha estat desenvolupat dins de l'assignatura de Robòtica de la Universitat Autònoma de Barcelona. L’objectiu és construir un robot capaç de resoldre puzles de manera autònoma. El robot funciona de manera similar a una màquina CNC, però incorpora una ventosa i una bomba de succió que li permeten agafar i col·locar peces amb precisió.


# Taula de contingut
   * [Objectius](#Objectius)
   * [Funcionament del sistema](#Funcionament-del-sistema)
   * [Arquitectura del projecte](#Arquitectura-del-projecte)
   * [Materials i components](#Materials-i-components)
   * [Software](#Software)
   * [Instal·lació i us](#Instal·lació-i-us)
   * [Resultats](#Resultats)
   * [Treball futur / millores](#Treball-futur-/-millores)
   * [Autors](#Autors)


# Objectius
L’objectiu principal d’aquest projecte és dissenyar i construir un robot capaç de resoldre puzles de forma autònoma, identificant la posició de les peces i col·locant-les correctament sobre una base.

Per assolir aquest objectiu general, es plantegen els següents objectius específics:

Dissenyar i construir un sistema robòtic funcional amb moviment controlat en 2D (com una màquina CNC) que permeti desplaçar-se amb precisió dins d’un pla de treball.

Implementar un sistema de manipulació d’objectes, mitjançant una ventosa i una bomba de succió, per agafar i deixar anar peces amb fiabilitat.

Desenvolupar el programari de control del robot, incloent la generació de trajectòries i la gestió de la interacció amb els diferents components (motores, ventosa, sensors...).

Garantir la precisió i repetibilitat dels moviments, per assegurar que les peces del puzle es col·loquin correctament.

Integrar i provar el sistema complet, realitzant tests pràctics amb diferents puzles per validar-ne el funcionament i detectar possibles millores.


# Funcionament del sistema

El robot ha estat dissenyat per operar de manera similar a una màquina CNC, amb l’objectiu de col·locar peces de puzle amb precisió sobre una superfície de treball. El sistema combina moviment mecànic, components electrònics i control programat a través d’una Raspberry Pi. A continuació es detallen els diferents subsistemes:

## Sistema mecànic
Moviment en els eixos X i Y: S'aconsegueix mitjançant corretges dentades, rodaments i barres de ferro llises que proporcionen una base estable i precisa. L'eix X està accionat per dos motors pas a pas que treballen de manera sincronitzada, mentre que l'eix Y utilitza un únic motor pas a pas.

Eix Z (vertical): Controlat per un micromotor connectat a una rosca infinita, que permet elevar o baixar la ventosa amb precisió.

Rotació de peces: S’inclou un servomotor addicional que permet girar les peces abans de col·locar-les, assegurant que s’ajustin correctament a la seva posició final.

Sistema de succió: Format per una ventosa i una bomba de succió, permet agafar les peces de manera segura i controlar-ne la col·locació.

## Posicionament i referència
Per establir el punt d'origen del robot (coordenada 0,0), s’utilitzen dos sensors de final de cursa, un per a cada eix (X i Y). Aquests sensors permeten al sistema fer un calibratge inicial i garantir que tots els moviments posteriors siguin precisos i repetibles.

## Electrònica i control
Unitat de control principal: Una Raspberry Pi s’encarrega de gestionar el comportament global del robot, executant el programari que coordina els moviments, la succió i la rotació.

Controladors de motor: Cada motor pas a pas està connectat a un driver de control, alimentat mitjançant una font d'alimentació externa, que proporciona la potència necessària per al moviment estable i controlat dels eixos.

Interfície de control: El sistema pot rebre instruccions preprogramades per resoldre un puzle determinat, i l’arquitectura està pensada per permetre fàcilment una ampliació cap a un sistema més intel·ligent o interactiu.

## Visió artificial
El robot incorpora una càmera Pi connectada a la Raspberry Pi. Aquesta càmera s’utilitza per detectar la posició i orientació de les peces del puzle sobre la superfície de treball. Mitjançant tècniques bàsiques de processament d’imatge, el sistema pot identificar quines peces estan disponibles i on es troben, facilitant la seva manipulació de manera automatitzada.

# Arquitectura del projecte
L’arquitectura del projecte PuzzleBot està organitzada en diversos nivells funcionals que es comuniquen de forma coordinada per assolir l’objectiu final: resoldre un puzle de manera autònoma. Aquesta estructura modular permet dividir clarament les responsabilitats entre el maquinari, el programari i la interacció entre ambdós.

En el nivell físic, el sistema està format per una base mecànica que proporciona moviment precís en els eixos X, Y i Z, juntament amb un conjunt de dispositius per manipular les peces (ventosa, bomba de succió i servomotor de rotació). Aquests elements són accionats mitjançant controladors electrònics que responen a ordres directes de la Raspberry Pi, la qual actua com a cervell del robot.

El programari s'encarrega de coordinar les diferents accions del sistema. A partir d’una imatge inicial del puzle, s’aplica visió artificial per localitzar les peces i generar una seqüència d’accions per col·locar-les. Aquestes accions es transformen en moviments concrets, enviats des de la Raspberry Pi als diversos actuadors mitjançant els GPIO i els drivers corresponents.

A nivell d'integració, el sistema es basa en una arquitectura lineal i seqüencial, però deixa oberta la porta a futures ampliacions cap a sistemes més intel·ligents o paral·lels. Tots els components comparteixen una alimentació comuna i una referència espacial establerta mitjançant sensors de final de cursa, que permeten un calibratge automàtic i fiable.

En conjunt, l’arquitectura del PuzzleBot reflecteix una combinació entre precisió mecànica, simplicitat electrònica i flexibilitat programàtica, que facilita tant el desenvolupament com la futura extensió del projecte.

# Materials i components
A continuació es detallen els components utilitzats per a la construcció del robot, dividits en tres grans grups: electrònica, mecànica i altres elements auxiliars.

## Electrònica
3 × Motors pas a pas NEMA 17

- 2 per a l’eix X (muntats en paral·lel)

- 1 per a l’eix Y

1 × Micromotor DC amb reductora

- Utilitzat per controlar el moviment de l’eix Z mitjançant una rosca infinita

1 × Servomotor SG90 o similar

- Per girar les peces abans de col·locar-les

1 × Bomba de succió de 5V

- Per agafar i moure les peces mitjançant una ventosa

2 × Finals de cursa

- Per detectar el punt 0,0 (X i Y)

3 × Drivers de motors pas a pas (com A4988 o DRV8825)

1 × Font d'alimentació de 12V

- Per alimentar motors i bomba

1 × Raspberry Pi (model 3B, 4 o similar)

- Unitat de control principal

1 × Càmera Pi per Raspberry

- Per a la detecció de peces mitjançant visió artificial

Cables, connectors i protoboard

## Mecànica
Corretges dentades GT2 i politges

- Per transmetre el moviment als eixos X i Y

Barres llises de ferro o acer inoxidable

- Guies lineals per al moviment suau dels eixos

Rodaments lineals LM8UU i LM12UU

- Per reduir la fricció en el desplaçament

Rosca infinita i femella acoblada

- Per al moviment vertical de l’eix Z

Estructura de suport feta amb fusta

Peces impreses en 3D per incorporar els components

## Altres
Ventosa de silicona petita

Tubs de silicona per a la succió

Tornilleria, separadors i femelles

Base de treball

# Software  

La carpeta **`src/`** conté tot el codi; està organitzada en mòduls auto-contenuts.  

| Carpeta / Fitxer | Paper dins el sistema |
|------------------|-----------------------|
| **main.py** | Punt d’entrada de la Raspberry. Modes: online (`socket`) i offline (`plan.json`). |
| **control.py** | FSM central: llegeix plans, invoca `movement.py`, escolta `feedback.py` i envia estats al PC. |
| **movement.py** | Mòdul **Moviment**. Drivers dels 2 NEMA-17 (X), NEMA-17 (Y), 28BYJ-48 (Z), servo i bomba. Inclou rampes i homing. |
| **feedback.py** | Mòdul **Retroalimentació**. Fil que vigila finals de carrera, presòstat de buit i E-Stop; dispara callbacks al Control. |
| **planificació.py** | Mòdul **Planificació**. Construeix la llista de pick / place a partir de les matrius de l’estat inicial/final (greedy NN). |
| **configuracio.py** | **Paràmetres clàssics** dels motors (pins DIR/STEP, micro-stepping, pas d’husillo). El mantindrem per compatibilitat amb el codi antic. |
| **sockets/** | Comunicació Pi ↔ PC |
| ├─ `config.py` | Config global (*pins*, IP PC, paràmetres mecànics). Es pot sobreescriure amb variables d’entorn. |
| ├─ `socket_client_pi.py` | Client TCP (corre a la Pi). Envia `HELLO` i `STATUS`, rep `PLAN`. |
| └─ `socket_server_pc.py` | Servidor TCP (corre al PC). Rep `HELLO`, genera el plan amb els mòduls de visió/greedy, l’envia i monitora l’estat. |
| **vision/** | Mòdul **Percepció** (PC) |
| ├─ `main.py` | Pipeline complet de visió. |
| ├─ `segment_pieces.py` | Segmentació de peces amb OpenCV. |
| ├─ `normalize_pieces.py` | Normalitza imatges per al solver. |
| ├─ `solve_puzzle_borders.py` | Detecta contorn, orienta tauler. |
| ├─ `piezas_info.json` | Sortida: posició i angle actual de cada peça. |
| ├─ `solution_greedy.json` | Resultat del solver: posició final/rotació. |
| └─ carpetes `in/`, `out_piezas/`, `pieces/` | Entrades i sortides intermèdies de visió. |

**Flux resumit**

1. **Visió (PC)**: detecta peces ⇒ `solution_greedy.json`.  
2. **socket_server_pc.py**: tradueix a `PLAN` i l’envia a la Pi.  
3. **socket_client_pi.py**: rep `PLAN` i l’entrega a `control.py`.  
4. **control.py**: executa ordres amb `movement.py`, vigila `feedback.py`.  
5. Estat (`READY`, `DONE`, `FINISHED`, `ERROR`) torna al PC via socket.

Aquesta arquitectura modular permet canviar qualsevol bloc (visió, algoritme, mecànica) sense reescriure la resta del codi.



# Resultats

Aquest projecte ha representat un repte molt més gran del que inicialment imaginàvem. Tot i que l'objectiu semblava clar i assolible, el procés de disseny, construcció i integració del sistema ha resultat ser molt més complex, amb múltiples dificultats tant tècniques com logístiques.

Durant el desenvolupament ens hem trobat amb problemes inesperats: des d’errors mecànics i electrònics, fins a limitacions en la coordinació entre el maquinari i el programari. Això ens ha obligat a adaptar-nos constantment, buscar solucions creatives i modificar diversos aspectes del disseny inicial.

Tot i aquestes complicacions, estem molt satisfets amb el resultat final. El robot que hem aconseguit construir s’ajusta molt al que havíem plantejat al principi del projecte: és capaç de detectar peces, moure’s dins del pla de treball, manipular les peces amb la ventosa i col·locar-les correctament a la seva posició.

A més, hem pogut dur a terme els tests i les proves pràctiques que ens havíem proposat, i aquests han demostrat que el sistema és funcional i té una base sòlida per a futures millores. Més enllà del resultat tècnic, aquest projecte ha estat una experiència d’aprenentatge intens i realista sobre el treball en equip, la resolució de problemes i la integració de sistemes complexos.


# Dificultats i solucions
Al llarg del desenvolupament del projecte, ens hem trobat amb diversos reptes tant en la fase de disseny com en la d'integració i posada en marxa del robot. A continuació es descriuen les principals dificultats:

## Integració i disseny mecànic
Dimensions incorrectes: En una primera versió del disseny, les dimensions d'algunes peces no s’ajustaven correctament entre elles, cosa que va dificultar el muntatge i va provocar que haguéssim de redissenyar part de l’estructura per adaptar-la millor als components reals.

Sistema d’elevació amb rosca infinita: La construcció d’un sistema funcional per pujar i baixar l’eix Z va suposar una dificultat important. Després d’explorar diferents opcions, vam decidir dissenyar i imprimir en 3D un mecanisme amb rosca infinita, que finalment es va adaptar bé al sistema.

## Problemes electrònics
Micromotor trencat: Durant les proves, el micromotor encarregat de l’eix Z es va avariar, cosa que ens va obligar a buscar-ne un de substitut compatible i tornar a ajustar el muntatge.

Cables cremats i connexions defectuoses: Alguns cables es van sobreescalfar i fondre, provocant interrupcions en el subministrament d’energia o en la transmissió de senyals. Això ens va portar a revisar completament les connexions i substituir diversos cables.

Coordinació de motors: Aconseguir que tots els motors funcionessin simultàniament i de manera estable va ser un procés llarg. Vam tenir problemes tant amb el codi de control com amb l’alimentació elèctrica, que inicialment no era suficient per alimentar tot el sistema alhora.


# Autors
Nil Mazouzi More - NIU: 1674092

Jan Sans Domingo - NIU: 1673276

Noah Nelson Carcelen - NIU: 1637982

Mauri Marquès Soto - NIU: 1673948
