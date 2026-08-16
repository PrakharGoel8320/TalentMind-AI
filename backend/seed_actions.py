import asyncio
import uuid
from app.database.session import engine, AsyncSessionLocal
from app.models.action import ActionProposal
from app.models.enums import ActionStatus, ActionType

async def seed():
    async with AsyncSessionLocal() as session:
        # A pending action
        p1 = ActionProposal(
            id=uuid.uuid4(),
            action_type=ActionType.EMAIL_CANDIDATE,
            target_id="cand_test_1",
            status=ActionStatus.PENDING_APPROVAL,
            reason="Good fit for the role",
            payload={"recipient": "test1@example.com", "subject": "Interview", "body": "You are invited."}
        )
        
        # An approved action
        p2 = ActionProposal(
            id=uuid.uuid4(),
            action_type=ActionType.EMAIL_CANDIDATE,
            target_id="cand_test_2",
            status=ActionStatus.APPROVED,
            reason="Excellent background",
            payload={"recipient": "test2@example.com", "subject": "Offer", "body": "Here is your offer."}
        )
        
        session.add(p1)
        session.add(p2)
        await session.commit()
        print("Seeded actions!")

if __name__ == "__main__":
    asyncio.run(seed())
