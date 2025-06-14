from camoufox.sync_api import Camoufox

with Camoufox(
        headless=False,                # you already have this
        persistent_context=True,       # keep settings & addons
        user_data_dir="~/camoufox-profile",
        enable_cache=True              # enables history/back/forward
) as browser:
    page = browser.new_page()
    page.goto("about:blank")
