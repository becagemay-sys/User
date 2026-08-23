"""Command /start dan keyboard menu utama."""

from __future__ import annotations

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import OWNER_ID
from database import get_or_create_user
from formatter import full_name, welcome_text
from logger import log, safe_handler
from plugins.approval import notify_owner


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📲 Minta Akses", callback_data="manager:request")],
            [
                InlineKeyboardButton("👤 Akun Saya", callback_data="manager:account"),
                InlineKeyboardButton("📖 Panduan", callback_data="manager:guide"),
            ],
            [InlineKeyboardButton("ℹ️ Tentang", callback_data="manager:about")],
        ]
    )


def home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏠 Menu Utama", callback_data="manager:home")]]
    )


def setup(client):
    @client.on_message(filters.command("start") & filters.private, group=-100)
    @safe_handler
    async def start_handler(client, message):
        user = message.from_user
        if not user:
            return
        user_data = get_or_create_user(user.id, user.username, full_name(user))
        
        # Notifikasi Bot Manager tentang user baru yang join
        if OWNER_ID and user_data and user_data.get("approval_status") == "pending":
            await notify_owner(client, user.id)
        
        await message.reply(welcome_text(), reply_markup=main_keyboard())

    @client.on_callback_query(filters.regex(r"^manager:home$"))
    @safe_handler
    async def start_menu_callback(client, query):
        await query.answer()
        if not query.message:
            return
        await query.message.edit(welcome_text(), reply_markup=main_keyboard())

    log.info("✓ Handler /start dan menu utama terdaftar.")

