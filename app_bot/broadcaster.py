import asyncio
import logging
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from aiogram import Bot, types
from aiogram.utils.i18n import I18n
from core.database import init
from core.database.models import User, Dispatcher, Post, CitiesForParser
from mail_parser.mail_parser import mail_parser
from settings import settings


logger = logging.getLogger(__name__)
bot = Bot(settings.bot_token.get_secret_value(), parse_mode='HTML')
i18n = I18n(path='locales', default_locale='ru', domain='messages')
i18n.set_current(i18n)


class Broadcaster(object):
    @staticmethod
    async def __send_mailing_msg_to_user(user_id: int, message: types.Message, bot: Bot):
        if message.photo:
            await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption)

        elif message.text:
            await bot.send_message(chat_id=user_id, text=message.text)


    @staticmethod
    async def __send_content_message(post: Post, user_id: int):
        try:
            if not post.photo_file_id and not post.video_file_id and not post.video_note_id \
                    and not post.document_file_id and post.text:
                await bot.send_message(chat_id=user_id, text=post.text)

            elif post.photo_file_id:  # photo
                await bot.send_photo(chat_id=user_id, photo=post.photo_file_id, caption=post.text)

            elif post.video_file_id:  # video
                await bot.send_video(chat_id=user_id, video=post.video_file_id, caption=post.text)

            elif post.video_note_id:  # video_note
                if post.text:
                    await bot.send_message(chat_id=user_id, text=post.text)
                await bot.send_video_note(chat_id=user_id, video_note=post.video_note_id)

            elif post.document_file_id:  # document
                await bot.send_document(chat_id=user_id, document=post.document_file_id, caption=post.text)
            else:
                logger.error(f'Unexpected content type: post_id={post.id}')

        except Exception as e:
            logger.error(f'Content sending error: user_id={user_id}, post_id={post.id}', exc_info=e)


    @classmethod
    async def send_content_to_users(cls, bot: Bot, message: types.Message = None,
                                    broadcaster_post: Post = None, museum_id: int = None):
        sent_amount = 0

        if museum_id:
            users_ids = await User.filter(museum_id=museum_id).all()
        else:
            users_ids = await User.all()
        if not users_ids:
            return sent_amount

        for i in range(0, len(users_ids), settings.mailing_batch_size):
            user_batch = users_ids[i:i + settings.mailing_batch_size]
            for user in user_batch:
                # send mailing from admin panel
                if broadcaster_post:
                    try:
                        await cls.__send_content_message(post=broadcaster_post, user_id=user.user_id)
                    except Exception as e:
                        logger.error(f'Error in mailing from admin panel, user_id={user.user_id}', exc_info=e)

                # send mailing via /send
                else:
                    try:
                        await cls.__send_mailing_msg_to_user(user_id=user.user_id, message=message, bot=bot)
                        sent_amount += 1
                    except Exception as e:
                        logger.error(f'Error in mailing via /send, user_id={user.user_id}', exc_info=e)

        return sent_amount


    # send mailing from admin panel
    @classmethod
    async def order_work(cls, order: Dispatcher):
        city: CitiesForParser | None = await order.city
        if city:
            # sending - check is it for city => call mail_parser
            await mail_parser(bot=bot, city=city)

            # update city and order (+24 hours)
            try:
                city.was_sent = True
                await city.save()

                await Dispatcher.filter(id=order.id).update(
                    send_at=(datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=1)).replace(
                        hour=city.hour, minute=city.minute, second=0, microsecond=0
                    ),
                )
            except Exception as e:
                logger.critical(f'Update order for city {city.name} error', exc_info=e)
                return

        # default mailing
        else:
            try:
                post = await Post.filter(id=(await order.post).id).first()
            except Exception as e:
                logger.error(f'Get post error', exc_info=e)
                return

            await cls.send_content_to_users(bot=bot, broadcaster_post=post, museum_id=order.museum_id)

            # delete order
            try:
                await Dispatcher.filter(id=order.id).delete()
            except Exception as e:
                logger.critical(f'Delete order error', exc_info=e)
                return

            logger.info(f'order_id={order.id} has been sent to users')


    @classmethod
    async def send_notification(cls):
        # send daily notification
        try:
            post = await Post.get_or_none(id=settings.notification_post_id)
            await cls.send_content_to_users(bot=bot, broadcaster_post=post)
        except Exception as e:
            logger.error(f'Error while sending daily notification', exc_info=e)


    @classmethod
    async def start_event_loop(cls):
        logger.info('Broadcaster started')
        while True:
            try:
                await cls.__create_orders_for_mails()
            except Exception as e:
                logger.error(f'check_and_send_mails error', exc_info=e)

            try:
                active_orders = await Dispatcher.filter(send_at__lte=datetime.now()).all()
                logger.info(f'active_orders: {active_orders}')

            except Exception as e:
                logger.error(f'get active orders error', exc_info=e)
                continue

            index = 0
            futures = []
            try:
                if active_orders:
                    async with asyncio.TaskGroup() as tg:
                        while index < len(active_orders) or futures:
                            # start order work
                            if (len(futures) < settings.mailing_batch_size) and (index < len(active_orders)):
                                futures.append(tg.create_task(cls.order_work(active_orders[index])))
                                logger.info(
                                    f'Create order: '
                                    f'order_id={active_orders[index].id} '
                                    f'post_id={active_orders[index].post_id} '
                                )
                                index += 1

                            ind_x = 0
                            for i, _f in enumerate(reversed(futures)):
                                if _f.done():
                                    _f.cancel()
                                    del futures[len(futures) - i - 1 + ind_x]
                                    ind_x += 1
                            await asyncio.sleep(0.5)
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f'Broadcaster main loop async creating tasks error', exc_info=e)
                continue

            await asyncio.sleep(settings.broadcaster_sleep)


    @classmethod
    async def __create_orders_for_mails(cls):
        cities = await CitiesForParser.all()
        if not cities:
            return

        tz = pytz.timezone('Europe/Moscow')
        current_date = datetime.now(tz)

        for city in cities:
            # delete all active orders for cities if is_turn=False
            if not city.is_turn:
                await Dispatcher.filter(city_id=city.id).delete()
                continue

            # delete all active orders if city configuration was edited 20 seconds ago
            if city.updated_at >= current_date - timedelta(seconds=10) and not city.was_sent:
                await Dispatcher.filter(city_id=city.id).delete()

            # check if there are already any orders for notifications, exit if there are any
            orders_for_cities = await Dispatcher.filter(city_id=city.id)
            if orders_for_cities:
                continue
            else:
                # we schedule only for future time
                send_at = current_date.replace(hour=city.hour, minute=city.minute, second=0, microsecond=0)
                if current_date > send_at:
                    send_at += timedelta(days=1)


                # create order for city
                await Dispatcher.create(
                    city_id=city.id,
                    send_at=send_at,
                )


async def main():
    await init()
    await Broadcaster.start_event_loop()


async def run_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(Broadcaster.send_notification,
                      trigger=CronTrigger(hour=settings.notification_hours, minute=settings.notification_minutes))

    scheduler.start()


async def run_tasks():
    broadcaster = asyncio.create_task(main())
    scheduler = asyncio.create_task(run_scheduler())
    await asyncio.gather(broadcaster, scheduler)


if __name__ == '__main__':
    asyncio.run(run_tasks())
