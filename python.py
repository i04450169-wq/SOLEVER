import asyncio
from playwright.async_api import async_playwright

# ====== املأ معلوماتك هنا ======
QUREO_USER = "ضع_اسم_المستخدم_هنا"
QUREO_PASS = "ضع_كلمة_المرور_هنا"
SOLUTIONS_URL = "https://qureoeg.com/qureo-solutions"
# ============================

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("[1] فتح صفحة تسجيل الدخول...")
        await page.goto("https://me-portal.qureo.education/login", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # محاولة إدخال اسم المستخدم وكلمة المرور
        # ملاحظة: محددات الحقول قد تتغير، وإذا فشلت، استخدم وضع التصحيح للتحقق من HTML
        username_input = page.locator('input[type="text"], input[name*="user"], input[id*="user"]').first
        password_input = page.locator('input[type="password"]').first

        if await username_input.count() > 0:
            await username_input.fill(QUREO_USER)
            await password_input.fill(QUREO_PASS)
            print("[2] تم إدخال معلومات الحساب")
        else:
            print("[!] لم يتم العثور على حقل اسم المستخدم، يرجى التحقق يدوياً")

        # محاولة النقر على زر تسجيل الدخول
        login_btn = page.locator('button:has-text("ログイン"), button:has-text("Login"), button[type="submit"]').first
        if await login_btn.count() > 0:
            await login_btn.click()
            print("[3] تم النقر على تسجيل الدخول")
        else:
            print("[!] لم يتم العثور على زر تسجيل الدخول، قد تحتاج إلى النقر يدوياً")

        await page.wait_for_timeout(5000)

        # التحقق من الصف: إذا ظهر خيار أولى ثانوي، انقر عليه
        print("[4] التحقق من خيارات الصف...")
        first_year = page.locator('text=اولی ثانوی, text=1年生, text=First Year').first
        if await first_year.count() > 0:
            await first_year.click()
            print("[5] تم اختيار أولى ثانوي")
            await page.wait_for_timeout(3000)
        else:
            print("[i] لم يتم العثور على خيار الصف، قد يكون الحساب محدداً مسبقاً أو أن الصفحة مختلفة")

        # محاولة استخراج محتوى JavaScript من الصفحة
        print("[6] محاولة استخراج محتوى JavaScript من الصفحة...")
        js_content = await page.locator('text=JavaScript, text=javascript, text=JS').all()
        if js_content:
            for item in js_content[:5]:
                print(f"  -> {await item.text_content()}")
        else:
            print("  [!] لم يتم العثور على محتوى JavaScript ظاهر مباشرة على الصفحة")

        # حفظ حالة الصفحة الحالية، لفحصها يدوياً
        await page.screenshot(path="qureo_after_login.png", full_page=True)
        print("[7] تم حفظ لقطة الشاشة: qureo_after_login.png")

        # فتح رابط الحلول (إذا كان يعمل)
        print(f"[8] محاولة فتح رابط الحلول: {SOLUTIONS_URL}")
        try:
            sol_page = await context.new_page()
            await sol_page.goto(SOLUTIONS_URL, wait_until="domcontentloaded", timeout=15000)
            await sol_page.wait_for_timeout(3000)
            sol_title = await sol_page.title()
            print(f"  -> عنوان الصفحة: {sol_title}")
            await sol_page.screenshot(path="solutions_page.png", full_page=True)
            print("[9] تم حفظ لقطة شاشة صفحة الحلول: solutions_page.png")
        except Exception as e:
            print(f"  [!] فشل فتح رابط الحلول: {e}")

        print("\n=== اكتمل التشغيل ===")
        print("يرجى التحقق من لقطات الشاشة qureo_after_login.png و solutions_page.png")
        print("إذا لم يتم العثور على حقول الإدخال أو الأزرار، أخبرني بما تراه على الشاشة، وسأعدل المحددات.")
        
        # إبقاء المتصفح مفتوحاً، حتى تتمكن من المتابعة يدوياً
        input("اضغط Enter للإغلاق...")
        await browser.close()

asyncio.run(main())
