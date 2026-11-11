# Jadidlar Telegram boti

Bot jadid ma’rifatparvarlari haqida qisqa ma’lumot, menyu va sodda viktorina taqdim etadi.

## Ishga tushirish (Windows PowerShell)

1. BotFather’da oshkor bo‘lgan eski tokenni bekor qiling va yangi token yarating.
2. `.env.example` faylidan nusxa olib, nusxasini `.env` deb nomlang.
3. `.env` ichidagi `BOT_TOKEN` qiymatini yangi token bilan almashtiring. Tokenni kodga yozmang va hech kimga yubormang.
4. Virtual muhit yarating va uni faollashtiring:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python main.py
   ```

5. Telegram’da botga `/start` yuboring. `/help` buyrug‘i botdan foydalanish bo‘yicha qisqa yordam beradi.

`.env` `.gitignore` ro‘yxatida; token xavfsizligi uchun uni repozitoriyga qo‘shmang.

## Vercel'ga joylash

Vercel loyiha sozlamalarida **Root Directory** repozitoriy ildizi (`./`) bo‘lishi
kerak;
**Environment Variables** bo‘limida production muhiti uchun `BOT_TOKEN`
bo‘lishi kerak. `api/app.py` Vercel uchun FastAPI ilovasini eksport qiladi,
Telegram yangilanishlari esa `/api/webhook` va `/webhook` manzillarida qabul
qilinadi. Domenni webhook sifatida ulashdan oldin deploy muvaffaqiyatli
bo‘lganini va endpoint `POST` so‘roviga javob berishini tekshiring.
