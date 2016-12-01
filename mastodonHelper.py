from mastodon import Mastodon
import os
import json
import threading

HOME = os.environ.get('HOME')
CONFIG_DIR = HOME + '/.config'
CONFIG_FILE = CONFIG_DIR + '/org.gabmus.mastodon-gtk.config.json'
CLIENT_CREDENTIALS_FILE = CONFIG_DIR + '/org.gabmus.mastodon-gtk.client-credentials'
USER_CREDENTIALS_FILE = CONFIG_DIR + '/org.gabmus.mastodon-gtk.user-credentials'

DEFAULT_CONFIG =  {
	'username':'',
	'password':''
}

def check_config():
	# check existence of ~/.config dir, eventually create one
	if not os.path.isdir(CONFIG_DIR):
		os.makedirs(CONFIG_DIR)
		
	# check existence of the CONFIG_FILE, eventually create an empty one
	if not os.path.isfile(CONFIG_FILE):
		out=open(CONFIG_FILE, 'w')
		out.write(json.dumps(DEFAULT_CONFIG))
		out.close()

def read_config():
	"""Returns config file json"""
	check_config()
	config_f = open(CONFIG_FILE, 'r')
	try:
		configtxt = config_f.read()
		config_f.close()
	except ValueError:
		config_f.close()
	return json.loads(configtxt)

class MastodonClient:
	
	media_list=None

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
	
	def _do_async(self, func, args):
		t=threading.Thread(
			group=None,
			target=func,
			name=None,
			args=args
		)
		t.start()
		#t.run()
		#t.join()
		return t

	def _load_pics(self, text, pic_list):
		media_list_toret=[]
		for pic in pic_list:
			media_list_toret.append(self.mclient.media_post(pic))
		self.media_list=media_list_toret
		return

	def toot(self, text, pic_list=None, media_ids=None, in_reply_to=None):
		if len(text) > 500:
			raise ValueError('Toot longer than 500 characters')
			return
		if len(text) == 0 or text is None:
			raise ValueError('Toot is empty or None')
			return
		if not media_ids is None or not in_reply_to is None:
			return self._do_async(
				self.mclient.status_post,
				(text,in_reply_to,media_ids),
			)
		if pic_list is None:
			return self._do_async(self.mclient.toot, ([text]))
		else:
			return self._do_async(self._load_pics, ([text],pic_list))
