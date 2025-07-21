from datetime import date, datetime

from sqlalchemy import (
    ForeignKey,
    Integer,
    Float,
    String,
    Boolean,
    Enum,
    Date,
    DECIMAL,
    TIMESTAMP,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash

from .database import db
from .enums import StaffRole, SubmissionStatus, ActionType


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)  # stored as hash
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False, default="")
    first_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    organisation: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    frozen: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone_number": self.phone_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth.isoformat(),
            "organisation": self.organisation,
            "frozen": self.frozen,
            "created_at": int(self.created_at.timestamp()),
        }

    def __repr__(self) -> str:
        return str(self.to_dict())


class Motivation(db.Model):
    __tablename__ = "motivations"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False
    )
    motivation: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "motivation": self.motivation,
            "created_at": int(self.created_at.timestamp()),
        }

    def __repr__(self) -> str:
        return str(self.to_dict())


class Staff(db.Model):
    __tablename__ = "staff"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False
    )
    role: Mapped[StaffRole] = mapped_column(Enum(StaffRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "role": self.role.value,
            "created_at": int(self.created_at.timestamp()),
        }

    def __repr__(self) -> str:
        return str(self.to_dict())


class Bin(db.Model):
    __tablename__ = "bins"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    latitude: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)

    # false means bin accepts any recyclable
    whitelist: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),
            "whitelist": self.whitelist,
            "name": self.name,
            "description": self.description,
            "created_at": int(self.created_at.timestamp()),
        }

    def __repr__(self) -> str:
        return str(self.to_dict())


class AllowedRecyclable(db.Model):
    __tablename__ = "allowed_recyclables"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    bin_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bins.id"), primary_key=True, nullable=False
    )
    recyclable_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recyclables.id"), primary_key=True, nullable=False
    )

    def to_dict(self) -> dict:
        return {"bin_id": self.bin_id, "recyclable_id": self.recyclable_id}

    def __repr__(self) -> str:
        return str(self.to_dict())


class Recyclable(db.Model):
    __tablename__ = "recyclables"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    type: Mapped[str] = mapped_column(String(200), nullable=False)
    points_value: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "points_value": self.points_value,
            "description": self.description,
            "weight": self.weight,
            "created_at": int(self.created_at.timestamp()),
        }

    def __repr__(self) -> str:
        return str(self.to_dict())


class Submission(db.Model):
    __tablename__ = "submissions"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    recyclable_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recyclables.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    bin_id: Mapped[int] = mapped_column(Integer, ForeignKey("bins.id"), nullable=False)
    latitude: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus), nullable=False, default=SubmissionStatus.not_confirmed
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "recyclable_id": self.recyclable_id,
            "user_id": self.user_id,
            "bin_id": self.bin_id,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),
            "status": self.status.value,
            "created_at": int(self.created_at.timestamp()),
        }

    def __repr__(self) -> str:
        return str(self.to_dict())


class Reward(db.Model):
    __tablename__ = "rewards"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False, default="")
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "created_at": int(self.created_at.timestamp()),
        }

    def __repr__(self) -> str:
        return str(self.to_dict())


class Purchase(db.Model):
    __tablename__ = "purchases"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    reward_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rewards.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "reward_id": self.reward_id,
            "quantity": self.quantity,
            "created_at": int(self.created_at.timestamp()),
        }

    def __repr__(self) -> str:
        return str(self.to_dict())


class UserActionLog(db.Model):
    __tablename__ = "user_action_logs"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )

    # (current) user_id can be null when, for instance, a new account is created
    # no foreign key constraint is applied since the log may refer to a user account that no longer exists
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)

    action_type: Mapped[ActionType] = mapped_column(Enum(ActionType), nullable=False)
    resource_id: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_table: Mapped[str] = mapped_column(String(255), nullable=False)
    data_before: Mapped[dict] = mapped_column(JSON, nullable=True)
    data_after: Mapped[dict] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action_type": self.action_type.value,
            "resource_id": self.resource_id,
            "resource_table": self.resource_table,
            "data_before": self.data_before,
            "data_after": self.data_after,
            "timestamp": int(self.timestamp.timestamp()),
        }

    def __repr__(self) -> str:
        return str(self.to_dict())
