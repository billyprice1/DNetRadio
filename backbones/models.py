import peewee
import peewee_async
from backbones.config import config
# Imports go here.

database = peewee_async.PostgresqlDatabase(
    database=config['postgres_config']['database'],
    user=config['postgres_config']['username'],
    host=config['postgres_config']['hostname'],
    port=config['postgres_config']['port'],
    password=config['postgres_config']['password']
)
# The Postgres database.

objects = peewee_async.Manager(database)
# The Peewee async manager.


class BaseModel(peewee.Model):
    class Meta:
        database = database
# the base model.


class Guild(BaseModel):
    guild_id = peewee.BigIntegerField(primary_key=True)
    voice_channel = peewee.BigIntegerField(null=True)
    enabled = peewee.BooleanField(default=True)
# Defines the guild database object.


def create_tables():
    if not Guild.table_exists():
        Guild.create_table(True)
# Creates any tables needed.
