from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_user_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add role column with default 'student'
    op.add_column('users', sa.Column('role', sa.String(length=50), nullable=False, server_default='student'))
    # Add is_active column
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')))
    # Add last_login column
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    # Ensure email unique constraint exists
    try:
        op.create_unique_constraint('uq_users_email', 'users', ['email'])
    except Exception:
        # constraint may already exist depending on DB state
        pass


def downgrade():
    try:
        op.drop_constraint('uq_users_email', 'users', type_='unique')
    except Exception:
        pass
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'role')
