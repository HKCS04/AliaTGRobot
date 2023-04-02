import os
import logging

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
import random
from utils import Media
from info import START_MSG, CHANNELS, ADMINS, INVITE_MSG

logger = logging.getLogger(__name__)

force_channel = "SC_Linkzz"

@Client.on_message(filters.command('start'))
async def start(client, message):
    if force_channel:
        try:
            user = await client.get_chat_member(force_channel, message.from_user.id)
            if user.status == "kicked out":
                await message.reply_text("You Are Banned")
                return
        except UserNotParticipant :
            await message.reply_text(
                text="PLEASE SUBSCRIBE MY CHANNEL TO USE ME DEAR 😁",
                reply_markup=InlineKeyboardMarkup( [[
                 InlineKeyboardButton("⚡️𝘾𝙃𝘼𝙉𝙉𝙀𝙇⚡️", url=f"t.me/{force_channel}")
                 ]]
                 )
            )
            return
    await message.reply_photo(
        photo=random.choice(PIC),
        caption=f"""𝗛𝗘𝗟𝗟𝗢 {message.from_user.mention}
        
𝗠𝗬 𝗡𝗔𝗠𝗘 𝗜𝗦 𝗔𝗟𝗜𝗔 𝗕𝗛𝗔𝗧𝗧, 𝗬𝗢𝗨 𝗖𝗔𝗡 𝗖𝗔𝗟𝗟 𝗠𝗘 𝗔𝗦 𝗔 𝗣𝗢𝗪𝗘𝗥𝗙𝗨𝗟 𝗠𝗢𝗩𝗜𝗘 𝗦𝗘𝗔𝗥𝗖𝗛 𝗕𝗢𝗧 😎

𝗜 𝗖𝗔𝗡 𝗢𝗡𝗟𝗬 𝗣𝗥𝗢𝗩𝗜𝗗𝗘 𝗙𝗔𝗡𝗧𝗔𝗦𝗬 𝗠𝗢𝗩𝗜𝗘𝗦 😁

𝗜𝗧 𝗜𝗦 𝗘𝗔𝗦𝗬 𝗧𝗢 𝗨𝗦𝗘 𝗠𝗘 𝗝𝗨𝗦𝗧 𝗖𝗟𝗜𝗖𝗞 𝗕𝗘𝗟𝗢𝗪 𝗦𝗘𝗔𝗥𝗖𝗛 𝗕𝗨𝗧𝗧𝗢𝗡 𝗔𝗡𝗗 𝗘𝗡𝗝𝗢𝗬 😍

𝗖𝗥𝗘𝗔𝗧𝗘𝗗 & 𝗠𝗔𝗜𝗡𝗧𝗔𝗜𝗡𝗘𝗗 𝗕𝗬 : @SC_Linkzz""",
        reply_markup=InlineKeyboardMarkup( [[
            InlineKeyboardButton("SEARCH HERE 🔍", switch_inline_query_current_chat=''),
            ],[
            InlineKeyboardButton("CREATOR 👨‍💻", url="www.github.com/SOULTG/"),
            InlineKeyboardButton("⭕ OUR BOTS LINKS ⭕", url="t.me/SC_Linkzz")
            ]]
            )
        )


@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total(bot, message):
    """Show total files in database"""
    msg = await message.reply("Processing...⏳", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'📁 Saved files: {total}')
    except Exception as e:
        logger.exception('Failed to check total files')
        await msg.edit(f'Error: {e}')


@Client.on_message(filters.command('logger') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if not (reply and reply.media):
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    msg = await message.reply("Processing...⏳", quote=True)

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media:
            media.file_type = file_type
            break
    else:
        await msg.edit('This is not supported file format')
        return

    result = await Media.collection.delete_one({
        'file_name': media.file_name,
        'file_size': media.file_size,
        'file_type': media.file_type,
        'mime_type': media.mime_type
    })

    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        await msg.edit('File not found in database')
