import datetime

from sqlalchemy import select, insert, update, column, text, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.model import (UsersTable, FormTable, TransactionsTable, RequestsTable,
                            DeeplinksTable, OneTimeLinksIdsTable, AdminsTable, ComplainsTable,
                            ImpressionsModelTable, UserImpressionsTable, WatchesTable, OpTable,
                            RatesTable, ApplicationsTable)

from dateutil.relativedelta import relativedelta
from utils.translator import Translator as create_translator
from utils.translator.translator import Translator



class DataInteraction():
    def __init__(self, session: async_sessionmaker):
        self._sessions = session

    async def check_language(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable.locale).where(UsersTable.user_id == user_id))
        return True if result else False

    async def add_watch(self, user_id: int, form_id: int):
        async with self._sessions() as session:
            await session.execute(insert(WatchesTable).values(
                user_id=user_id,
                form_id=form_id
            ))
            await session.commit()

    async def check_form(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(FormTable).where(FormTable.user_id == user_id))
        return True if result else False

    async def check_user_impression(self, impression_id: int, user_id: int) -> bool:
        async with self._sessions() as session:
            result = await session.scalar(select(UserImpressionsTable).where(and_(
                UserImpressionsTable.user_id == user_id,
                UserImpressionsTable.impression_id == impression_id
            )))
        return True if result else False

    async def check_request(self, sender: int, receiver: int):
        async with self._sessions() as session:
            result = await session.scalar(select(RequestsTable).where(
                and_(
                    RequestsTable.sender == sender,
                    RequestsTable.receiver == receiver
                )
            ))
            return True if result else False

    async def check_user(self, user_id: int) -> bool:
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable).where(UsersTable.user_id == user_id))
        return True if result else False

    async def add_user(self, user_id: int, username: str, name: str, referral: int | None):
        if await self.check_user(user_id):
            return
        async with self._sessions() as session:
            await session.execute(insert(UsersTable).values(
                user_id=user_id,
                username=username,
                name=name,
                referral=referral
            ))
            await session.commit()

    async def add_refs(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                refs=UsersTable.refs + 1
            ))
            await session.commit()

    async def add_application(self, user_id: int, photos: list[str], message_ids: list[int]):
        application = await self.get_application(user_id)
        if application:
            await self.del_application(user_id)
        async with self._sessions() as session:
            await session.execute(insert(ApplicationsTable).values(
                user_id=user_id,
                photos=photos,
                message_ids=message_ids
            ))
            await session.commit()

    async def add_form(
            self, user_id: int, name: str, male: str, age: int,
            city: str, profession: str, education: str, income: str, description: str,
            religion: str, family: str, children_count: str|int, children: str, leave: str, second_wife: int | None=None
    ):
        if not await self.get_form(user_id):
            async with self._sessions() as session:
                await session.execute(insert(FormTable).values(
                    user_id=user_id,
                    name=name,
                    male=male,
                    age=age,
                    city=city,
                    profession=profession,
                    education=education,
                    income=income,
                    description=description,
                    religion=religion,
                    family=family,
                    children_count=str(children_count),
                    children=children,
                    leave=leave,
                    second_wife=second_wife
                ))
                await session.commit()
        else:
            async with self._sessions() as session:
                await session.execute(update(FormTable).where(FormTable.user_id == user_id).values(
                    user_id=user_id,
                    name=name,
                    male=male,
                    age=age,
                    city=city,
                    profession=profession,
                    education=education,
                    income=income,
                    description=description,
                    religion=religion,
                    family=family,
                    children_count=str(children_count),
                    children=children,
                    leave=leave,
                    second_wife=second_wife,
                ))
                await session.commit()

    async def add_rate(self, amount: int, price: int):
        async with self._sessions() as session:
            await session.execute(insert(RatesTable).values(
                amount=amount,
                price=price,
            ))
            await session.commit()

    async def add_request(self, sender: int, receiver: int) -> bool:
        if await self.check_request(sender, receiver):
            return False
        async with self._sessions() as session:
            await session.execute(insert(RequestsTable).values(
                sender=sender,
                receiver=receiver
            ))
            await session.commit()
        return True

    async def add_op(self, chat_id: int, name: str, link: str):
        async with self._sessions() as session:
            await session.execute(insert(OpTable).values(
                chat_id=chat_id,
                name=name,
                link=link
            ))
            await session.commit()

    async def add_transaction(self, user_id: int, sum: int, description: str | None = None):
        async with self._sessions() as session:
            await session.execute(insert(TransactionsTable).values(
                user_id=user_id,
                sum=sum,
                description=description
            ))
            await session.commit()

    async def add_deeplink(self, link: str):
        async with self._sessions() as session:
            await session.execute(insert(DeeplinksTable).values(
                link=link
            ))
            await session.commit()

    async def add_link(self, link: str):
        async with self._sessions() as session:
            await session.execute(insert(OneTimeLinksIdsTable).values(
                link=link
            ))
            await session.commit()

    async def add_admin(self, user_id: int, name: str):
        async with self._sessions() as session:
            await session.execute(insert(AdminsTable).values(
                user_id=user_id,
                name=name
            ))
            await session.commit()

    async def add_complain(self, user_id: int, form_user_id: int, complain: str):
        async with self._sessions() as session:
            await session.execute(insert(ComplainsTable).values(
                user_id=user_id,
                form_user_id=form_user_id,
                complain=complain
            ))
            await session.commit()

    async def add_impressions_model(
            self, male: list[str] | None, min_age: int | None, max_age: int | None,
            city: list[str] | None, profession: list[str] | None, education: list[str] | None,
            income: list[str] | None, religion: list[str] | None, family: list[str] | None,
            children_count: str | None, children: list[str] | None,
            message_id: int, from_chat_id: int, keyboard: list[list[str]]|None
    ):
        async with self._sessions() as session:
            await session.execute(insert(ImpressionsModelTable).values(
                male=male,
                min_age=min_age,
                max_age=max_age,
                city=city,
                profession=profession,
                education=education,
                income=income,
                religion=religion,
                family=family,
                children_count=children_count,
                children=children,
                message_id=message_id,
                from_chat_id=from_chat_id,
                keyboard=keyboard
            ))
            await session.commit()

    async def get_user_watches(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalars(select(WatchesTable).where(WatchesTable.user_id == user_id))
        return result.fetchall()

    async def add_user_impression(self, impression_id: int, user_id: int, shown: bool):
        async with self._sessions() as session:
            impression = await session.scalar(select(ImpressionsModelTable).where(ImpressionsModelTable.id == impression_id))
            model = UserImpressionsTable(
                impression_id=impression_id,
                user_id=user_id,
                shown=shown,
            )
            session.add(model)
            await session.commit()

    async def get_impressions(self):
        async with self._sessions() as session:
            result = await session.scalars(select(ImpressionsModelTable))
        return result.fetchall()

    async def get_impression(self, id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(ImpressionsModelTable).where(ImpressionsModelTable.id == id))
        return result

    async def get_transactions(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalars(select(TransactionsTable).where(TransactionsTable.user_id == user_id).
                                           order_by(TransactionsTable.create))
        return result.fetchall()

    async def get_all_transactions(self):
        async with self._sessions() as session:
            result = await session.scalars(select(TransactionsTable).order_by(TransactionsTable.create))
        return result.fetchall()

    async def get_my_requests(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalars(select(RequestsTable).where(RequestsTable.sender == user_id))
        return result.fetchall()

    async def get_rate(self, id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(RatesTable).where(RatesTable.id == id))
        return result

    async def get_rates(self):
        async with self._sessions() as session:
            result = await session.scalars(select(RatesTable))
        return result.fetchall()

    async def get_complains(self):
        async with self._sessions() as session:
            result = await session.scalars(select(ComplainsTable))
        return result.fetchall()

    async def get_op(self):
        async with self._sessions() as session:
            result = await session.scalars(select(OpTable))
        return result.fetchall()

    async def get_op_by_chat_id(self, chat_id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(OpTable).where(OpTable.chat_id == chat_id))
        return result

    async def get_requests_to_my(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalars(select(RequestsTable).where(RequestsTable.receiver == user_id))
        return result.fetchall()

    async def get_request(self, id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(RequestsTable).where(RequestsTable.id == id))
        return result

    async def get_form(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(FormTable).where(FormTable.user_id == user_id))
        return result

    async def get_form_by_id(self, id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(FormTable).where(FormTable.id == id))
        return result

    async def get_application(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(ApplicationsTable).where(ApplicationsTable.user_id == user_id))
        return result

    async def get_forms(self):
        async with self._sessions() as session:
            result = await session.scalars(select(FormTable))
        return result.fetchall()

    async def get_user(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable).where(UsersTable.user_id == user_id))
        return result

    async def get_links(self):
        async with self._sessions() as session:
            result = await session.scalars(select(OneTimeLinksIdsTable))
        return result.fetchall()

    async def get_users(self):
        async with self._sessions() as session:
            result = await session.scalars(select(UsersTable))
        return result.fetchall()

    async def get_best_refs(self):
        async with self._sessions() as session:
            result = await session.scalars(select(UsersTable).order_by(UsersTable.refs))
        return result.fetchall()

    async def get_admins(self):
        async with self._sessions() as session:
            result = await session.scalars(select(AdminsTable))
        return result.fetchall()

    async def get_deeplinks(self):
        async with self._sessions() as session:
            result = await session.scalars(select(DeeplinksTable))
        return result.fetchall()

    async def update_form(self, user_id: int, **kwargs):
        async with self._sessions() as session:
            await session.execute(update(FormTable).where(FormTable.user_id == user_id).values(
                kwargs
            ))
            await session.commit()

    async def update_vip(self, user_id: int, vip: bool, vip_end: datetime.datetime | None=None):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                vip=vip,
                vip_end=(vip_end if vip_end else UsersTable.vip_end)
            ))
            await session.commit()

    async def update_tokens(self, user_id: int, tokens: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                tokens=UsersTable.tokens + tokens
            ))
            await session.commit()

    async def update_balance(self, user_id: int, amount: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                balance=UsersTable.balance + amount
            ))
            await session.commit()

    async def update_income(self, user_id: int, income: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                balance=UsersTable.income + income
            ))
            await session.commit()

    async def update_photos(self, user_id: int, photos: list[str]):
        async with self._sessions() as session:
            await session.execute(update(FormTable).where(FormTable.user_id == user_id).values(
                photos=photos
            ))
            await session.commit()

    async def set_block(self, user_id):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                block=True
            ))
            await session.commit()

    async def set_locale(self, user_id: int, locale: str):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                locale=locale
            ))
            await session.commit()

    async def set_active(self, user_id: int, active: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                active=active
            ))
            await session.commit()

    async def set_activity(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                activity=datetime.datetime.today()
            ))
            await session.commit()

    async def set_form_active(self, user_id: int, active: bool):
        async with self._sessions() as session:
            await session.execute(update(FormTable).where(FormTable.user_id == user_id).values(
                active=active
            ))
            await session.commit()

    async def set_button_link(self, chat_id: int, link: str):
        async with self._sessions() as session:
            await session.execute(update(OpTable).where(OpTable.chat_id == chat_id).values(
                link=link
            ))
            await session.commit()

    async def set_rate_amount(self, id: int, amount: int):
        async with self._sessions() as session:
            await session.execute(update(RatesTable).where(RatesTable.id == id).values(
                amount=amount
            ))
            await session.commit()

    async def set_rate_price(self, id: int, price: int):
        async with self._sessions() as session:
            await session.execute(update(RatesTable).where(RatesTable.id == id).values(
                price=price
            ))
            await session.commit()

    async def add_entry(self, link: str):
        async with self._sessions() as session:
            await session.execute(update(DeeplinksTable).where(DeeplinksTable.link == link).values(
                entry=DeeplinksTable.entry+1
            ))
            await session.commit()

    async def del_request(self, id: int):
        async with self._sessions() as session:
            await session.execute(delete(RequestsTable).where(RequestsTable.id == id))
            await session.commit()

    async def del_requests(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(delete(RequestsTable).where(
                or_(
                    RequestsTable.sender == user_id,
                    RequestsTable.receiver == user_id
                )
            ))
            await session.commit()

    async def del_deeplink(self, link: str):
        async with self._sessions() as session:
            await session.execute(delete(DeeplinksTable).where(DeeplinksTable.link == link))
            await session.commit()

    async def del_link(self, link_id: str):
        async with self._sessions() as session:
            await session.execute(delete(OneTimeLinksIdsTable).where(OneTimeLinksIdsTable.link == link_id))
            await session.commit()

    async def del_admin(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(delete(AdminsTable).where(AdminsTable.user_id == user_id))
            await session.commit()

    async def del_complain(self, id: int):
        async with self._sessions() as session:
            await session.execute(delete(ComplainsTable).where(ComplainsTable.id == id))
            await session.commit()

    async def del_rate(self, id: int):
        async with self._sessions() as session:
            await session.execute(delete(RatesTable).where(RatesTable.id == id))
            await session.commit()

    async def del_application(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(delete(ApplicationsTable).where(ApplicationsTable.user_id == user_id))
            await session.commit()

    async def del_form(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(delete(FormTable).where(FormTable.user_id == user_id))
            await session.commit()

    async def del_impression(self, id: int):
        async with self._sessions() as session:
            await session.execute(delete(ImpressionsModelTable).where(ImpressionsModelTable.id == id))
            await session.commit()

    async def del_watch(self, id: int):
        async with self._sessions() as session:
            await session.execute(delete(WatchesTable).where(WatchesTable.id == id))
            await session.commit()

    async def filter_forms_without_city(self, user_id: int, counter: int, search: list) -> list[int] | list:
        user = await self.get_user(user_id)
        form = await self.get_form(user_id)
        translator = create_translator(user.locale)
        async with self._sessions() as session:
            stmt = select(FormTable).where(
                and_(
                    FormTable.age.in_(range(form.age - counter, form.age + counter)),
                    FormTable.male == (translator['women_button'] if form.male == translator['men_button'] else translator['men_button']),
                    FormTable.religion == form.religion,
                    FormTable.active == True
                )
            ).order_by(FormTable.age)
            forms = (await session.scalars(stmt)).fetchall()
        if not forms:
            async with self._sessions() as session:
                stmt = select(FormTable).where(
                    and_(
                        FormTable.age.in_(range(form.age - counter, form.age + counter)),
                        FormTable.male == (
                            translator['women_button'] if form.male == translator['men_button'] else translator[
                                'men_button']),
                        FormTable.active == True
                    )
                ).order_by(FormTable.age)
                forms = (await session.scalars(stmt)).fetchall()
        watches = await self.get_user_watches(user_id)
        watches_form_ids = [watch.form_id for watch in watches]
        for form in forms:
            if form.id not in watches_form_ids:
                search.append(form.id)
            else:
                for watch in watches:
                    if watch.form_id == form.id:
                        print(watch.view, datetime.datetime.today() - datetime.timedelta(days=2))
                        if watch.view < datetime.datetime.today() - datetime.timedelta(days=2):
                            await self.del_watch(watch.id)
                            search.append(form.id)
        return search

    async def filter_forms(self, user_id: int, counter: int = 2, count=0) -> list[int] | None:
        user = await self.get_user(user_id)
        form = await self.get_form(user_id)
        translator = create_translator(user.locale)
        search = []
        async with self._sessions() as session:
            stmt = select(FormTable).where(
                and_(
                    FormTable.age.in_(range(form.age - counter, form.age + counter)),
                    FormTable.male == (translator['women_button'] if form.male == translator['men_button'] else translator['men_button']),
                    FormTable.religion == form.religion,
                    FormTable.city == form.city,
                    FormTable.active == True
                )
            ).order_by(FormTable.age)
            forms = (await session.scalars(stmt)).fetchall()
        watches = await self.get_user_watches(user_id)
        watches_form_ids = [watch.form_id for watch in watches]
        for form in forms:
            if form.id not in watches_form_ids:
                search.append(form.id)
            else:
                for watch in watches:
                    if watch.form_id == form.id:
                        if watch.view < datetime.datetime.today() - datetime.timedelta(days=2):
                            await self.del_watch(watch.id)
                            search.append(form.id)
        if not search:
            search = await self.filter_forms_without_city(user_id, counter, search)
        if not search and count == 4:
            return None
        if not search:
            search = await self.filter_forms(user_id, counter + 2, count+1)
        return search

    async def filter_forms_by_params(self, user_id: int, **kwargs) -> list[int] | None:
        user = await self.get_user(user_id)
        form = await self.get_form(user_id)
        translator = create_translator(user.locale)
        search = []
        async with self._sessions() as session:
            stmt = select(FormTable).where(
                and_(
                    (FormTable.age.in_(range(kwargs.get('age')[0], kwargs.get('age')[1]))) if kwargs.get('age') else True,
                    FormTable.male == (translator['women_button'] if form.male == translator['men_button'] else translator['men_button']),
                    (FormTable.city == kwargs.get('city')) if kwargs.get('city') else True,
                    (FormTable.family == kwargs.get('family')) if kwargs.get('family') else True,
                    (FormTable.children == kwargs.get('children')) if kwargs.get('children') else True,
                    (FormTable.religion == kwargs.get('religion')) if kwargs.get('religion') else True,
                    FormTable.active == True
                )
            ).order_by(FormTable.age)
            forms = (await session.scalars(stmt)).fetchall()
        watches = await self.get_user_watches(user_id)
        watches_form_ids = [watch.form_id for watch in watches]
        for form in forms:
            if form.id not in watches_form_ids:
                search.append(form.id)
            else:
                for watch in watches:
                    if watch.form_id == form.id:
                        if watch.view < datetime.datetime.today() - datetime.timedelta(days=2):
                            await self.del_watch(watch.id)
                            search.append(form.id)
                        break
        return search

    async def targeting_filter(self, **kwargs) -> list[int]:
        users = []
        async with self._sessions() as session:
            forms = await session.scalars(select(FormTable))
        for form in forms.fetchall():
            user = await self.get_user(form.user_id)
            translator = create_translator(user.locale)
            if (
                ((form.male in [translator[v] for i, v in kwargs.get('male').items()]) if kwargs.get('male') else True)
                and ((form.age in range(kwargs.get('age')[0], kwargs.get('age')[1])) if kwargs.get('age') else True)
                and ((form.city in [city for city in kwargs.get('city')]) if kwargs.get('city') else True)
                and ((form.profession in [city for city in kwargs.get('profession')]) if kwargs.get('profession') else True)
                and ((form.education in [translator[v] for i, v in kwargs.get('education').items()]) if kwargs.get('education') else True)
                and ((form.income in [translator[v] for i, v in kwargs.get('income').items()]) if kwargs.get('income') else True)
                and ((form.religion in [translator[v] for i, v in kwargs.get('religion').items()]) if kwargs.get('religion') else True)
                # отдельное условие
                and ((form.children_count == kwargs.get('children_count') if isinstance(kwargs.get('children_count'), int)
                else form.children_count == translator[kwargs.get('children_count')])
                if kwargs.get('children_count') else True)
                # конец условия
                and ((form.children in [translator[v] for i, v in kwargs.get('children').items()]) if kwargs.get('children') else True)
            ):
                users.append(form.user_id)

        return users

