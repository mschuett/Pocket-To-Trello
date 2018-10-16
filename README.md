# Pocket-To-Trello
A utility to create cards in a reading board in Trello out of new items saved to Pocket

## About this Fork

I forked the original version from [OrBin/Pocket-To-Trello](https://github.com/OrBin/Pocket-To-Trello)
to adapt it for my own workflow for reblogging interesting items:
- I use a specific tag `reblog` in Pocket,
- I want Pocket-To-Trello to copy those items to Trello,
- After an item is copied it is archived in Pocket (so be careful when testing this version, as it will modify your Pocket list).

Other small changes:
- Copy Pocket's tags as Trello labels,
- Copy an item's first image (as used in Pocket) to the Trello card,
- Do not add the Pocket URL as attachment.

## Usage

### Installing requirements
```
pip install -r requirements.txt
```

### Get Pocket consumer key
[Create a new Pocket app](https://getpocket.com/developer/apps/new) with "Retrieve" permission and save the generated consumer key for later use.

### Get Trello API key
Visit [here](https://trello.com/app-key) to get your Trello API key and save it for later use.

### Creating a configuration file
A configuration file `config.json` should be placed in the same directory as the code files.

Here is an example of how the initial configuration file should look:
```
{
  "authentication": {
    "pocket_consumer_key": "YOUR-POCKET-CONSUMER-KEY",
    "trello_api_key": "YOUR-TRELLO-API-KEY",
  },
  "pocket_last_checked": 0,
  "trello_list_id": "YOUR-TRELLO-LIST-ID"
}
```

### Authorizing with Pocket and Trello (Should be done only once)
Authorize with Pocket:
```
python authorize_pocket.py
```
Authorize with Trello:
```
python authorize_trello.py
```

### Run
```
python main.py
```

### (Optional) Add to cron
You can create a cron job with the following configuration to run the app every 10 minutes:
```
*/10 * * * * python /path/to/repository/Pocket-To-Trello/main.py
```

## External packages
* [requests](http://docs.python-requests.org/en/master/)
* [py-trello](https://github.com/sarumont/py-trello)
* [pocket](https://github.com/tapanpandita/pocket)
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
