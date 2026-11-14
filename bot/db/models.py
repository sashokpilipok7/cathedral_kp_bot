from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class TelegramUser(Base):
    """Model for storing Telegram bot users in WordPress database (wp_telegram_users)."""

    __tablename__ = "wp_telegram_users"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id = Column(BigIntPK, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(16), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    reminders = relationship(
        "TelegramSendReminder",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<TelegramUser(id={self.id}, telegram_id={self.telegram_id}, "
            f"username={self.username!r}, is_active={self.is_active})>"
        )


class TelegramSendReminder(Base):
    """Model for storing sent/scheduled event reminders in WordPress database (wp_telegram_send_reminders)."""

    __tablename__ = "wp_telegram_send_reminders"
    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "telegram_id",
            "reminder_type",
            name="uq_event_user_reminder_type",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(BigIntPK, primary_key=True, autoincrement=True)
    event_id = Column(BigInteger, nullable=False, index=True)
    telegram_id = Column(
        BigInteger,
        ForeignKey("wp_telegram_users.telegram_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    reminder_type = Column(String(50), default="default", nullable=False)
    status = Column(String(50), default="sent", nullable=False)
    sent_at = Column(
        DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False
    )

    user = relationship("TelegramUser", back_populates="reminders")

    def __repr__(self):
        return (
            f"<TelegramSendReminder(id={self.id}, event_id={self.event_id}, "
            f"telegram_id={self.telegram_id}, reminder_type={self.reminder_type!r}, "
            f"status={self.status!r})>"
        )


# Table-name and alternative aliases for convenience
wp_telegram_users = TelegramUser
wp_telegram_send_reminders = TelegramSendReminder
wp_telegram_sent_reminders = TelegramSendReminder
TelegramSentReminder = TelegramSendReminder
