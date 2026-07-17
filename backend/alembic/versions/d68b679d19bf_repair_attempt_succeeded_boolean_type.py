"""repair attempt succeeded boolean type

Revision ID: d68b679d19bf
Revises: 6be3755c2da8
Create Date: 2026-07-17 16:31:19.608317

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd68b679d19bf'
down_revision: Union[str, Sequence[str], None] = '6be3755c2da8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    columns = sa.inspect(connection).get_columns("delivery_attempts")
    succeeded_column = next(
        column for column in columns if column["name"] == "succeeded"
    )

    if isinstance(succeeded_column["type"], sa.Integer):
        op.execute(
            """
            ALTER TABLE delivery_attempts
            ALTER COLUMN succeeded TYPE BOOLEAN
            USING CASE
                WHEN succeeded = 1 THEN TRUE
                ELSE FALSE
            END
            """
        )


def downgrade() -> None:
    connection = op.get_bind()

    columns = sa.inspect(connection).get_columns("delivery_attempts")
    succeeded_column = next(
        column for column in columns if column["name"] == "succeeded"
    )

    if isinstance(succeeded_column["type"], sa.Boolean):
        op.execute(
            """
            ALTER TABLE delivery_attempts
            ALTER COLUMN succeeded TYPE INTEGER
            USING CASE
                WHEN succeeded THEN 1
                ELSE 0
            END
            """
        )