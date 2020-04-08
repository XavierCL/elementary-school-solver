%include "ecole_de_rang_profs_dispos.dzn"; % super facile, profs ultra dispos
%include "ecole_de_rang_temps_partiel.dzn"; % plus tough, car les dispos des profs sont serrées
%include "school_1.dzn";
%include "school_2.dzn";
%include "school_isabelle; % not yet created
include "school_frank.dzn";


int: JOURS_CYCLE;
int: PERIODES_JOUR;
int: SPECIALISTES;
int: NIVEAUX;
int: MAX_GROUPES;
int: TEMPS_PLEIN;
int: SPECIALITES_PAR_GROUPE;
int: PERIODES_CYCLE = JOURS_CYCLE * PERIODES_JOUR;
set of int: Jours_Cycle = 1..JOURS_CYCLE;
set of int: Periodes_Jour = 1..PERIODES_JOUR;
set of int: Specialistes = 1..SPECIALISTES;
set of int: Specialites_par_groupe = 1..SPECIALITES_PAR_GROUPE;
set of int: Niveaux = 1..NIVEAUX;
set of int: Max_Groupes = 1..MAX_GROUPES;
set of int: Groupes = 1..(MAX_GROUPES*NIVEAUX);
set of int: Periodes_Cycle = 1..PERIODES_CYCLE;
array [Niveaux, Max_Groupes, Specialistes] of int: DEMANDE;
array [Niveaux, Max_Groupes] of int: PAVILLONS;
array [Groupes, Jours_Cycle] of int: DISPOS_TUTEURS;
array [Specialistes, Jours_Cycle, Periodes_Jour] of int: DISPOS_SPECIALISTES;
array [Specialistes] of var int: Demande_Par_Specialiste;
array [Specialistes] of var int: Dispos_Par_Specialiste;
array [Groupes] of var int: Demande_Par_Groupe;


constraint forall(sp in Specialistes) (Dispos_Par_Specialiste[sp] = sum([DISPOS_SPECIALISTES[sp, jc, pj] | jc in Jours_Cycle, pj in Periodes_Jour])); 
constraint forall(sp in Specialistes) (Demande_Par_Specialiste[sp] = sum([DEMANDE[nv, mg, sp] | nv in Niveaux, mg in Max_Groupes])); 
% soft 41 périodes sur 50 parce que certains profs peuvent avoir plus de 100% de tâche
%constraint forall(sp in Specialistes) (Demande_Par_Specialiste[sp] <= TEMPS_PLEIN); 

% permet d'obtenir le total de classes de spécialités par groupe (généralement égal à 9)
constraint forall(nv in Niveaux, mg in Max_Groupes) (
    Demande_Par_Groupe[(nv*MAX_GROUPES - MAX_GROUPES + mg)] = sum([DEMANDE[nv, mg, sp] | sp in Specialistes]));

% cette contrainte n'est plus vraie, maternelles et 6e en anglais intensif ont moins de 9 spécialités...
%constraint forall(nv in Niveaux, mg in Max_Groupes) (Demande_Par_Groupe[nv, mg] = SPECIALITES_PAR_GROUPE \/ Demande_Par_Groupe[nv, mg] = 0); 
% cette contrainte qui valide la borne max de 9 est quelque peu redondante...
%constraint forall(nv in Niveaux, mg in Max_Groupes) (Demande_Par_Groupe[nv, mg] <= SPECIALITES_PAR_GROUPE); 


array [1..SPECIALISTES, 1..JOURS_CYCLE, 1..PERIODES_JOUR] of var 0..(NIVEAUX*MAX_GROUPES): HorairesSpecialistes;
% tenir compte des jours de non-dispo des spécialistes
constraint forall(sp in Specialistes, jc in Jours_Cycle, pj in Periodes_Jour) (
      if DISPOS_SPECIALISTES[sp, jc, pj] == 0 then HorairesSpecialistes[sp, jc, pj] = 0 else true endif);

% double check puisque valider le nombre de périodes libres équivaut à valider le nombre de périodes d'enseignement 
% périodes libres (identifiées 0) sont égales à périodes totales - périodes occupées (demande_par_spécialiste)
%constraint forall(sp in Specialistes) (PERIODES_CYCLE - Demande_Par_Specialiste[sp] = count([HorairesSpecialistes[sp, jc, pj] | jc in Jours_Cycle, pj in Periodes_Jour], 0));


% l'horaire de chaque spécialiste doit contenir exactement le bon nombre de visites de chaque groupe
% un groupe est identifiable par la formule suivante: niveau*max_groupes - max_groupes + mg(groupe actuel)
constraint forall(nv in Niveaux, mg in Max_Groupes, sp in Specialistes) (
      DEMANDE[nv, mg, sp] = count([HorairesSpecialistes[sp, jc, pj] | jc in Jours_Cycle, pj in Periodes_Jour], (nv*MAX_GROUPES - MAX_GROUPES + mg)));

% un tuteur doit n’avoir qu’UNE seule journée pleine (5 périodes), donc 9 jours de 4 périodes.
% la contrainte stipule qu'un numéro de groupe ne doit apparaître qu'une fois max par jour dans tous les horaires de spécialistes
constraint forall(jc in Jours_Cycle, gr in Groupes) (
      count([HorairesSpecialistes[sp, jc, pj] | pj in Periodes_Jour, sp in Specialistes], gr) <= 1 /\ count([HorairesSpecialistes[sp, jc, pj] | pj in Periodes_Jour, sp in Specialistes], gr) >= bool2int(DISPOS_TUTEURS[gr, jc] == 0));

%forall(pj in Periodes_Jour) (
%      count([HorairesSpecialistes[sp, jc, pj] | sp in Specialistes], gr) <= (DISPOS_TUTEURS[gr, pj])));
% ceil((50-41)/jours_cycle(10))

% un tuteur doit avoir une bonne répartition des périodes libres (tout le monde préfère P5 libre, mais on les répartit)
% la contrainte stipule qu'on ne doit pas avoir plus de 3 fois la même période libre...
% La borne inférieure à 1 fonctionne juste si la demande du groupe >= au nombre de périodes... (1*5)
constraint forall(pj in Periodes_Jour, gr in Groupes) (
      count([HorairesSpecialistes[sp, jc, pj] | jc in Jours_Cycle, sp in Specialistes], gr) <= 3 /\
      count([HorairesSpecialistes[sp, jc, pj] | jc in Jours_Cycle, sp in Specialistes], gr) >= 1 * bool2int(Demande_Par_Groupe[gr] >= PERIODES_JOUR));

%constraint forall(gr in Groupes) (
 %     count([HorairesSpecialistes[sp, jc, 5] | jc in Jours_Cycle, sp in Specialistes], gr) <= 3 /\ 
  %    count([HorairesSpecialistes[sp, jc, 1] | jc in Jours_Cycle, sp in Specialistes], gr) <= 3);


% EN CHANTIER pour une meilleure fonction de calcul de la distance
% tentative de mettre un coût sur la mauvaise dispersion des périodes
% les périodes de spécialité doivent être bien réparties dans le cycle. Par exemple, pour une spécialité à deux périodes, on souhaite une distance idéale de 5 jours (jours 1 et 6, 2 et 7, etc.) en plus d’avoir une période le matin et l’autre en après-midi.
% ex: punir lorsque 2 périodes de musique pour un groupe sont toutes deux à la fin de la journée (5e période)
%array [1..SPECIALITES_PAR_GROUPE] of var int: moyennes;
%constraint forall(spg in Specialites_par_groupe) (moyennes[spg] = round((((spg*(spg+1))/2)-spg)*(100*JOURS_CYCLE/(spg*spg))));
%array[1..MAX_GROUPES*NIVEAUX, 1..SPECIALISTES] of var 0..2*9: couts_par_specialiste_par_groupe;
%constraint forall(gr in Groupes, sp in Specialistes) (
%        (couts_par_specialiste_par_groupe[gr, sp] = abs(sum(jc in Jours_Cycle, pj in Periodes_Jour)(
%            if (HorairesSpecialistes[sp, jc, pj] == gr /\ (pj > 0)) then (if pj == 3 then 1 else 3-pj endif) else 0 endif))));


% on ne veut pas qu'un groupe ait 2 périodes identiques de la journée pour une même spécialité (ex: 2 musique à la première période)
% peut-être trop stricte comme contrainte (ex: anglais intensif avec plus de périodes d'anglais que de périodes dans une jounée)
% cette contrainte là rallentit beaucoup trop...
%constraint forall(sp in Specialistes, pj in Periodes_Jour, gr in Groupes) (count([HorairesSpecialistes[sp, jc, pj] | jc in Jours_Cycle], gr) <= 3);



array[1..SPECIALISTES, 2..(PERIODES_JOUR - 1)] of var 0..50: couts_par_specialiste_par_jour;
%array[1..SPECIALISTES, 1..PERIODES_JOUR] of var 0..50: couts_par_specialiste_par_jour;

% cette version ne fait que calculer combien de fois un spécialiste a le groupe X à P_i et punit les répétitions de période (exponentiel)
%constraint forall(sp in Specialistes, pj in Periodes_Jour) (
%        couts_par_specialiste_par_jour[sp, pj] = sum(gr in Groupes) (count([HorairesSpecialistes[sp, jc, pj] | jc in Jours_Cycle], gr)^2-%count([HorairesSpecialistes[sp, jc, pj] | jc in Jours_Cycle], gr)));

%constraint forall(sp in Specialistes, jc in Jours_Cycle) (
%constraint forall(sp in 1..2, jc in Jours_Cycle) (
%        if HorairesSpecialistes[sp, jc, 1] != 0 /\ HorairesSpecialistes[sp, jc, 2] != 0 then ((HorairesSpecialistes[sp, jc, 1] + (MAX_GROUPES -1)) div MAX_GROUPES) == ((HorairesSpecialistes[sp, jc, 2] + (MAX_GROUPES -1)) div MAX_GROUPES) else true endif);

% TRÈS IMPORTANT
% les spécialistes préfèrent regrouper les groupes de même niveau (ex: voir les 2 groupes de 3e année un à la suite de l'autre)        

% version qui alloue 0 pénalité quand une classe est suivie ou précédée d'une période libre
%PROBLÈME: l'optimiseur tente d'éviter les pénalités en alternant classe et période libre au lieu de grouper les niveaux identiques
%constraint forall(sp in Specialistes, pj in 1..(PERIODES_JOUR-1)) (
 %       if pj < 5 then couts_par_specialiste_par_jour[sp, pj] = sum(jc in Jours_Cycle) (min(HorairesSpecialistes[sp, jc, pj] * HorairesSpecialistes[sp, jc, (pj+1)] + 11, 12 * bool2int((HorairesSpecialistes[sp, jc, pj] + (MAX_GROUPES - 1)) div MAX_GROUPES - (HorairesSpecialistes[sp, jc, pj+1] + (MAX_GROUPES - 1)) div MAX_GROUPES != 0))) else true endif);

%constraint forall(sp in Specialistes, pj in 1..(PERIODES_JOUR-1)) (
 %       if pj < 5 then couts_par_specialiste_par_jour[sp, pj] = sum(jc in Jours_Cycle) ((bool2int(HorairesSpecialistes[sp, jc, pj] == 0 /\ HorairesSpecialistes[sp, jc, (pj+1)] == 0)) + bool2int((HorairesSpecialistes[sp, jc, pj] + (MAX_GROUPES - 1)) div MAX_GROUPES - (HorairesSpecialistes[sp, jc, pj+1] + (MAX_GROUPES - 1)) div MAX_GROUPES != 0)) else true endif);

constraint forall(sp in Specialistes, pj in 2..(PERIODES_JOUR - 1)) (
        couts_par_specialiste_par_jour[sp, pj] = min(bool2int(pj == 4) * 10 + bool2int(pj < 4) * sum(jc in Jours_Cycle) ((bool2int(HorairesSpecialistes[sp, jc, pj] == 0 /\ HorairesSpecialistes[sp, jc, (pj - 1)] == 0)) + bool2int((HorairesSpecialistes[sp, jc, pj] + (MAX_GROUPES - 1)) div MAX_GROUPES - (HorairesSpecialistes[sp, jc, pj - 1] + (MAX_GROUPES - 1)) div MAX_GROUPES != 0)), bool2int(pj == 2) * 10 + bool2int(pj > 2) * sum(jc in Jours_Cycle) ((bool2int(HorairesSpecialistes[sp, jc, pj] == 0 /\ HorairesSpecialistes[sp, jc, (pj + 1)] == 0)) + bool2int((HorairesSpecialistes[sp, jc, pj] + (MAX_GROUPES - 1)) div MAX_GROUPES - (HorairesSpecialistes[sp, jc, pj + 1] + (MAX_GROUPES - 1)) div MAX_GROUPES != 0))));

%constraint forall(sp in Specialistes, pj in 1..(PERIODES_JOUR-1)) (
 %       if pj < 5 then couts_par_specialiste_par_jour[sp, pj] = sum(jc in Jours_Cycle) (2*bool2int((HorairesSpecialistes[sp, jc, pj] + (MAX_GROUPES - 1)) div MAX_GROUPES - (HorairesSpecialistes[sp, jc, pj+1] + (MAX_GROUPES - 1)) div MAX_GROUPES != 0)) else true endif);


output["\n" ++ show(couts_par_specialiste_par_jour)];
var int: couts = sum(couts_par_specialiste_par_jour);
%output["\n" ++ show(couts_par_specialiste_par_groupe)];
%var int: couts = sum(couts_par_specialiste_par_groupe);
%var int: couts = sum(couts_par_specialiste_par_groupe) + sum(couts_par_specialiste_par_jour);


% un contractuel qui comble une tâche de tuteur ne doit PAS hériter de la journée pleine.    
% en terme de contraintes d'horaires de spécialistes, si un contractuel est présent à certaines journées du cycle, ces journées doivent avoir exactement UNE spécialité à l'horaire. Pour les tuteurs, une école va indiquer au départ quel(s) jour(s) le contractuel va venir combler la tâche autant pour les tuteurs que les spécialistes. Une réduction de tâche pour un spécialiste signifie qu'un contractuel donnera les cours de spécialité à certains jours fixes. Un contractuel n’est disponible que lors de jours fixes (ex: seulement les jours 1 et 6)
% ... à faire... et créer disponibilités pour chaque tuteur




% un spécialiste peut se déplacer d'un pavillon à l'autre (faisant partie de la même école) ou d’une école à l’autre lors d'une journée (tâche combinée dans plusieurs écoles), mais on veut minimiser ces déplacements et/ou les prévoir lors du dîner.
% exemple de Frank, soit sur le dîner, soit avoir une période libre pour le déplacement

% pour des raisons sonores, un local polyvalent de spécialité peut être non disponible pour la musique si son local adjacent est occupé lors de certaines plages horaires.
% on devrait laisser tomber...


%solve :: restart_geometric(1.5, 100) minimize couts;

%solve minimize couts;
%solve satisfy;
solve :: seq_search([int_search(couts_par_specialiste_par_jour, first_fail, indomain_split)]) minimize couts;

output["\nDemande par spécialiste:" ++ show(Demande_Par_Specialiste)];
%output["\n Dispos par spécialiste:" ++ show(Dispos_Par_Specialiste)];
%output["\nMoyenne pour " ++ show(spg) ++ " périodes:" ++ show_int(2, moyennes[spg]) | spg in Specialites_par_groupe];
output["\nMATRICE CONSTRUITE POUR ", show(MAX_GROUPES * NIVEAUX), " GROUPES:"];
output["\nDemande par groupe:" ++ show(Demande_Par_Groupe) ++ "\n"];
output[show_int(2, HorairesSpecialistes[sp, jc, pj]) ++ if jc == max(Jours_Cycle) then "\n" else " " endif ++ if jc == max(Jours_Cycle) /\ pj == max(Periodes_Jour) then "\n" else "" endif | sp in Specialistes, pj in Periodes_Jour, jc in Jours_Cycle];
%output[show(ceil(2.5)) ++ " " ++ show(floor(2.5)) ++ " " ++ show(round(2.49))];
output["\nCoût:" ++ show(couts)];
