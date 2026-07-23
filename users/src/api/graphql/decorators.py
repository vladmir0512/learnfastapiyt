from functools import wraps

from sqlalchemy.sql.functions import current_user

from api.graphql.user.schemas import UserPage


def require_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        info = kwargs.get("info") or args[1]
        current_user = info.context.get("current_user")
        if not current_user:
            raise ValueError("Authentication required")

        return func(*args, **kwargs)
    return wrapper


def paginate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        limit = kwargs.get("limit") or 10
        offset = kwargs.get("offset") or 0
        all_items = func(*args, **kwargs)
        total_items = len(all_items)
        paginated_items = list(all_items)[offset:offset + limit]
        return UserPage(items=paginated_items, total=total_items, limit=limit, offset=offset)
    return wrapper