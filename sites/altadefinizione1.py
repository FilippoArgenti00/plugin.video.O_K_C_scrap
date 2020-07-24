#!/usr/bin/python

from hosts import hosts
from requests import get
from sys import version_info
from bs4 import BeautifulSoup

from scrapers.utils import (
	headers, m_identify,
	decode_middle_encrypted
)

host = "https://altadefinizione.group/"
excapes = ["Back", "back", ""]

if version_info.major < 3:
	input = raw_input

def search_film(film_to_search):
	search_url = "{}?s={}".format(host, film_to_search)

	body = get(
		search_url,
		headers = headers,
		timeout = 8
	).text

	parsing = BeautifulSoup(body, "html.parser")

	json = {
		"results": []
	}

	how = json['results']

	for a in parsing.find_all("div", class_ = "col-lg-4 col-md-4 col-xs-4"):
		image = a.find("img").get("src")
		link = a.find("a").get("href")
		title = a.find("h2").get_text()

		data = {
			"title": title,
			"link": link,
			"image": image
		}

		how.append(data)

	return json

def search_mirrors(film_to_see):
	body = get(film_to_see).text
	parse = BeautifulSoup(body, "html.parser")

	film_id_url = (
		parse
		.find("iframe", id = "iframeVid")
		.get("src")
		.split("&")[0]
	)

	body = get(film_id_url).text
	parse = BeautifulSoup(body, "html.parser")

	parsing = (
		parse
		.find("ul", class_ = "buttons-list d-flex")
		.find_all("li")
	)

	json = {
		"results": []
	}

	datas = json['results']

	for a in parsing:
		usha = a.find("a")
		quality = a.find("a").get_text()
		link = usha.get("href")
		body = get(link).text
		parse = BeautifulSoup(body, "html.parser")

		mirrors = (
			parse
			.find_all("ul", class_ = "buttons-list d-flex")[1]
			.find_all("li")
		)

		for b in mirrors:
			c = b.find("a")
			link = c.get("href")
			mirror = c.get_text().lower()
			body = get(link).text
			parse = BeautifulSoup(body, "html.parser")

			link_enc = (
				parse
				.find("iframe")
				.get("custom-src")
			)

			if not link_enc:
				continue

			link_mirror = m_identify(
				decode_middle_encrypted(link_enc)
			)

			try:
				hosts[mirror]

				data = {
					"mirror": mirror,
					"quality": quality,
					"link": link_mirror
				}

				datas.append(data)
			except KeyError:
				pass

	return json

def identify(info):
	link = info['link']
	mirror = info['mirror']
	return hosts[mirror].get_video(link)

def menu():
	while True:
		try:
			ans = input("Type the film title which you would search: ")
			result = search_film(ans)['results']

			while True:
				for a in range(
					len(result)
				):
					print(
						"%d): %s" % 
						(
							a + 1,
							result[a]['title']
						)
					)

				ans = input("What film do you want to see?: ")

				if ans in excapes:
					break
					
				index = int(ans) - 1
				film_to_see = result[index]['link']
				datas = search_mirrors(film_to_see)['results']

				while True:
					for a in range(
						len(datas)
					):
						print(
							"%s): %s (%s)"
							% (
								a + 1,
								datas[a]['mirror'],
								datas[a]['quality']
							)
						)

					ans = input("What film do you want to see?: ")

					if ans in excapes:
						break

					index = int(ans) - 1
					video = identify(datas[index])
					print(video)
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	menu()