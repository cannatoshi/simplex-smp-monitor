# Generated migration for new Test model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0003_server_control_port_and_more'),
        ('stresstests', '0001_initial'),
    ]

    operations = [
        # Altes TestRun Model umbenennen (Backup)
        migrations.RenameModel(
            old_name='TestRun',
            new_name='TestRunOld',
        ),
        
        # Neues Test Model erstellen
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('test_type', models.CharField(choices=[('monitoring', 'Server Monitoring'), ('stress', 'Stress Test'), ('latency', 'Latency Check')], default='monitoring', max_length=20)),
                ('status', models.CharField(choices=[('inactive', 'Inaktiv'), ('active', 'Aktiv'), ('running', 'Läuft'), ('paused', 'Pausiert'), ('completed', 'Abgeschlossen'), ('failed', 'Fehlgeschlagen')], default='inactive', max_length=20)),
                ('test_all_active_servers', models.BooleanField(default=False, help_text='Alle aktiven Server testen')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('last_run', models.DateTimeField(blank=True, null=True)),
                ('total_runs', models.PositiveIntegerField(default=0)),
                ('successful_runs', models.PositiveIntegerField(default=0)),
                ('failed_runs', models.PositiveIntegerField(default=0)),
                ('interval_minutes', models.PositiveIntegerField(default=5, help_text='Check-Intervall in Minuten')),
                ('num_clients', models.PositiveIntegerField(default=2)),
                ('duration_seconds', models.PositiveIntegerField(default=60)),
                ('message_interval_seconds', models.PositiveIntegerField(default=5)),
                ('messages_sent', models.PositiveIntegerField(default=0)),
                ('messages_received', models.PositiveIntegerField(default=0)),
                ('avg_latency_ms', models.FloatField(blank=True, null=True)),
                ('min_latency_ms', models.FloatField(blank=True, null=True)),
                ('max_latency_ms', models.FloatField(blank=True, null=True)),
                ('write_to_influxdb', models.BooleanField(default=True, help_text='Metriken nach InfluxDB schreiben')),
                ('influxdb_measurement', models.CharField(default='server_monitoring', max_length=100)),
                ('servers', models.ManyToManyField(blank=True, related_name='tests', to='servers.server')),
            ],
            options={
                'verbose_name': 'Test',
                'verbose_name_plural': 'Tests',
                'ordering': ['-created_at'],
            },
        ),
        
        # TestResult Model
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('success', models.BooleanField(default=False)),
                ('latency_ms', models.IntegerField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('used_tor', models.BooleanField(default=False)),
                ('tls_version', models.CharField(blank=True, max_length=20)),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_results', to='servers.server')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='stresstests.test')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='testresult',
            index=models.Index(fields=['test', '-timestamp'], name='stresstests_test_id_7a1234_idx'),
        ),
        migrations.AddIndex(
            model_name='testresult',
            index=models.Index(fields=['server', '-timestamp'], name='stresstests_server__abc123_idx'),
        ),
        
        # Metric Model aktualisieren (FK zu neuem Test Model)
        migrations.AlterField(
            model_name='metric',
            name='test_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='stresstests.test'),
        ),
        migrations.RenameField(
            model_name='metric',
            old_name='test_run',
            new_name='test',
        ),
        migrations.AddField(
            model_name='metric',
            name='server_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='metric',
            name='details',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
