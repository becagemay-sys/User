"""Command /start dan keyboard menu utama."""

from __future__ import annotations

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import OWNER_ID
from database import get_or_create_user
from formatter import full_name, welcome_text
from logger import log, safe_handler


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
    """Daftarkan handler /start dan menu utama."""
    
    @client.on_message(filters.command("start") & filters.private, group=-100)
    @safe_handler
    async def start_handler(_client, message):
        """Handle /start command di private chat."""
        user = message.from_user
        if not user:
            return
        
        # Buat atau perbarui user record
        user_data = get_or_create_user(user.id, user.username, full_name(user))
        
        # Kirim reply dengan welcome text dan keyboard
        try:
            await message.reply(welcome_text(), reply_markup=main_keyboard())
        except Exception:
            log.exception("Gagal mengirim /start reply ke user %s.", user.id)
            return
        
        # Kirim notifikasi ke Owner jika user status masih pending
        # Jangan block reply jika notifikasi gagal
        if OWNER_ID and user_data and user_data.get("approval_status") == "pending":
            try:
                from plugins.approval import notify_owner
                await notify_owner(_client, user.id)
            except Exception:
                log.warning(
                    "Gagal mengirim notifikasi approval ke Owner untuk user %s.",
                    user.id,
                )

    @client.on_callback_query(filters.regex(r"^manager:home$"))
    @safe_handler
    async def start_menu_callback(_client, query):
        """Handle manager:home callback untuk kembali ke menu utama."""
        await query.answer()
        if not query.message:
            return
        try:
            await query.message.edit(welcome_text(), reply_markup=main_keyboard())
        except Exception:
            log.exception("Gagal edit menu utama untuk user %s.", query.from_user.id if query.from_user else "unknown")

    log.info("✓ Handler /start dan menu utama terdaftar.")
