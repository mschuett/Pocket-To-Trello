import sys
import json
import requests
import os
import logging
import itertools
from logging.handlers import RotatingFileHandler
from pocket import Pocket
from datetime import datetime
from bs4 import BeautifulSoup
from trello import TrelloClient


CONFIG_FILE_NAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
LOG_FILE_NAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log.txt')
AUTH_DATA_KEY = 'authentication'


# Enable logging
file_handler = RotatingFileHandler(
    LOG_FILE_NAME, maxBytes=(1048576 * 5), backupCount=7
)
console_handler = logging.StreamHandler()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers=[file_handler, console_handler])
logger = logging.getLogger(__name__)

# Reading configuration and authentication data
with open(CONFIG_FILE_NAME, 'r') as conf_file:
    conf_data = json.load(conf_file)
auth_data = conf_data[AUTH_DATA_KEY]

# Logging in to Pocket
pocket_consumer_key = conf_data[AUTH_DATA_KEY]['pocket_consumer_key']
pocket_client = Pocket(conf_data[AUTH_DATA_KEY]['pocket_consumer_key'],
                       conf_data[AUTH_DATA_KEY]['pocket_user_credentials']['access_token'])
logger.info('Logged in to Pocket')

# Logging in to Trello
trello_client = TrelloClient(
    api_key=conf_data[AUTH_DATA_KEY]['trello_api_key'],
    token=conf_data[AUTH_DATA_KEY]['trello_token']
)
logger.info('Logged in to Trello')
trello_list = trello_client.get_list(conf_data['trello_list_id'])
trello_board = trello_list.board
trello_labels = {}
for label in trello_board.get_labels():
    label.fetch()
    trello_labels[label.name] = label
logging.debug('Labels: %s', trello_labels)

trello_label_color_generator = itertools.cycle([
    "green", "yellow", "orange", "red", "purple",
    "blue", "sky", "lime", "pink", "black"])


now_timestamp = int(datetime.now().timestamp())
pocket_tag = conf_data['pocket_tag'] if 'pocket_tag' in conf_data else None
pocket_state = conf_data['pocket_state'] if 'pocket_state' in conf_data else 'all'

new_pocket_items, _ = pocket_client.get(state=pocket_state, detailType='complete', tag=pocket_tag)
logger.info('Fetched new Pocket items')

if len(new_pocket_items['list']) == 0:
    logger.info('No new items.')
    sys.exit(0)

for pocket_item_id, pocket_item_data in new_pocket_items['list'].items():
    if pocket_item_data['status'] == '0':
        page_url = pocket_item_data['given_url']
        logger.info('Found item %s', page_url)

        # Getting page title
        if page_url.endswith('.pdf'):
            page_title = page_url.split('/')[-1].split('.')[0]
        else:
            try:
                with requests.get(page_url) as page_response:
                    parsed_page = BeautifulSoup(page_response.text, 'html.parser')
                page_title = parsed_page.title.text
            except:
                page_title = page_url

        card = trello_list.add_card(name=page_title,
                                    desc=pocket_item_data['excerpt'])
        logger.info('Created card \'%s\'', page_title)
        pocket_item_url = 'https://getpocket.com/a/read/%s' % pocket_item_id
        card.attach(url=page_url)
        logger.info('Attached link %s to item', page_url)
        if pocket_item_data['has_image'] == '1':
            pocket_item_image_url = pocket_item_data['image']['src']
            card.attach(url=pocket_item_image_url)
            logger.info('Attached img %s to item', pocket_item_image_url)
        for tag in pocket_item_data["tags"].keys():
            # ignore marker tag
            if pocket_tag and tag == pocket_tag:
                continue
            # create new label
            if tag not in trello_labels:
                label_color = next(trello_label_color_generator)
                label = trello_board.add_label(tag, label_color)
                trello_labels[tag] = label
            card.add_label(trello_labels[tag])

        pocket_client.archive(pocket_item_id).commit()
        logger.info('Archived item %s', page_url)


conf_data['pocket_last_checked'] = now_timestamp
with open(CONFIG_FILE_NAME, 'w') as conf_file:
    json.dump(conf_data, conf_file, indent=2)
