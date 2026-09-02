import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    """Le modèle d'utilisateur, avant toute autre migration — point
    d'irréversibilité du socle (PROMPT_00, étape 5). AUTH_USER_MODEL ne se
    substitue plus une fois cette migration appliquée.
    """

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        # Ordre explicite, pas laissé au hasard du graphe de migrations :
        # btree_gist doit être posée avant la première table du socle.
        ("noyau", "0001_extensions"),
    ]

    operations = [
        migrations.CreateModel(
            name="Utilisateur",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="last login"),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Designates that this user has all permissions without "
                            "explicitly assigning them."
                        ),
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text=(
                            "Required. 150 characters or fewer. Letters, digits and "
                            "@/./+/-/_ only."
                        ),
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(blank=True, max_length=150, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(blank=True, max_length=150, verbose_name="last name"),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, verbose_name="email address"),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "Designates whether this user should be treated as active. "
                            "Unselect this instead of deleting accounts."
                        ),
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("grade", models.CharField(max_length=50, verbose_name="grade")),
                (
                    "profil",
                    models.CharField(
                        choices=[
                            ("administrateur", "Administrateur"),
                            ("cellule_pedagogique", "Cellule pédagogique"),
                            ("cellule_planification", "Cellule planification"),
                            ("cellule_examens", "Cellule examens"),
                            ("direction_formation", "Direction de formation"),
                        ],
                        max_length=30,
                        verbose_name="profil",
                    ),
                ),
                (
                    "echecs_consecutifs",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="échecs consécutifs"
                    ),
                ),
                (
                    "verrouille_jusqu_a",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="verrouillé jusqu'à"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text=(
                            "The groups this user belongs to. A user will get all "
                            "permissions granted to each of their groups."
                        ),
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "utilisateur",
                "verbose_name_plural": "utilisateurs",
                "db_table": "administration_utilisateur",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddConstraint(
            model_name="utilisateur",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    (
                        "profil__in",
                        [
                            "administrateur",
                            "cellule_pedagogique",
                            "cellule_planification",
                            "cellule_examens",
                            "direction_formation",
                        ],
                    )
                ),
                name="ck_utilisateur_profil",
            ),
        ),
    ]
