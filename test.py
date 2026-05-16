from pathlib import Path
from playwright.sync_api import sync_playwright, Page
from config import LOGIN_URL, ADMIN_LOGIN_ID, ADMIN_PASSWORD


TEST_CLIENT_SEARCH = "leela"
TEST_CLIENT_NAME = "Leelavathi Choudhary"


def clean_view_for_pdf(page: Page, active_panel_selector: str):
    page.evaluate(
        """(activePanelSelector) => {
            const hideSelectors = [
                '#dashHeader',
                '#adminTabs',
                '#logoutBtn',
                '#backToFamily'
            ];

            hideSelectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => el.style.display = 'none');
            });

            const userTabs = document.querySelector('#userTabs');
            if (userTabs) userTabs.style.display = 'none';

            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.style.display = 'none';
            });

            const activePanel = document.querySelector(activePanelSelector);
            if (activePanel) {
                activePanel.style.display = 'block';
                activePanel.style.visibility = 'visible';
            }

            document.querySelectorAll('.card').forEach(card => {
                const text = (card.innerText || '').trim();
                if (text.startsWith('Client Search')) {
                    card.style.display = 'none';
                }
            });

            document.body.style.background = '#ffffff';
            document.body.style.padding = '0';
        }""",
        active_panel_selector
    )


def export_current_view_pdf(page: Page, output_path: str):
    page.emulate_media(media="screen")
    page.pdf(
        path=output_path,
        format="A4",
        landscape=True,
        print_background=True,
        margin={"top": "8mm", "right": "8mm", "bottom": "8mm", "left": "8mm"}
    )


def open_client_from_search(page: Page, search_text: str, client_name: str):
    page.locator("#adminClientSearch").wait_for(state="visible", timeout=240_000)
    page.locator("#adminClientSearch").fill(search_text)

    client_row = page.locator(".admin-client-row", has_text=client_name).first
    client_row.wait_for(state="visible", timeout=240_000)
    client_row.click()


def generate_client_reports(page: Page, search_text: str, client_name: str, output_dir: str):
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_name = "".join(c if c.isalnum() else "_" for c in client_name).strip("_")
    performance_pdf = str(out_dir / f"{safe_name}_performance.pdf")
    profitbook_pdf = str(out_dir / f"{safe_name}_profitbook.pdf")

    open_client_from_search(page, search_text=search_text, client_name=client_name)

    page.locator('#userTabs .tab[data-tab="performance"]').wait_for(state="visible", timeout=240_000)

    page.locator('#userTabs .tab[data-tab="performance"]').click()
    page.locator("#tab-performance").wait_for(state="visible", timeout=240_000)

    if page.locator("#tab-performance .expand-all").count() > 0 and page.locator("#tab-performance .expand-all").is_visible():
        page.locator("#tab-performance .expand-all").click()

    page.wait_for_timeout(1500)
    clean_view_for_pdf(page, "#tab-performance")
    export_current_view_pdf(page, performance_pdf)

    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    page.locator("#adminClientSearch").wait_for(state="visible", timeout=240_000)
    open_client_from_search(page, search_text=search_text, client_name=client_name)

    page.locator('#userTabs .tab[data-tab="profit"]').wait_for(state="visible", timeout=240_000)
    page.locator('#userTabs .tab[data-tab="profit"]').click()
    page.locator("#tab-profit").wait_for(state="visible", timeout=240_000)

    if page.locator("#tab-profit .expand-all").count() > 0 and page.locator("#tab-profit .expand-all").is_visible():
        page.locator("#tab-profit .expand-all").click()

    page.wait_for_timeout(1500)
    clean_view_for_pdf(page, "#tab-profit")
    export_current_view_pdf(page, profitbook_pdf)

    return {
        "performance_pdf": performance_pdf,
        "profitbook_pdf": profitbook_pdf
    }


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(240_000)

        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=240_000)

        page.get_by_placeholder("Login-Id").fill(ADMIN_LOGIN_ID)
        page.locator("#password").fill(ADMIN_PASSWORD)
        page.locator("#loginBtn").click()

        clients_tab = page.locator('#adminTabs .tab[data-admin="clients"]')
        clients_tab.wait_for(state="visible", timeout=240_000)
        clients_tab.click()

        page.wait_for_function(
            """() => {
                const bodyText = document.body ? document.body.innerText : "";
                return !bodyText.includes("Loading clients...");
            }""",
            timeout=240_000
        )

        page.locator("#admin-clients").wait_for(state="visible", timeout=240_000)
        page.locator("#adminClientSearch").wait_for(state="visible", timeout=240_000)

        reports = generate_client_reports(
            page=page,
            search_text=TEST_CLIENT_SEARCH,
            client_name=TEST_CLIENT_NAME,
            output_dir="output/email_reports/leela"
        )

        print(reports)
        browser.close()


if __name__ == "__main__":
    main()