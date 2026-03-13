"""add agent runs table

Revision ID: 8c1f9c2b7d11
Revises: 2b968a8ff528
Create Date: 2026-03-13 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8c1f9c2b7d11"
down_revision: Union[str, None] = "2b968a8ff528"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_runs",
        sa.Column("agent_id", sa.String(length=120), nullable=False, comment="Agent 식별자"),
        sa.Column("status", sa.String(length=20), nullable=False, comment="실행 상태"),
        sa.Column("input_text", sa.Text(), nullable=False, comment="입력 프롬프트/요청"),
        sa.Column("output_text", sa.Text(), nullable=True, comment="Agent 응답 결과"),
        sa.Column("error_message", sa.Text(), nullable=True, comment="실패 시 에러 메시지"),
        sa.Column("external_run_id", sa.String(length=255), nullable=True, comment="외부 플랫폼 실행 ID"),
        sa.Column("model_name", sa.String(length=120), nullable=True, comment="요청 모델명"),
        sa.Column("metadata_json", sa.Text(), nullable=True, comment="추가 메타데이터(JSON 문자열)"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True, comment="실행 시작 시각"),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True, comment="실행 종료 시각"),
        sa.Column("owner_id", sa.UUID(), nullable=False, comment="요청 사용자 ID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="생성일시"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="수정일시"),
        sa.Column("id", sa.UUID(), nullable=False, comment="PK (UUID)"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_runs_agent_id"), "agent_runs", ["agent_id"], unique=False)
    op.create_index(op.f("ix_agent_runs_owner_id"), "agent_runs", ["owner_id"], unique=False)
    op.create_index(op.f("ix_agent_runs_status"), "agent_runs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_runs_status"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_owner_id"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_agent_id"), table_name="agent_runs")
    op.drop_table("agent_runs")

