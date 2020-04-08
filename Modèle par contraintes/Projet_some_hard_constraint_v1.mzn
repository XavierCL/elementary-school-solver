%include "ecole_de_rang_profs_dispos.dzn"; % super facile, profs ultra dispos
include "ecole_de_rang_temps_partiel.dzn"; % ultra hard, profs donnent tout juste ce qu'il faut pour que ça fonctionne
%include "school_1.dzn";
%include "school_2.dzn";
%include "school_3.dzn"; % not yet created
%include "ecole_a_Frank"; % not yet created


int: JOURS_CYCLE;
int: PERIODES_JOUR;
int: ANGLAIS;
int: EDUC_PHYS;
int: MUSIQUE;
int: SPECIALISTES;
int: PERIODES_AM;
int: PERIODES_PM;
int: NIVEAUX;
int: MAX_GROUPES;
int: TEMPS_PLEIN;
int: SPECIALITES_PAR_GROUPE;
int: PERIODES_CYCLE = JOURS_CYCLE * PERIODES_JOUR;
set of int: Jours_Cycle = 1..JOURS_CYCLE;
set of int: Periodes_Jour = 1..PERIODES_JOUR;
set of int: Specialistes = 1..SPECIALISTES;
set of int: Niveaux = 1..NIVEAUX;
set of int: Max_Groupes = 1..MAX_GROUPES;
set of int: Groupes = 1..(MAX_GROUPES*NIVEAUX);
array [Niveaux, Max_Groupes, Specialistes] of int: DEMANDE;
array [Specialistes, Jours_Cycle, Periodes_Jour] of int: DISPOS_SPECIALISTES;
array [Specialistes] of var int: Demande_Par_Specialiste;
array [Specialistes] of var int: Dispos_Par_Specialiste;
array [Niveaux, Max_Groupes] of var int: Demande_Par_Groupe;

constraint forall(sp in Specialistes) (Dispos_Par_Specialiste[sp] = sum([DISPOS_SPECIALISTES[sp, jc, pj] | jc in Jours_Cycle, pj in Periodes_Jour])); 

constraint forall(sp in Specialistes) (Demande_Par_Specialiste[sp] = sum([DEMANDE[nv, mg, sp] | nv in Niveaux, mg in Max_Groupes])); 
constraint forall(sp in Specialistes) (Demande_Par_Specialiste[sp] <= TEMPS_PLEIN); 

constraint forall(nv in Niveaux, mg in Max_Groupes) (Demande_Par_Groupe[nv, mg] = sum([DEMANDE[nv, mg, sp] | sp in Specialistes])); 
constraint forall(nv in Niveaux, mg in Max_Groupes) (Demande_Par_Groupe[nv, mg] = 9 \/ Demande_Par_Groupe[nv, mg] = 0); 

array [1..SPECIALISTES, 1..JOURS_CYCLE, 1..PERIODES_JOUR] of var 0..(NIVEAUX*MAX_GROUPES): HorairesSpecialistes;
array [1..SPECIALISTES, 1..JOURS_CYCLE, 1..PERIODES_JOUR] of var 0..1: Disponibiltes_Par_Specialistes; % 0 = non, 1 = oui

% tenir compte des jours de non-dispo des spécialistes
constraint forall(sp in Specialistes, jc in Jours_Cycle, pj in Periodes_Jour) (
      if DISPOS_SPECIALISTES[sp, jc, pj] == 0 then HorairesSpecialistes[sp, jc, pj] = 0 else true endif);

% périodes libres (identifiées 0) sont égales à périodes totales - périodes occupées (demande_par_spécialiste)
constraint forall(sp in Specialistes) (
      PERIODES_CYCLE - Demande_Par_Specialiste[sp] = count([HorairesSpecialistes[sp, jc, pj] | jc in Jours_Cycle, pj in Periodes_Jour], 0));

% l'horaire de chaque spécialiste doit contenir exactement le bon nombre de visites de chaque groupe
% un groupe est identifiable par la formule suivante: niveau*max_groupes - max_groupes + mg(groupe actuel)
constraint forall(nv in Niveaux, mg in Max_Groupes, sp in Specialistes) (
      DEMANDE[nv, mg, sp] = count([HorairesSpecialistes[sp, jc, pj] | jc in Jours_Cycle, pj in Periodes_Jour], (nv*MAX_GROUPES - MAX_GROUPES + mg)));

% périodes libres (identifiées 0) sont égales à périodes totales - périodes occupées (demande_par_spécialiste)
constraint forall(jc in Jours_Cycle, nv in Niveaux, mg in Max_Groupes) (
      count([HorairesSpecialistes[sp, jc, pj] | pj in Periodes_Jour, sp in Specialistes], (nv*MAX_GROUPES - MAX_GROUPES + mg)) <= 1);
  
  
% un tuteur doit n’avoir qu’UNE seule journée pleine (5 périodes), donc 9 jours de 4 périodes.
% un contractuel qui comble une tâche de tuteur ne doit PAS hériter de la journée pleine.
% en terme de contraintes d'horaires de spécialistes, si un contractuel est présent à certaines journées du cycle, ces journées doivent avoir exactement UNE spécialité à l'horaire


% à chaque 10% de réduction de tâche, on doit libérer une journée complète et à chaque 5% de plus, on doit regrouper les périodes libres 
%pour libérer un avant-midi ou après-midi de congé). Par exemple, une tâche à 75% implique un horaire de 7 jours complets et une demi-journée.
% pour les tuteurs, une école va indiquer au départ quel(s) jour(s) le contractuel va venir combler la tâche.
% une réduction de tâche pour un spécialiste signifie qu'un contractuel donnera les cours de spécialité à certains jours fixes.
% pour le contractuel, on ne doit pas se soucier des journées pleines à 5 périodes parce qu'il se voit plutôt assigner certaines groupes (ex: les 5e et 6e années, 2 groupes par niveau)



% un contractuel n’est disponible que lors de jours fixes (ex: seulement les jours 1 et 6)
% les périodes de spécialité doivent être bien réparties dans le cycle. Par exemple, pour une spécialité à deux périodes, on souhaite une distance idéale de 5 jours (jours 1 et 6, 2 et 7, etc.) en plus d’avoir une période le matin et l’autre en après-midi.
% un spécialiste peut se déplacer d'un pavillon à l'autre (faisant partie de la même école) ou d’une école à l’autre lors d'une journée (tâche combinée dans plusieurs écoles), mais on veut minimiser ces déplacements et/ou les prévoir lors du dîner.
% pour des raisons sonores, un local polyvalent de spécialité peut être non disponible pour la musique si son local adjacent est occupé lors de certaines plages horaires.
% les spécialistes préfèrent regrouper les groupes de même niveau (ex: voir les 2 groupes de 3e année un à la suite de l'autre)

solve satisfy;

output[show(SPECIALISTES) ++ " spécialistes: " ++ show(ANGLAIS) ++ " d'anglais, " ++ show(EDUC_PHYS) ++ " d'éducation physique et " ++ show(MUSIQUE) ++ " de musique."];
output["\nDemande par spécialiste:" ++ show(Demande_Par_Specialiste)];
output["\n Dispos par spécialiste:" ++ show(Dispos_Par_Specialiste)];
output["\nMATRICE CONSTRUITE POUR ", show(MAX_GROUPES * NIVEAUX), " GROUPES:"];
output["\nDemande par groupe:" ++ show(Demande_Par_Groupe) ++ "\n"];
output[show_int(2, HorairesSpecialistes[sp, jc, pj]) ++ if jc == max(Jours_Cycle) then "\n" else " " endif ++ if jc == max(Jours_Cycle) /\ pj == max(Periodes_Jour) then "\n" else "" endif | sp in Specialistes, pj in Periodes_Jour, jc in Jours_Cycle];
