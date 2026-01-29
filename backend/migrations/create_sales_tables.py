import asyncio
from backend.core.database import digital_customer_sync_engine, Base
from backend.models.db_models import (
    SalesKnowledge,
    TrainingSession,
    ConversationRound,
    StageEvaluation,
    FinalEvaluation
)
from loguru import logger

def create_tables():
    logger.info("Creating sales training tables in digital_customer.db...")
    Base.metadata.create_all(
        bind=digital_customer_sync_engine,
        tables=[
            SalesKnowledge.__table__,
            TrainingSession.__table__,
            ConversationRound.__table__,
            StageEvaluation.__table__,
            FinalEvaluation.__table__
        ]
    )
    logger.info("Tables created successfully!")

if __name__ == "__main__":
    create_tables()