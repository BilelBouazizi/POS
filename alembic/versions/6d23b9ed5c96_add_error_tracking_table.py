"""Add error tracking table

Revision ID: 6d23b9ed5c96
Revises: e46003b3a8a7
Create Date: 2025-02-04 12:29:26.064929

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d23b9ed5c96'
down_revision: Union[str, None] = 'e46003b3a8a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
