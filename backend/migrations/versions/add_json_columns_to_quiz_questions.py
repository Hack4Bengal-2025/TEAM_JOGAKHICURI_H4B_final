"""add json columns to quiz questions

Revision ID: add_json_columns_to_quiz_questions
Revises: 
Create Date: 2024-04-20 09:10:04.047310

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'add_json_columns_to_quiz_questions'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing columns if they exist
    op.drop_column('quiz_questions', 'options')
    op.drop_column('quiz_questions', 'answer')

    # Add new JSON columns with proper defaults
    op.add_column('quiz_questions',
                  sa.Column('options', postgresql.JSON(
                      astext_type=sa.Text()), nullable=False, server_default='[]')
                  )
    op.add_column('quiz_questions',
                  sa.Column('answer', postgresql.JSON(
                      astext_type=sa.Text()), nullable=False, server_default='""')
                  )


def downgrade():
    op.drop_column('quiz_questions', 'options')
    op.drop_column('quiz_questions', 'answer')
