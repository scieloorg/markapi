from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("markup_doc", "0004_articledocxmarkup_xref_status"),
        ("markup_doc", "0003_remove_articledocxmarkup_dateiso_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="articledocxmarkup",
            name="collection",
        ),
        migrations.DeleteModel(
            name="CollectionModel",
        ),
        migrations.DeleteModel(
            name="CollectionValuesModel",
        ),
    ]
