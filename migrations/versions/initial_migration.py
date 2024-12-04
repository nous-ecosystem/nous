"""initial

Revision ID: initial_migration
Revises:
Create Date: 2024-12-04 02:20:45.700211

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = "initial_migration"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create all your initial tables
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("discord_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("discord_id"),
    )

    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("target_type", sa.String(length=10), nullable=False),
        sa.Column("target_id", sa.BigInteger(), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "permission_type",
            sa.Enum("ALLOW", "DENY", name="permissiontype"),
            nullable=True,
        ),
        sa.Column("can_use_bot", sa.Boolean(), nullable=True),
        sa.Column("can_manage_permissions", sa.Boolean(), nullable=True),
        sa.Column("can_use_admin_commands", sa.Boolean(), nullable=True),
        sa.Column("max_requests_per_day", sa.Integer(), nullable=True),
        sa.Column("view_channel", sa.Boolean(), nullable=True),
        sa.Column("manage_channels", sa.Boolean(), nullable=True),
        sa.Column("manage_roles", sa.Boolean(), nullable=True),
        sa.Column("manage_messages", sa.Boolean(), nullable=True),
        sa.Column("send_messages", sa.Boolean(), nullable=True),
        sa.Column("send_messages_in_threads", sa.Boolean(), nullable=True),
        sa.Column("create_public_threads", sa.Boolean(), nullable=True),
        sa.Column("create_private_threads", sa.Boolean(), nullable=True),
        sa.Column("attach_files", sa.Boolean(), nullable=True),
        sa.Column("add_reactions", sa.Boolean(), nullable=True),
        sa.Column("use_external_emojis", sa.Boolean(), nullable=True),
        sa.Column("use_external_stickers", sa.Boolean(), nullable=True),
        sa.Column("mention_everyone", sa.Boolean(), nullable=True),
        sa.Column("manage_webhooks", sa.Boolean(), nullable=True),
        sa.Column("moderate_members", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "command_hashes",
        sa.Column("guild_id", sa.String(), nullable=False),
        sa.Column("command_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("guild_id"),
    )


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table("command_hashes")
    op.drop_table("permissions")
    op.drop_table("users")
