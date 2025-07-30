from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    BigInteger, 
    ForeignKey,
    text,
    Integer,
    Enum,
)
from database.model_base import Base
from bot.club_infrastructure.types import (
    InfrastructureLevel,
    InfrastructureType,
    InfrastructureTyping
)

from database.model_base import Base

class ClubInfrastructure(Base):
    __tablename__ = 'club_infrastructures'
    
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True
    )

    club_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('clubs.id'), nullable=False
    )
    points: Mapped[int] = mapped_column(
        Integer, nullable=False, default = 0, server_default=text('0')
    )

    last_update_points: Mapped[datetime] = mapped_column(
        default = datetime(1970, 1, 1), server_default=text('TIMESTAMP \'1970-01-01 00:00:00\'')
    )

    training_base: Mapped[InfrastructureLevel] = mapped_column(
        Enum(InfrastructureLevel), default=InfrastructureLevel.LEVEL_0,
        server_default = text("'LEVEL_0'")
    )
    training_center: Mapped[InfrastructureLevel] = mapped_column(
        Enum(InfrastructureLevel), default=InfrastructureLevel.LEVEL_0,
        server_default = text("'LEVEL_0'")
    )
    premium_fond: Mapped[InfrastructureLevel] = mapped_column(
        Enum(InfrastructureLevel), default=InfrastructureLevel.LEVEL_0,
        server_default = text("'LEVEL_0'")
    )
    stadium: Mapped[InfrastructureLevel] = mapped_column(
        Enum(InfrastructureLevel), default=InfrastructureLevel.LEVEL_0,
        server_default = text("'LEVEL_0'")
    )
    sports_medicine: Mapped[InfrastructureLevel] = mapped_column(
        Enum(InfrastructureLevel), default=InfrastructureLevel.LEVEL_0,
        server_default = text("'LEVEL_0'")
    )
    academy_talent: Mapped[InfrastructureLevel] = mapped_column(
        Enum(InfrastructureLevel), default=InfrastructureLevel.LEVEL_0,
        server_default = text("'LEVEL_0'")
    )
    
    
    def get_infrastructure_level(self, infrastructure_type: InfrastructureType) -> InfrastructureLevel:
        name_infrastructure = InfrastructureTyping.get_name(infrastructure_type)
        return getattr(self, name_infrastructure)