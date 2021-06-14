import json

from googleapiclient.discovery import build
from google.oauth2 import service_account
import re

import requests
from lxml import html

start_row = 533
end_row = 860


def read_sheet():
	SERVICE_ACCOUNT_FILE = '/keys.json'
	SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

	credentials = service_account.Credentials.from_service_account_file(
		SERVICE_ACCOUNT_FILE, scopes=SCOPES)

	SPREADSHEET_ID = '10m479W16sWnC0Of-1_b3BneB2xkYlrtWeUxHxn073t8'

	service = build('sheets', 'v4', credentials=credentials)

	sheet = service.spreadsheets()
	result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'US!F{start_row}:{end_row}').execute()

	values = result.get('values', [])
	return values


def create_file(row, name, data_dict):
	with open(f'json/USA/{str(row) + name}.json', 'w', encoding="utf-8") as outfile:
		json.dump(data_dict, outfile, indent=4, ensure_ascii=False)


def read_git():
	values = read_sheet()
	row = start_row
	for link in values:
		if link:
			try:
				name = link[0].split('/')[-1]
				if name.isalpha():
					base_git = link[0][:-len(name)]
					url = f'{base_git}{name}/blob/main/{name}/spiders/spider.py'
					response = requests.get(url)
					tree = html.fromstring(response.text)
					table = tree.xpath('//table')
					content = table[0].text_content()

					try:
						start_urls = re.findall(r"start_urls\s=\s\['(.*)'\]", content)[0]
					except:
						start_urls = ''
					try:
						articles_xpath = re.findall(r"post_links\s=\sresponse.xpath\('(.*)\/@href", content)[0].replace(
							'"', "'")
					except:
						articles_xpath = ''
					try:
						title_xpath = re.findall(r"title\s=\sresponse.xpath\('(.*)\/", content)[0].replace('"', "'")
					except:
						title_xpath = ''
					try:
						body_xpath = re.findall(r"description\s=\sresponse.xpath\('(.*)//text", content)[0].replace('"',
						                                                                                            "'")
					except:
						body_xpath = ''
					try:
						pubdate_xpath = re.findall(r"date\s=\sresponse.xpath\('(.*)/text", content)[0].replace('"', "'")
					except:
						pubdate_xpath = ''

					data_dict = {
						"scrapy_arguments": {
							"start_urls": start_urls,
							"articles_xpath": articles_xpath,
							"title_xpath": title_xpath,
							"body_xpath": body_xpath,
							"pubdate_xpath": pubdate_xpath
						},
						"scrapy_settings": {
							"USER_AGENT": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
						}
					}
					create_file(row, name, data_dict)

			except:
				pass
		row += 1


read_git()
