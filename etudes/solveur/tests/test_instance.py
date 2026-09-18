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
