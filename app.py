# import os
# import socket
# import ipaddress
# import requests
# import gradio as gr
# from dotenv import load_dotenv
# from bs4 import BeautifulSoup
# from urllib.parse import urlparse
# from openai import OpenAI



# load_dotenv(override=True)
# API_KEY = os.getenv("GROQ_API_KEY")
# BASE_URL = "https://api.groq.com/openai/v1"

# if not API_KEY:
#     print("No API_Key found, Please set the API_KEY.")
#     exit(1)
# elif API_KEY.strip() != API_KEY:
#     print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
# else:
#     print("API key found and looks good so far!")


# openai = OpenAI(api_key=API_KEY, base_url =BASE_URL)
# # ollama_with_openai = OpenAI(api_key = "ollama", base_url = "http://localhost:11434/v1")

# """
# Explanation of this code: https://chatgpt.com/share/686f8aed-a210-8007-970d-37906975fa4f
# """


# def is_safe_url(url):
#     try:
#         parsed = urlparse(url)
#         if parsed.scheme not in ["http", "https"] or parsed.netloc == "":
#             return False

#         host = parsed.hostname
#         ip = ipaddress.ip_address(socket.gethostbyname(host))
#         if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
#             return False
#     except Exception:
#         return False
#     return True


# class WebScraper:
#     """
#     A utility class to represent a Website that we have scraped, using Selenium, with extracted links.
#     """

#     def __init__(self, url):
#         if not is_safe_url(url):
#             raise ValueError("Invalid or unsafe URL")

#         self.url = url
#         self.title = "No title found"
#         self.text = ""
#         self.links = []
#         self.images = []
#         self.files = []
#         self.tables = []
#         self.scripts = []

#         # Setup Selenium
#         options = Options()
#         options.add_argument("--headless")
#         options.add_argument("--disable-gpu")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-extensions")
#         options.add_argument("--disable-blink-features=AutomationControlled")

#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#         try:
#             driver.set_page_load_timeout(60)
#             driver.get(url)
#             soup = BeautifulSoup(driver.page_source, "html.parser")

#             # Get title
#             self.title = soup.title.string.strip() if soup.title else "No title found"

#             # Remove irrelevant tags
#             if soup.body:
#                 for tag in soup.body(["script", "style", "input"]):
#                     tag.decompose()
#                 self.text = soup.body.get_text(strip=True)

#             # Extract all Images
#             all_images = [img.get("src") for img in soup.find_all("img") if img.get("src")]
#             self.images = all_images

#             # Extract all valid links
#             all_links = [a.get("href") for a in soup.find_all("a") if a.get("href") and is_safe_url(a.get("href"))]
#             self.links = all_links

#             # Extract all tables
#             all_tables = [table for table in soup.find_all("table")]
#             self.tables = all_tables

#             # Extract all scripts
#             all_scripts = [script for script in soup.find_all("script")]
#             self.scripts = all_scripts

#         except WebDriverException as e:
#             print(f"Error loading page with Selenium: {e}")
#         finally:
#             driver.quit()

#     def get_contents(self):
#         return f"-> Webpage Title:\n{self.title}\n\n\n-> Webpage Contents (limited text displayed up to 1000 characters):\n{self.text[:1000]}\n\n\n-> Links (limited to 20 links displayed):\n{self.links[:20]}\n\n\n-> Images:\n{self.images}\n\n\n-> Tables:\n{self.tables}\n\n\n-> Scripts:\n{self.scripts}\n"


# website = WebScraper("https://www.w3schools.com/")
# # print(web_scrapper.get_contents())
# print(website.get_contents())
# # web_scrapper.links


# system_prompt = (
#     "You are a highly intelligent assistant tasked with analyzing website content. "
#     "Your job is to extract and summarize the **core purpose** and **main content** of the site, ignoring any navigation bars, footers, cookie banners, or repetitive UI elements. "
#     "You excel at identifying meaningful information such as services offered, articles, announcements, product details, or business descriptions. "
#     "Always format your response in **markdown**, and present the summary in a clean, human-readable format that would make sense to someone who has never seen the site before."
# )


# def user_prompt_for(website):
#     user_prompt = (
#         f"## Website Title\n"
#         f"**{website.title}**\n\n"
#         f"## Instructions\n"
#         f"You are analyzing the contents of this website. Please provide a clear and concise markdown summary of the website’s purpose and content. "
#         f"Include any relevant details such as:\n"
#         f"- Services, products, or features offered\n"
#         f"- Blog posts, articles, or resources\n"
#         f"- News or announcements\n"
#         f"- Contact information, locations, or teams (if present)\n\n"
#         f"### Important:\n"
#         f"- **Ignore** navigation links, UI controls, cookie notices, or footer text.\n"
#         f"- Focus on meaningful, unique content visible to a visitor.\n\n"
#         f"## Website Content\n"
#         f"{website.text[:5000]}"
#     )
#     return user_prompt

# def summarize(url):
#     try:
#         website = WebScraper(url)
#         streamed_response = openai.chat.completions.create(
#             model="llama3-70b-8192",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt_for(website)}
#             ],
#             stream=True
#         )
#         # return display(Makrdown(streamed_response.choices[0].message.content))

#         result = ""
#         for chunk in streamed_response:
#             content_piece = chunk.choices[0].delta.content or ""
#             result += content_piece
#             cleaned_result = result.replace("```", "").replace("markdown", "")
#             yield cleaned_result  # <- Streaming to Gradio

#     except Exception as e:
#         yield f"[LLM Error] {e}"  # <- yield for Gradio to handle the stream



# view = gr.Interface(
#     fn=summarize,
#     inputs=gr.Textbox(label="Enter Website URL"),
#     outputs=gr.Markdown(label="Summary"),
#     title="Website Summarizer",
#     description="Paste a URL and get a clean summary of the site's purpose and content.",
#     flagging_mode="never"
# )

# view.launch(share=True)
