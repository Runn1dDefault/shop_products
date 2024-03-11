from db.connections import db_session_manager


async def list_parameters(skip: int = 0, limit: int = 10, search: str = None, ordering: str = None):
    if limit > 30:
        limit = 30

    if not ordering:
        ordering = ''
    return {"skip": skip, "limit": limit, "search": search, "ordering": list(ordering.replace(' ', '').split(','))}


async def get_db():
    async with db_session_manager.session() as session:
        yield session
