from pyrogram import filters
from pyrogram.types import Message

from PURVIMUSIC import app
from PURVIMUSIC.utils import extract_user, int_to_alpha
from PURVIMUSIC.utils.database import (
    delete_authuser,
    get_authuser,
    get_authuser_names,
    save_authuser,
)
from PURVIMUSIC.utils.decorators import AdminActual, language
from PURVIMUSIC.utils.inline import close_markup
from config import BANNED_USERS, adminlist


@app.on_message(filters.command("auth", "") & filters.group & ~BANNED_USERS)
@AdminActual
async def auth(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text("لطفا دستور را به درستی وارد کنید")
    user = await extract_user(message)
    token = await int_to_alpha(user.id)
    _check = await get_authuser_names(message.chat.id)
    count = len(_check)
    if int(count) == 25:
        return await message.reply_text("حداکثر تعداد کاربران مجاز (25) به این گروه اضافه شده‌اند")
    if token not in _check:
        assis = {
            "auth_user_id": user.id,
            "auth_name": user.first_name,
            "admin_id": message.from_user.id,
            "admin_name": message.from_user.first_name,
        }
        get = adminlist.get(message.chat.id)
        if get:
            if user.id not in get:
                get.append(user.id)
        await save_authuser(message.chat.id, token, assis)
        return await message.reply_text(f"{user.mention} با موفقیت به لیست کاربران مجاز اضافه شد")
    else:
        return await message.reply_text(f"{user.mention} از قبل در لیست کاربران مجاز قرار دارد")


@app.on_message(filters.command("unauth", "") & filters.group & ~BANNED_USERS)
@AdminActual
async def unauthusers(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text("لطفا دستور را به درستی وارد کنید")
    user = await extract_user(message)
    token = await int_to_alpha(user.id)
    deleted = await delete_authuser(message.chat.id, token)
    get = adminlist.get(message.chat.id)
    if get:
        if user.id in get:
            get.remove(user.id)
    if deleted:
        return await message.reply_text(f"{user.mention} از لیست کاربران مجاز حذف شد")
    else:
        return await message.reply_text(f"{user.mention} در لیست کاربران مجاز وجود ندارد")


@app.on_message(
    filters.command(["authlist", "authusers"], "") & filters.group & ~BANNED_USERS
)
@language
async def authusers(client, message: Message, _):
    _wtf = await get_authuser_names(message.chat.id)
    if not _wtf:
        return await message.reply_text("هیچ کاربر مجازی در این گروه وجود ندارد")
    else:
        j = 0
        mystic = await message.reply_text("در حال دریافت لیست کاربران مجاز...")
        text = f"لیست کاربران مجاز در {message.chat.title}:\n\n"
        for umm in _wtf:
            _umm = await get_authuser(message.chat.id, umm)
            user_id = _umm["auth_user_id"]
            admin_id = _umm["admin_id"]
            admin_name = _umm["admin_name"]
            try:
                user = (await app.get_users(user_id)).first_name
                j += 1
            except:
                continue
            text += f"{j}➤ {user}[<code>{user_id}</code>]\n"
            text += f"   توسط ادمین: {admin_name}[<code>{admin_id}</code>]\n\n"
        await mystic.edit_text(text, reply_markup=close_markup(_))
