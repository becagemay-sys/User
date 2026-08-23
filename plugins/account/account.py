"""Callback menu Akun Saya."""

from __future__ import annotations

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import OWNER_ID
from database import get_or_create_user
from formatter import account_text, full_name
from logger import safe_handler
from plugins.approval import notify_owner


def account_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏠 Menu Utama", callback_data="manager:home")]]
    )


def setup(client):
    @client.on_callback_query(filters.regex(r"^manager:account$"))
    @safe_handler
    async def account_callback(client, query):
        await query.answer()
        if not query.message or not query.from_user:
            return
        user = query.from_user
        data = get_or_create_user(user.id, user.username, full_name(user))
        
        # Notifikasi Bot Manager tentang user yang mengakses akun mereka
        # Jika status masih pending (belum disetujui), kirim notifikasi approval
        if OWNER_ID and data and data.get("approval_status") == "pending":
            await notify_owner(client, user.id)
        
        await query.message.edit(account_text(data), reply_markup=account_keyboard())
