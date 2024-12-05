SEARCH_BUTTON = "//a[contains(text(), 'Search')]"
PROFILE_NAME_INPUT = "//*[@placeholder='Profile name or number']"
PROFILE_DROPDOWN_OPTION = "//li[a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{company_name}')]]"
FILING_TYPE_INPUT = "//label[span[text()='Filing type']]//following::span[contains(@class, 'select2-container')][1]//textarea"
FILING_TYPE_OPTION = "//li[contains(text(), 'Annual report')]"
FROM_DATE_INPUT = "//div[label[text()='From date']]//following::input[@name = 'SubmissionDate']"
TO_DATE_INPUT = "//div[label[text()='To date']]//following::input[@name = 'SubmissionDate2']"
SEARCH_SUBMIT_BUTTON = "//button//span[contains(text(), 'Search')]"
DOWNLOAD_PDF = "//table//div//span[contains(text(), 'Annual report')]"
PROCESSING_TEXT = "//div[@role='alert' or contains(@class,'alert')]"