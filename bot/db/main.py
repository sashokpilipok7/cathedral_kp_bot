import os
from contextlib import contextmanager
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from configuration import Config
from .models import Base, TelegramUser, TelegramSendReminder


def build_database_url(config_path="configuration.yaml") -> str:
    """
    Build the SQLAlchemy MySQL connection URL for the WordPress database.
    Format: mysql+pymysql://wp_user:wp_password@cam2021.mysql.ukraine.com.ua:3306/cam2021_cathedralkp
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    db_cfg = {}
    if os.path.exists(config_path):
        try:
            db_cfg = Config(config_path).get_db_config() or {}
        except Exception:
            db_cfg = {}

    host = os.getenv("DB_HOST", db_cfg.get("host", "cam2021.mysql.ukraine.com.ua"))
    port = os.getenv("DB_PORT", db_cfg.get("port", 3306))
    database = os.getenv("DB_NAME", db_cfg.get("database", "cam2021_cathedralkp"))
    user = os.getenv("DB_USER", db_cfg.get("user", "wp_user"))
    password = os.getenv("DB_PASSWORD", db_cfg.get("password", "wp_password"))

    encoded_user = quote_plus(str(user))
    encoded_password = quote_plus(str(password))

    return (
        f"mysql+pymysql://{encoded_user}:{encoded_password}"
        f"@{host}:{port}/{database}?charset=utf8mb4"
    )


DATABASE_URL = build_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    connect_args={"connect_timeout": 10, "read_timeout": 10, "write_timeout": 10}
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def init_db():
    """Create database tables (wp_telegram_users, wp_telegram_send_reminders) if they do not exist."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session():
    """Provide a transactional scope around a series of database operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class DBManager:
    """Database manager for WordPress MySQL Telegram bot tables."""

    def __init__(self, db_url: str = None):
        if db_url:
            self.engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
            )
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
        else:
            self.engine = engine
            self.SessionLocal = SessionLocal
        print("Session created")

    def init_db(self):
        """Create tables if they do not exist in the WordPress database."""
        Base.metadata.create_all(bind=self.engine)
        print("Table initiated")

    @contextmanager
    def session_scope(self):
        """Context manager for database session."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # --- User operations (wp_telegram_users) ---

    def upsert_user(
        self,
        telegram_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        language_code: str = None,
        is_active: bool = True,
    ) -> TelegramUser:
        """Create a new Telegram user or update an existing one."""
        with self.session_scope() as session:
            user = (
                session.query(TelegramUser)
                .filter(TelegramUser.telegram_id == telegram_id)
                .first()
            )
            if user:
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                if language_code is not None:
                    user.language_code = language_code
                user.is_active = is_active
            else:
                user = TelegramUser(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    language_code=language_code,
                    is_active=is_active,
                )
                session.add(user)
            session.flush()
            session.refresh(user)
            return user

    def get_user(self, telegram_id: int) -> TelegramUser:
        """Get a user by their Telegram ID."""
        with self.session_scope() as session:
            return (
                session.query(TelegramUser)
                .filter(TelegramUser.telegram_id == telegram_id)
                .first()
            )

    def get_active_users(self) -> list[TelegramUser]:
        """Get all active Telegram users."""
        with self.session_scope() as session:
            return (
                session.query(TelegramUser)
                .filter(TelegramUser.is_active.is_(True))
                .all()
            )

    def set_user_active(self, telegram_id: int, is_active: bool) -> bool:
        """Activate or deactivate a user (e.g., when bot is blocked by user)."""
        with self.session_scope() as session:
            user = (
                session.query(TelegramUser)
                .filter(TelegramUser.telegram_id == telegram_id)
                .first()
            )
            if not user:
                return False
            user.is_active = is_active
            return True

    # --- Reminder operations (wp_telegram_send_reminders) ---

    def is_reminder_sent(
        self,
        event_id: int,
        telegram_id: int = None,
        reminder_type: str = "default",
    ) -> bool:
        """Check whether a reminder for a given event (and optionally user) was already sent."""
        with self.session_scope() as session:
            query = session.query(TelegramSendReminder).filter(
                TelegramSendReminder.event_id == event_id,
                TelegramSendReminder.reminder_type == reminder_type,
            )
            if telegram_id is not None:
                query = query.filter(TelegramSendReminder.telegram_id == telegram_id)
            return session.query(query.exists()).scalar()

    def record_reminder(
        self,
        event_id: int,
        telegram_id: int = None,
        reminder_type: str = "default",
        status: str = "sent",
    ) -> TelegramSendReminder:
        """Record a sent reminder in wp_telegram_send_reminders."""
        with self.session_scope() as session:
            existing = (
                session.query(TelegramSendReminder)
                .filter(
                    TelegramSendReminder.event_id == event_id,
                    TelegramSendReminder.telegram_id == telegram_id,
                    TelegramSendReminder.reminder_type == reminder_type,
                )
                .first()
            )
            if existing:
                existing.status = status
                session.flush()
                session.refresh(existing)
                return existing

            reminder = TelegramSendReminder(
                event_id=event_id,
                telegram_id=telegram_id,
                reminder_type=reminder_type,
                status=status,
            )
            session.add(reminder)
            session.flush()
            session.refresh(reminder)
            return reminder

    def get_reminders_for_event(self, event_id: int) -> list[TelegramSendReminder]:
        """Get all recorded reminders for a specific WordPress event ID."""
        with self.session_scope() as session:
            return (
                session.query(TelegramSendReminder)
                .filter(TelegramSendReminder.event_id == event_id)
                .all()
            )


db_manager = DBManager()
