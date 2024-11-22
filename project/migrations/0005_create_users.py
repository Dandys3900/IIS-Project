from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_initial_users(apps, _):
    # Get user model
    CustomUser = apps.get_model("project", "CustomUser")  # Adjust if needed
    # Add user"s data
    users_data = [
        {"first_name": "Jan", "last_name": "Novák", "username": "jnovak", "password": "Heslo123", "email": "jan.novak@email.cz", "phone_number": "+420123456789", "userrole": "volunteer", "verified": False},
        {"first_name": "Milan", "last_name": "Vrbas", "username": "Milisaurus", "password": "C!master7", "email": "milan.vrbas1@gmail.com", "phone_number": "+420731672979", "userrole": "vet", "verified": False},
        {"first_name": "Petr", "last_name": "Svoboda", "username": "psvoboda", "password": "Petr*Heslo", "email": "petr.svoboda@email.com", "phone_number": "+420987654321", "userrole": "carer", "verified": False},
        {"first_name": "Tomáš", "last_name": "Daniel", "username": "xDandys", "password": "Gym_Monster", "email": "tomas.daniel@centrum.cz", "phone_number": "+420731572983", "userrole": "admin", "verified": False},
        {"first_name": "Janšta", "last_name": "Jakub", "username": "Kubalabambula", "password": "Godot#Master", "email": "jakub.jansta@gmail.com", "phone_number": "+420732315134", "userrole": "admin", "verified": False},
        {"first_name": "Eva", "last_name": "Kralová", "username": "ekralova", "password": "Kralova@", "email": "eva.kralova@gmail.com", "phone_number": "+420555555555", "userrole": "volunteer", "verified": False},
        {"first_name": "Marie", "last_name": "Novotná", "username": "mnovotna", "password": "MarieHeslo420", "email": "marie.novotna@seznam.cz", "phone_number": "+420624421413", "userrole": "carer", "verified": False}
    ]

    for user_data in users_data:
        user_data["password"] = make_password(user_data["password"])
        CustomUser.objects.create(**user_data)

class Migration(migrations.Migration):

    dependencies = [
        ("project", "0004_animaltask"),
    ]

    operations = [
        migrations.RunPython(create_initial_users),
    ]