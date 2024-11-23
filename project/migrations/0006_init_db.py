from django.db import migrations, connection

def execute_sql(apps, schema_editor):
    # Open SQL script
    with open('dbinit.sql', 'r', encoding='utf-8') as file:
        commands = file.read()
    # Execute SQL commands
    sql_statements = commands.split(';')

    # Execute each statement individually
    with connection.cursor() as cursor:
        for statement in sql_statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(e)

class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_create_users'),
    ]

    operations = [
        migrations.RunPython(execute_sql),
    ]
