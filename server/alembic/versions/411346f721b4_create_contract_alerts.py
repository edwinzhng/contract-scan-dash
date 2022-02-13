"""Create contract alerts

Revision ID: 411346f721b4
Revises: 72ed3f54a6ca
Create Date: 2022-02-13 02:12:10.026180

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "411346f721b4"
down_revision = "72ed3f54a6ca"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "contract_alerts",
        sa.Column("alert_id", postgresql.BIGINT(), nullable=False),
        sa.Column("keyword", sa.String(), nullable=False, unique=True),
        sa.Column("chat_ids", postgresql.ARRAY(postgresql.BIGINT()), nullable=False),
        sa.PrimaryKeyConstraint("alert_id"),
    )
    op.create_index(
        "ix_contract_alerts__chat_ids",
        "contract_alerts",
        ["chat_ids"],
        unique=False,
        postgresql_using="gin",
    )
    op.create_index(
        op.f("ix_contract_alerts_keyword"), "contract_alerts", ["keyword"], unique=True
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_contract_alerts_keyword"), table_name="contract_alerts")
    op.drop_index(
        "ix_contract_alerts__chat_ids",
        table_name="contract_alerts",
        postgresql_using="gin",
    )
    op.drop_table("contract_alerts")
    # ### end Alembic commands ###