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


# Arquitectura del projecte


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


# Instal·lació i us


# Resultats


# Dificultats i solucions
Al llarg del desenvolupament del projecte, ens hem trobat amb diversos reptes tant en la fase de disseny com en la d'integració i posada en marxa del robot. A continuació es descriuen les principals dificultats:

## Integració i disseny mecànic
Dimensions incorrectes: En una primera versió del disseny, les dimensions d'algunes peces no s’ajustaven correctament entre elles, cosa que va dificultar el muntatge i va provocar que haguéssim de redissenyar part de l’estructura per adaptar-la millor als components reals.

Sistema d’elevació amb rosca infinita: La construcció d’un sistema funcional per pujar i baixar l’eix Z va suposar una dificultat important. Després d’explorar diferents opcions, vam decidir dissenyar i imprimir en 3D un mecanisme amb rosca infinita, que finalment es va adaptar bé al sistema.

## Problemes electrònics
Micromotor trencat: Durant les proves, el micromotor encarregat de l’eix Z es va avariar, cosa que ens va obligar a buscar-ne un de substitut compatible i tornar a ajustar el muntatge.

Cables cremats i connexions defectuoses: Alguns cables es van sobreescalfar i fondre, provocant interrupcions en el subministrament d’energia o en la transmissió de senyals. Això ens va portar a revisar completament les connexions i substituir diversos cables.

Coordinació de motors: Aconseguir que tots els motors funcionessin simultàniament i de manera estable va ser un procés llarg. Vam tenir problemes tant amb el codi de control com amb l’alimentació elèctrica, que inicialment no era suficient per alimentar tot el sistema alhora.


# Treball futur / millores


# Autors
Nil Mazouzi More - NIU: 1674092

Jan Sans Domingo - NIU: 1673276

Noah Nelson Carcelen - NIU: 1637982

Mauri Marquès Soto - NIU: 1673948
