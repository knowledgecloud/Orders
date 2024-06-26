
from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def orders():
    """
    Orders robots
    Saves the order as a PDF.
    Saves screenshot of the robot.
    Embeds the screenshot of robot in PDF.
    Creates ZIP file.
    """

    open_website()
    download_csv()
    get_orders()
    archive_receipts()

def open_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_csv():
    """Downloads orders from given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def close_modal():
    """Closes the modal"""
    page = browser.page()
    page.click("button:text('OK')")

def get_orders():
    """read csv file into table"""    
    table = Tables()
    orders = table.read_table_from_csv("orders.csv") 

    for order in orders:
        fill_form(order)


def fill_form(order):
    """Fills the order form with given details"""  
    page = browser.page()
    close_modal()

    page.select_option("#head", order["Head"])
    page.check(f"#id-body-" + order["Body"])
    page.fill(".form-control", order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#preview")
    page.click("#order")

    while not page.query_selector("#order-another"):
        page.click("#order")

    save_receipt_as_pdf(order["Order number"])

    page.click("#order-another")


def save_receipt_as_pdf(order_number):
    """Stores receipts to PDF and takes a screenshot of ordered robots"""  
    page = browser.page()

    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_file = f"output/{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, pdf_file)

    # screenshot
    robo = page.query_selector("#robot-preview-image")
    screenshot = f"output/{order_number}.png"
    robo.screenshot(path=screenshot)

    embed_screenshot(screenshot, pdf_file)


def embed_screenshot(screenshot, pdf_file):
    """Embeds screenshot to thge receipt PDF""" 
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)
    
    
def archive_receipts():
    """Archives outputs""" 
    folder = Archive()
    folder.archive_folder_with_zip('output', 'output/ordes.zip', include='*.pdf')
