"""fix_atch_file_id_column_length

Revision ID: 97f9a3852183
Revises: a28f1893deb8
Create Date: 2025-09-08 10:11:54.745051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97f9a3852183'
down_revision: Union[str, None] = 'a28f1893deb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # tb_file 테이블의 atch_file_id 컬럼 크기를 20에서 36으로 변경 (UUID 지원)
    op.alter_column('tb_file', 'atch_file_id',
                   existing_type=sa.String(length=20),
                   type_=sa.String(length=36),
                   existing_nullable=False,
                   schema='skybootcore')
    
    # tb_filedetail 테이블의 atch_file_id 컬럼도 동일하게 변경
    op.alter_column('tb_filedetail', 'atch_file_id',
                   existing_type=sa.String(length=20),
                   type_=sa.String(length=36),
                   existing_nullable=False,
                   schema='skybootcore')


def downgrade() -> None:
    # 롤백 시 원래 크기로 복원
    op.alter_column('tb_filedetail', 'atch_file_id',
                   existing_type=sa.String(length=36),
                   type_=sa.String(length=20),
                   existing_nullable=False,
                   schema='skybootcore')
    
    op.alter_column('tb_file', 'atch_file_id',
                   existing_type=sa.String(length=36),
                   type_=sa.String(length=20),
                   existing_nullable=False,
                   schema='skybootcore')
