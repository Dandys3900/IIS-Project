import os
from django.db import migrations

# Function for executing initial SQL script
def executeSQLscript(apps, schema_editor):
    # Try to open script file
    with open(os.path.join("dbinit.sql"), "r", encoding="utf-8") as file:
        print(file)
        script = file.read()
    try:
        # Execute script
        schema_editor.execute(script)
    except Exception as err:
        print(f"Error while executing script, error: {err}")

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(executeSQLscript)
    ]
