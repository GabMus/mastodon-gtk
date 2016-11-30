from mastodon import Mastodon
import os
import json

HOME = os.environ.get('HOME')
CONFIG_DIR = HOME + '/.config'
CONFIG_FILE = CONFIG_DIR + '/org.gabmus.mastodon-gtk.config.json'
CLIENT_CREDENTIALS_FILE = CONFIG_DIR + '/org.gabmus.mastodon-gtk.client-credentials'
USER_CREDENTIALS_FILE = CONFIG_DIR + '/org.gabmus.mastodon-gtk.user-credentials'

# TODO: create config file if doesn't exist

def read_config():
	"""Returns config file json"""
	try:
		config_f = open(CONFIG_FILE, 'r')
		configtxt = config_f.read()
		config_f.close()
	except ValueError:
		config_f.close()
		# TODO: create config file here
	return json.loads(configtxt)

class MastodonClient:
	def __init__(self):
		self.config_dict=read_config()
		self.username=self.config_dict['username']
		self.password=self.config_dict['password']
		Mastodon.create_app(
			client_name='Mastodon-GTK',
			to_file=CLIENT_CREDENTIALS_FILE
		)
		if not (os.path.isfile(CLIENT_CREDENTIALS_FILE) and os.path.isfile(USER_CREDENTIALS_FILE)):
			self.mclient=Mastodon(client_id=CLIENT_CREDENTIALS_FILE)
			self.mclient.log_in(
			self.username,
			self.password,
			to_file=USER_CREDENTIALS_FILE
			)
		else:
			self.mclient=Mastodon(
				client_id=CLIENT_CREDENTIALS_FILE,
				access_token=USER_CREDENTIALS_FILE
			)

	def toot(self, text):
		if len(text) > 500:
			raise ValueError('Toot longer than 500 characters')
			return
		if len(text) == 0 or text is None:
			raise ValueError('Toot is empty or None')
			return
		self.mclient.toot(text)
