# -*- coding: utf-8 -*-
import requests
import time
import random
import math
import argparse
import webbrowser
from lxml import etree
from fake_useragent import UserAgent

ua = UserAgent()


def get_cookie():
    with open('cookie', 'r') as f:
        cookies = {}
        for line in f.read().split(';'):
            name, value = line.strip().split('=', 1)  # 1代表只分割一次
            cookies[name] = value
        return cookies


url_format = "http://{0}.lianjia.com/"

current_section_name = ""


def spider_get_xml(url):
    try:
        print("processing {}".format(url))
        time.sleep(random.uniform(0.5, 1.6))
        ret = requests.get(url, headers={'User-Agent': ua.chrome}, cookies=get_cookie(), timeout=5)
        return etree.HTML(ret.content)
    except Exception as e:
        return etree.HTML("<None/>")


def get_regions(suffix):
    while True:
        page = spider_get_xml(root_url + suffix)
        hrefs = page.xpath("//div[@data-role='ershoufang']//a")

        # for href in hrefs:
        #    print(href.attrib['href'],href.text)
        regions = {}
        for href in hrefs:
            regions[href.attrib['href']] = href.text
        if len(regions) > 0:
            return regions

            # return [x.attrib['href'] for x in hrefs]


def get_section(url):
    while True:
        page = spider_get_xml(root_url + url)
        hrefs = page.xpath("//div[@data-role='ershoufang']/div[2]//a")

        sections = {}
        for href in hrefs:
            sections[href.attrib['href']] = href.text
        if len(sections) > 0:
            return sections


def process_onsell_section(url):
    while True:
        page = spider_get_xml(root_url + url)
        data = page.xpath("//*[@class='total fl']/span")
        if len(data) > 0:
            total_num = int(data[0].text)
            page_num = int(math.ceil(total_num / 30))
            # print('{0} has {1} house(s)'.format(section_name, total_num))
            break

    for i in range(1, page_num + 1):
        process_onsell_page(root_url + url + "pg{0}/".format(i))
        """
        hrefs = page.xpath("//div[@page-data]")
        if len(hrefs) > 0:
            page_info = hrefs[0].attrib['page-data']
            page_num = page_info.split(',')[0].split(':')[1]
            print('{0} has {1} page(s)'.format(section_name, page_num))
            return
        """


def process_onsell_page(url):
    while True:
        page = spider_get_xml(url)
        data = page.xpath("//h2[@class='total fl']/span")
        if len(data) > 0:
            break

    house_refs = page.xpath("//ul[@class='sellListContent']/li")
    for house_ref in house_refs:
        process_onsell_house(house_ref)
        # process_onsell_unit(house_ref.attrib['href'])
        # print(house_ref.attrib['href'])


def process_onsell_house(house_ref):
    try:

        house_url = house_ref.xpath("div[@class='info clear']/div[@class='title']/a")[0].attrib['href']
        house_info = house_ref.xpath("div[@class='info clear']//div[@class='houseInfo']/a")[0]
        data = [x.strip() for x in house_info.tail.split('|')]
        huxing, area, face = data[1:4]
        area = area[:-2]
        xiaoqu = house_info.text.strip()
        tax_info = house_ref.xpath("div[@class='info clear']//span[@class='five']")
        if len(tax_info) > 0:
            tax = tax_info[0].text
        else:
            tax = ""
        price = float(house_ref.xpath(".//div[@class='totalPrice']/span")[0].text)
        unit_price = float(house_ref.xpath(".//div[@class='unitPrice']")[0].attrib["data-price"])
        info = "{0}\t{1:g}\t{2:g}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}".format(house_url, price, unit_price, huxing, area,
                                                                        face, current_section_name, xiaoqu, tax)
        print(info)
    except Exception as e:
        pass


def process_onsell_unit(url):
    for i in range(0, 16):
        page = spider_get_xml(url)
        data = page.xpath("//div[@class='price ']/span[1]")
        if len(data) > 0:
            break

    if len(data) == 0:
        print("failed to process {}".format(url))
        return
    price = float(data[0].text)
    unit_price = float(page.xpath("//span[@class='unitPriceValue']")[0].text)
    houseinfo = page.xpath("//div[@class='houseInfo']//div[@class='mainInfo']")

    huxing = houseinfo[0].text
    face = houseinfo[1].text
    area = houseinfo[2].text[:-2]

    xiaoqu = page.xpath("//div[@class='aroundInfo']/div[@class='communityName']/a")[0].text
    region = page.xpath("//div[@class='aroundInfo']/div[@class='areaName']//a")[0].text
    section = page.xpath("//div[@class='aroundInfo']/div[@class='areaName']//a")[1].text

    info = "{0}\t{1:g}\t{2:g}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}".format(url, price, unit_price, huxing, face, area, region,
                                                                    section, xiaoqu)
    print(info)


def process_traded_section(url):
    while True:
        page = spider_get_xml(root_url + url)
        data = page.xpath("//*[@class='total fl']/span")
        if len(data) > 0:
            total_num = int(data[0].text)
            page_num = int(math.ceil(total_num / 30))
            # print('{0} has {1} house(s)'.format(section_name, total_num))
            break

    for i in range(1, page_num + 1):
        process_traded_page(root_url + url + "pg{0}/".format(i))


def process_traded_page(url):
    # record_url(url)
    # return
    index = 16
    while index > 0:
        page = spider_get_xml(url)
        data = page.xpath("//*[@class='total fl']/span")
        if len(data) > 0:
            break
        index -= 1
        open_browser(url)
        input("看看弹出的浏览器信息，处理之后按任意键继续爬")

    if index == 0:
        print("get stuck in page {}", url)
        return
    house_refs = page.xpath("//ul[@class='listContent']/li")
    for house_ref in house_refs:
        process_traded_house(house_ref)


def process_traded_house(house_ref):
    try:
        title = house_ref.xpath("div[@class='info']/div[@class='title']/a")[0]
        house_url = title.attrib['href']
        xiaoqu, huxing, area = title.text.split(' ')
        area = area[:-2]
        deal_date = house_ref.xpath(".//div[@class='dealDate']")[0].text
        price = float(house_ref.xpath(".//div[@class='totalPrice']/span")[0].text)
        unit_price = float(house_ref.xpath(".//div[@class='unitPrice']/span")[0].text)
        info = "{0}\t{1:g}\t{2:g}\t{3}\t{4}\t{5}\t{6}\t{7}".format(house_url, price, unit_price, huxing, area,
                                                                   current_section_name, xiaoqu, deal_date)
        record_data(info)
    except Exception as e:
        pass


def record_data(data):
    with open("data.txt", 'a') as f:
        line = data + '\n'
        f.write(line)


def record_url(url):
    f = open('url_to_process.dat', 'a')
    line = url + '\n'
    f.write(line)
    f.close()


def open_browser(url):
    # MacOS
    chrome_path = 'open -a /Applications/Google\ Chrome.app %s'

    # Windows
    # chrome_path = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe %s'

    # Linux
    # chrome_path = '/usr/bin/google-chrome %s'

    webbrowser.get(chrome_path).open(url)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--city", type=str,
                        help="城市拼音首字母，bj for 北京", default="cd")
    parser.add_argument("-t", "--type", type=str, choices=["onsell", "traded"],
                        help="在售房源或者历史成交记录", default="traded")
    args = parser.parse_args()
    if args.type == 'traded':
        suffix = "chengjiao"
        processor = process_traded_section
    else:
        suffix = "ershoufang"
        processor = process_onsell_section

    root_url = url_format.format(args.city)
    # process_onsell_section("/ershoufang/cuiyuan/")
    # process_traded_page("http://hz.lianjia.com/chengjiao/shenhua/pg15/")
    regions = get_regions(suffix)
    # print(regions)
    sections = {}
    for region in regions:
        # print("sections in {0} is ".format(regions[region]), )
        sections.update(get_section(region))

    # print(sections)

    for section in sections:
        current_section_name = sections[section]
        processor(section)
