from aiomysql import DictCursor
from aiomysql.connection import Connection as aiomysql_connect

from settings import settings


async def create_db_conn(loop):
    db_conf = settings['async_database']
    conn = aiomysql_connect(host=db_conf['host'],
                            port=db_conf['port'],
                            user=db_conf['user'],
                            password=db_conf['pass'],
                            db=db_conf['name'],
                            charset='utf8',
                            loop=loop)

    await conn._connect()
    return conn


class AsyncSession:
    def __init__(self, loop):
        self._loop = loop

    async def __aenter__(self):
        self._conn = await create_db_conn(self._loop)
        return self._conn

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            await self._conn.rollback()

        self._conn.close()


async def db_executemany(db, sql, params=None, autocommit=True, echo=False):
    async with db.cursor() as cur:
        if echo:
            print(cur.mogrify(sql, args=params))

        await cur.executemany(sql, params)
        if autocommit:
            await db.commit()


async def db_execute(db, sql, params=None, autocommit=False, echo=False):
    async with db.cursor() as cur:
        if echo:
            print(cur.mogrify(sql, args=params))

        await cur.execute(sql, args=params)
        if autocommit:
            await db.commit()

        return {
            'lastrowid': cur.lastrowid,
            'rowcount': cur.rowcount
        }


async def db_fetch(db, sql, params, as_dict, one=False, echo=False):
    async with db.cursor(DictCursor if as_dict else None) as cur:
        if echo:
            print(cur.mogrify(sql, args=params))

        await cur.execute(sql, args=params)
        await db.commit()
        return await cur.fetchone() if one else await cur.fetchall()


async def db_fetchone(db, sql, params=None, as_dict=False, echo=False):
    return await db_fetch(db, sql, params, as_dict, one=True, echo=echo)


async def db_fetchall(db, sql, params=None, as_dict=False, echo=False):
    return await db_fetch(db, sql, params, as_dict, echo=echo)
