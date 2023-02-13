
# IGC scrapping

transformer en client ligne de commande avec argument

argument : plafond_min, plafon_max, distance_min, distance_max, nom dossier output
Un premier scrapping sur plafond puis un second sur distance en mettant dans une map par clé id de vol poru pas avoir de doublon
voir imperva script click 

Etre capable de scrapper depuis plusieurs déco d'un meme site, exemple clecy deco S et déco O

Output dans dossier = nom du site, distance min, plafond min

# Analyse IGC 

Objectif 1 : lancer le script et trier par orientation du vent
Verifier que distance point déco point attero est bien superieur a min distance
Objectif 2 : comment virer les paramoteur ?
Objectif 3 : detecter les traces qui sont passées par un cercle pour pouvoir différencier les cross

comment detecter phase ? 
cheminement : trajectoire droite avec faible gain/perte de hauteur
transition : trajectoire droite avec perte de hauteur regulière
thermique : trajectoire circulaire avec gain
recherche : trajectoire chaotique sans gain

detecter vol paramoteur : periode de monté longue sans rotation avec gain de hauteur important


### Librairie wheel sur pypy
Comment gérer ce putain de spot Id ?
mylib --action=get-igc --min-distance --spot-id
mylib --action=filter-igc --distance-min-between-takeoff-and-landing=10 || --min-distance-from-point-gps=50.2,2.3 --min-distance-from-point-meter=100
