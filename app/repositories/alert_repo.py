from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.schemas.alert import AlertCreate


class AlertRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_alerts(self, user_id: str) -> Sequence[Alert]:
        stmt = select(Alert).where(Alert.user_id == user_id).order_by(Alert.received_at.desc())
        result = await self.session.scalars(stmt)
        return result.all()

    async def create_alert(self, user_id: str, alert_in: AlertCreate) -> Alert:
        alert = Alert(
            user_id=user_id,
            title=alert_in.title,
            message=alert_in.message,
            source_app=alert_in.source_app,
            device_name=alert_in.device_name,
        )
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert
