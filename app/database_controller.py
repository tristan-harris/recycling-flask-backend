from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .database import db
from .enums import StaffRole, SubmissionStatus, ActionType
from .models import AllowedRecyclable, Bin, User, Staff, Reward, Purchase, Recyclable, \
                    Submission, UserActionLog

class InvalidDataError(Exception):
    def __init__(self, message = "Invalid data"):
        self.message = message
        super().__init__(self.message)

class FailedAuthenticationError(Exception):
    def __init__(self, message = "Authentication failed"):
        self.message = message
        super().__init__(self.message)

class ForbiddenRequestError(Exception):
    def __init__(self, message = "Forbidden request"):
        self.message = message
        super().__init__(self.message)

class NotFoundError(Exception):
    def __init__(self, message = "Resource not found"):
        self.message = message
        super().__init__(self.message)

class ServerError(Exception):
    def __init__(self, message = "Unexpected server error"):
        self.message = message
        super().__init__(self.message)

def database_commit() -> bool:
    try:
        db.session.commit()
        return True
    except IntegrityError as e:
        db.session.rollback()
        raise InvalidDataError() from e
    except SQLAlchemyError as e:
        print(f"SQLAlchemyError -> {e}")
        db.session.rollback()
        raise ServerError("Unexpected server error") from e
    except Exception as e:
        print(f"Error -> {e}")
        db.session.rollback()
        raise ServerError() from e

class DatabaseController:

    def create_new(self, model, data:dict, actor_user_id:int|None):
        instance = model(**data)
        db.session.add(instance)

        committed = database_commit()
        if committed:
            self.log_user_action(
                actor_user_id, ActionType.create, instance.id, model.__tablename__, None, instance.to_dict()
            )

        return instance

    def get(self, model, key:str, value):
        scalar = db.session.execute(db.select(model)
            .where(getattr(model, key) == value)).scalar_one_or_none()
        if scalar is None:
            raise NotFoundError()
        return scalar

    def get_all(self, model):
        scalars = db.session.execute(db.select(model)).scalars().all()
        return scalars

    def get_all_matching(self, model, key:str, value):
        scalars = db.session.execute(db.select(model).where(getattr(model, key) == value)).scalars()
        return scalars

    def update(self, model, key:str, value, data:dict, actor_user_id:int):
        scalar = db.session.execute(db.select(model) \
                                    .where(getattr(model, key) == value)) \
                                    .scalar_one_or_none()
        if scalar is None:
            raise NotFoundError()

        scalar_before_data = scalar.to_dict()

        for key, value in data.items():
            setattr(scalar, key, value)

        committed = database_commit()
        if committed:
            self.log_user_action(
                actor_user_id, ActionType.update, scalar.id, model.__tablename__,
                scalar_before_data, scalar.to_dict()
            )

    def delete(self, model, key:str, value, actor_user_id:int):
        scalar = db.session.execute(db.select(model).where(getattr(model, key) == value)).scalar()
        if scalar is None:
            raise NotFoundError()

        db.session.delete(scalar)

        committed = database_commit()
        if committed:
            self.log_user_action(
                actor_user_id, ActionType.delete, scalar.id, model.__tablename__, scalar.to_dict(), None
            )

    def log_user_action(self, user_id:int|None, action_type:ActionType, resource_id:int,
                        resource_table:str, data_before:dict|None, data_after:dict|None):

        log = UserActionLog(user_id=user_id, action_type=action_type,               # pyright: ignore
                            resource_id=resource_id, resource_table=resource_table, # pyright: ignore
                            data_before=data_before, data_after=data_after)         # pyright: ignore

        db.session.add(log)
        database_commit()

    def is_unique(self, model, key:str, value) -> bool:
        scalar = db.session.execute(db.select(model)
            .where(getattr(model, key) == value)).scalar_one_or_none()
        return scalar is None

    def is_frozen(self, id:int) -> bool:
        try:
            user = self.get(User, "id", id)
            return user.frozen
        except NotFoundError as e:
            raise NotFoundError("User not found") from e

    def get_count_of(self, model) -> int:
        count = db.session.execute(select(func.count()).select_from(model)).scalar()
        if not isinstance(count, int):
            raise ValueError("Result of `get_count_of` is not int")
        return count

    def get_user_balance(self, id:int) -> int:

        # ensure that user exists first
        try:
            self.get(User, "id", id)
        except NotFoundError as e:
            raise NotFoundError("User not found") from e

        submissions_subquery = db.select(Recyclable.points_value) \
            .join(Submission, Submission.recyclable_id == Recyclable.id) \
            .where(Submission.user_id == id
                   and Submission.status == SubmissionStatus.confirmed).subquery()

        earned_query = db.select(db.func.sum(submissions_subquery.c.points_value))
        points_earned = db.session.execute(earned_query).scalar_one_or_none()
        if points_earned is None:
            points_earned = 0

        purchases_subquery = db.select(Purchase.quantity, Reward.price) \
            .join(Reward, Purchase.reward_id == Reward.id) \
            .where(Purchase.user_id == id).subquery()

        spent_query = db.select(
            db.func.sum(purchases_subquery.c.quantity * purchases_subquery.c.price))
        points_spent = db.session.execute(spent_query).scalar_one_or_none()
        if points_spent is None:
            points_spent = 0

        return int(points_earned - points_spent)

    def get_bin_whitelist(self, id:int):
        recyclables = []
        try:
            bin = self.get(Bin, "id", id)
        except NotFoundError as e:
            raise NotFoundError("Bin not found") from e

        if not bin.whitelist:
            return recyclables

        allowed_recyclables = db.session \
            .execute(db.select(AllowedRecyclable) \
            .where(AllowedRecyclable.bin_id==bin.id)).scalars().all()

        for allowed_recyclable in allowed_recyclables:
            recyclable = self.get(Recyclable, "id", allowed_recyclable.recyclable_id)
            recyclables.append(recyclable)

        return recyclables

    def validate_login(self, data:dict):

        user = None
        if "username" in data:
            user = self.get(User, "username", data["username"])
        else:
            user = self.get(User, "email", data["email"])

        if user is None:
            raise NotFoundError("User not found")
        if not user.check_password(data["password"]):
            raise FailedAuthenticationError()

        return user

    # if User is owner of particular resource (User, Submission, Purchase etc)
    def is_owner(self, user_id:int, model, resource_id:int):
        try:
            resource = self.get(model, "id", resource_id)
        except NotFoundError:
            return False

        if model is User:
            return user_id == resource.id

        return getattr(resource, "user_id", -1) == user_id

    # admins also have moderator privileges
    def has_moderator_access_level(self, id:int) -> bool:
        staff = db.session.execute(db.select(Staff).where(Staff.user_id==id)).scalar_one_or_none()
        return staff is not None

    def has_admin_access_level(self, id:int) -> bool:
        staff = db.session.execute(db.select(Staff).where(Staff.user_id==id)).scalar_one_or_none()
        if staff is None or staff.role != StaffRole.admin:
            return False
        return True

    def is_owner_or_moderator(self, user_id:int, model, resource_id:int) -> bool:
        if self.has_moderator_access_level(user_id):
            return True
        if self.is_owner(user_id, model, resource_id):
            return True
        return False

    def is_owner_or_admin(self, user_id:int, model, resource_id:int) -> bool:
        if self.has_admin_access_level(user_id):
            return True
        if self.is_owner(user_id, model, resource_id):
            return True
        return False
