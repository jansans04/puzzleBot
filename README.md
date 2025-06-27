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

El sistema de control del PuzzleBot es basa en una arquitectura de programari modular, totalment desenvolupada en Python i pensada per ser executada sobre una Raspberry Pi. El codi cobreix tres àrees principals: **visió artificial**, **control de moviment** i **coordinació de la manipulació**.

## Estructura general

El repositori s’organitza en diferents subcarpetes i scripts, cadascun amb una funcionalitat ben definida:

## Estructura del programari per mòduls

El programari del PuzzleBot segueix una arquitectura modular basada en els següents components, inspirats directament en la divisió funcional del sistema:

- **Mòdul de Percepció**
  - Equival a la carpeta `visio/`
  - S’encarrega de capturar la imatge amb la càmera, processar-la, segmentar les peces del puzle i identificar-ne la posició, l’orientació i la forma de cada costat. Aquest mòdul proporciona tota la informació visual necessària per la resta del sistema.

- **Mòdul de Resolució**
  - Inclou la lògica de resolució dins de `visio/` i part del `main.py`
  - Utilitza la informació del mòdul de percepció per calcular com encaixar totes les peces del puzle: determina la solució òptima i genera una seqüència d’accions per col·locar cada peça al seu lloc.

- **Mòdul de Planificació**
  - Integrat en el flux de `main.py`
  - Rep la solució del puzle i transforma cada acció planificada (agafar, moure, girar, deixar) en una trajectòria concreta per als motors del robot, planificant tot el moviment des de l’inici fins a la posició final.

- **Mòdul de Moviment**
  - Equival a la carpeta `control/`
  - Gestiona el moviment físic dels motors pas a pas dels eixos X i Y, el micromotor de l’eix Z i el servomotor de rotació. S’encarrega d’executar les ordres de moviment planificades i comprovar la posició amb els sensors de final de cursa.

- **Mòdul de Control**
  - Implementat principalment al `main.py`
  - Orquestra i sincronitza tots els altres mòduls. Rep informació dels sensors, gestiona l’ordre d’execució de cada acció (moviment, succió, col·locació), i assegura la coordinació global entre hardware i software.

- **Mòdul de Retroalimentació**
  - Forma part del bucle principal de control i monitorització al `main.py`
  - Supervisa l’estat dels motors, sensors i actuadors en tot moment. Detecta errors, ajusta el comportament segons la resposta del sistema i permet repetir accions o corregir desviacions si es produeix alguna incidència durant el procés.


## Funcionament del programari

1. **Captura i processament d’imatge:**  
   El sistema utilitza la càmera Pi per obtenir una imatge de la zona de treball. Aquesta imatge es processa mitjançant OpenCV i NumPy per identificar totes les peces de puzle, determinar-ne la posició, l’orientació i la forma de cada costat. S’apliquen tècniques de segmentació, normalització i classificació de costats (vegeu apartat de visió artificial).

2. **Resolució del puzle (matching):**  
   A partir de la informació de les peces identificades, el sistema calcula la solució del puzle:  
   - Si el puzle és conegut (sintètic), es fa servir un algoritme de matching basat en descriptors geomètrics i de color per decidir la posició de cada peça.
   - El sistema genera una llista ordenada d’accions (pickup, move, rotate, drop) per a cada peça, indicant la posició d’origen i la posició final sobre el tauler.

3. **Generació de trajectòries i control de motors:**  
   Les accions generades es tradueixen a moviments concrets dels motors X, Y i Z, tenint en compte el calibratge inicial amb els finals de cursa. Els motors s’accionen utilitzant una llibreria de control per GPIO o mitjançant comandes G-code simplificades.

4. **Manipulació i col·locació de les peces:**  
   El sistema activa la ventosa i la bomba de succió per agafar la peça, la transporta fins a la posició correcta, ajusta la seva orientació amb el servomotor si cal, i allibera la peça exactament a la seva posició final. Tot aquest procés es repeteix fins que el puzle està complet.

5. **Seguretat i comprovacions:**  
   El programari incorpora comprovacions de posició, temps d’espera i feedback dels sensors per garantir que no es produeixin col·lisions ni moviments fora dels límits establerts.




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
