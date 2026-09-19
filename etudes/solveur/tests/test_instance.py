from solveur.generateur import ParametresInstance, generer


def _parametres(**overrides):
    base = dict(
        taille="CONTROLE",
        demande_lieux_partages=0.15,
        densite_qualification=4,
        fraction_modules_rares=0.05,
        graine=1,
    )
    base.update(overrides)
    return ParametresInstance(**base)


def test_meme_graine_produit_la_meme_instance():
    a = generer(_parametres())
    b = generer(_parametres())
    assert a.vers_json() == b.vers_json()


def test_graines_differentes_produisent_des_instances_differentes():
    a = generer(_parametres(graine=1))
    b = generer(_parametres(graine=2))
    assert a.vers_json() != b.vers_json()


def test_taille_controle_respecte_les_effectifs_attendus():
    instance = generer(_parametres())
    assert len(instance.brigades) == 3
    assert len(instance.instructeurs) == 9
    assert len(instance.creneaux) == 20


def test_json_aller_retour_preserve_l_instance():
    from solveur.instance import depuis_json

    instance = generer(_parametres())
    relue = depuis_json(instance.vers_json())
    assert relue.vers_json() == instance.vers_json()


def test_fraction_modules_rares_a_exactement_un_instructeur_qualifie():
    instance = generer(_parametres(taille="REELLE", fraction_modules_rares=1.0, graine=3))
    qualifies_par_module = {}
    for instructeur in instance.instructeurs:
        for module_id in instructeur.modules_qualifies:
            qualifies_par_module.setdefault(module_id, []).append(instructeur.id)
    for module in instance.modules:
        assert len(qualifies_par_module.get(module.id, [])) == 1


def _instance_reelle(demande, graine=0):
    return generer(
        ParametresInstance(
            taille="REELLE",
            demande_lieux_partages=demande,
            densite_qualification=4,
            fraction_modules_rares=0.05,
            graine=graine,
        )
    )


def test_le_programme_cible_couvre_tous_les_creneaux_de_chaque_brigade():
    instance = _instance_reelle(0.15)
    for brigade in instance.brigades:
        assert sum(brigade.programme_cible.values()) == len(instance.creneaux)


def test_la_demande_en_lieux_s_applique_aux_seances_a_pourvoir():
    """Régression de la revue du 2026-09-18 : appliquée au catalogue, la
    demande effective n'atteignait que 3 à 11 % pour 10 à 25 % annoncés. Elle
    doit valoir EXACTEMENT round(demande × créneaux) séances par brigade."""
    for demande, attendu_par_brigade in ((0.10, 2), (0.15, 3), (0.20, 4), (0.25, 5)):
        instance = _instance_reelle(demande)
        par_id = {m.id: m for m in instance.modules}
        for brigade in instance.brigades:
            avec_lieu = sum(
                n for m, n in brigade.programme_cible.items() if par_id[m].necessite_lieu_partage
            )
            assert avec_lieu == attendu_par_brigade
        total = instance.meta["seances_a_pourvoir_avec_lieu"]
        assert total == attendu_par_brigade * len(instance.brigades)


def test_la_capacite_nominale_des_lieux_partages_vaut_espaces_fois_creneaux():
    """Un lieu SIMULTANÉ ne reçoit qu'UNE brigade non regroupée : la capacité
    se compte comme au § 2 du prompt, 7 espaces × 20 créneaux = 140."""
    instance = _instance_reelle(0.25)
    effectifs = [b.effectif for b in instance.brigades]
    for lieu in instance.lieux_partages:
        if lieu.mode == "SIMULTANE":
            assert lieu.capacite >= max(effectifs)
            assert lieu.capacite < 2 * min(effectifs)
    assert len(instance.lieux_partages) * len(instance.creneaux) == 140


def test_le_volume_prescrit_couvre_le_programme_cible():
    instance = _instance_reelle(0.25)
    total = {}
    for brigade in instance.brigades:
        for module_id, n in brigade.programme_cible.items():
            total[module_id] = total.get(module_id, 0) + n
    par_id = {m.id: m for m in instance.modules}
    for module_id, n in total.items():
        assert par_id[module_id].volume_prescrit >= n * 2.0


def test_les_prerequis_acquis_restent_acquis_apres_relevement_des_volumes():
    from solveur.preparation import modules_eligibles

    instance = _instance_reelle(0.25)
    par_id = {m.id: m for m in instance.modules}
    for brigade in instance.brigades:
        for module_id in brigade.programme_cible:
            module = par_id[module_id]
            assert module_id in modules_eligibles(instance)[brigade.id]
            if module.prerequis_id:
                assert brigade.volume_deja_programme[module.prerequis_id] >= (
                    par_id[module.prerequis_id].volume_prescrit
                )


def test_l_instance_ne_depend_pas_de_la_graine_de_hachage_du_processus():
    """Régression du 2026-09-19 : un `set` de chaînes itéré avec un tirage
    aléatoire par élément rendait l'instance différente d'un processus à
    l'autre — les trois régimes et l'heuristique d'une même ligne de la
    matrice étaient alors mesurés sur des instances différentes."""
    import os
    import subprocess
    import sys

    programme = (
        "import sys; sys.path.insert(0, '.');"
        "from solveur.generateur import ParametresInstance, generer;"
        "print(generer(ParametresInstance('REELLE', 0.25, 4, 0.05, 0)).empreinte())"
    )
    empreintes = set()
    for graine_hachage in ("0", "1", "2", "3"):
        env = {**os.environ, "PYTHONHASHSEED": graine_hachage}
        sortie = subprocess.run(
            [sys.executable, "-c", programme], capture_output=True, text=True, env=env, check=True
        )
        empreintes.add(sortie.stdout.strip())
    assert len(empreintes) == 1, empreintes
