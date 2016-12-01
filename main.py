#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf
import os
import sys
import mastodonHelper

EXEC_FOLDER = os.path.realpath(os.path.dirname(__file__)) + "/"
builder = Gtk.Builder()
builder.add_from_file(EXEC_FOLDER + "ui.glade")
HOME = os.environ.get('HOME')

IMG_CHAR_SIZE=36

settings = Gtk.Settings.get_default()
settings.set_property("gtk-application-prefer-dark-theme", True)

class App(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self,
								 application_id="org.gabmus.mastodon-gtk",
								 flags=Gio.ApplicationFlags.FLAGS_NONE)
		self.connect("activate", self.activateCb)

	def do_startup(self):
		# start the application
		Gtk.Application.do_startup(self)

	def activateCb(self, app):
		window = builder.get_object("window")
		window.set_wmclass("Mastodon GTK", "Mastodon GTK")
		window.set_title("Mastodon GTK")
		app.add_window(window)
		appMenu = Gio.Menu()
		appMenu.append("About", "app.about")
		appMenu.append("Quit", "app.quit")
		about_action = Gio.SimpleAction.new("about", None)
		about_action.connect("activate", self.on_about_activate)
		builder.get_object("aboutdialog").connect(
			"delete-event", lambda *_: builder.get_object("aboutdialog").hide() or True)
		app.add_action(about_action)
		quit_action = Gio.SimpleAction.new("quit", None)
		quit_action.connect("activate", self.on_quit_activate)
		app.add_action(quit_action)
		app.set_app_menu(appMenu)
		window.show_all()

	def on_about_activate(self, *agrs):
		builder.get_object("aboutdialog").show()

	def on_quit_activate(self, *args):
		self.quit()

app = App()
mastodon_cl=mastodonHelper.MastodonClient()

toot_btn=builder.get_object('tootButton')

new_toot_textbuf=builder.get_object('newTootTextBuffer')
new_toot_text_view=builder.get_object('newTootTextView')
toot_charnum_label=builder.get_object('tootCharnumLabel')
toot_image_flowbox=builder.get_object('tootImageFlowbox')

toot_spinner = builder.get_object('tootSpinner')

delete_image_btn=builder.get_object('deleteImageButton')

images_to_toot=[]

def update_show_delete():
	if len(images_to_toot) > 0:
		delete_image_btn.show()
	else:
		delete_image_btn.hide()

def add_image_to_flowbox(path):
	pbuf=GdkPixbuf.Pixbuf().new_from_file_at_scale(path, -1, 100, True)
	img_w=Gtk.Image()
	img_w.set_from_pixbuf(pbuf)
	toot_image_flowbox.insert(img_w, -1)
	img_w.show()
	img_w.value=path
	images_to_toot.append(path)
	update_show_delete()

def remove_image_from_flowbox(child):
	toot_image_flowbox.remove(child)
	del images_to_toot[images_to_toot.index(child.get_child().value)]
	update_show_delete()

def wait_for_thread(thread):
	while thread.is_alive():
			while Gtk.events_pending():
				Gtk.main_iteration()
	return

class Handler:

	def onDeleteWindow(self, *args):
		app.quit()

	def on_newTootTextBuffer_changed(self, *args):
		l = len(self._get_buf_text())+(IMG_CHAR_SIZE*len(images_to_toot))
		if l>500:
			toot_btn.set_sensitive(False)
		else:
			toot_btn.set_sensitive(True)
		toot_charnum_label.set_text(str(l))

	def _get_buf_text(self):
		start_iter = new_toot_textbuf.get_start_iter()
		end_iter = new_toot_textbuf.get_end_iter()
		to_ret=new_toot_textbuf.get_text(
			start_iter,
			end_iter,
			True
		)
		return to_ret


	def on_tootButton_clicked(self, btn):
		has_pics=False
		toot_spinner.start()
		new_toot_text_view.set_sensitive(False)
		toot_btn.set_sensitive(False)
		if len(images_to_toot) == 0 or len(images_to_toot) > 4:
			t = mastodon_cl.toot(self._get_buf_text(), None)
		else:
			t = mastodon_cl.toot(self._get_buf_text(), images_to_toot)
			has_pics=True
		wait_for_thread(t)
		if has_pics:
			pic_dic=mastodon_cl.media_list
			mastodon_cl.media_list=None
			txt_to_toot=self._get_buf_text()
			media_ids=[]
			for dic in pic_dic:
				txt_to_toot+=' '+dic['text_url']
				media_ids.append(dic['id'])
			t = mastodon_cl.toot(txt_to_toot, None, media_ids, None)
			wait_for_thread(t)
		new_toot_textbuf.set_text('')
		new_toot_text_view.set_sensitive(True)
		toot_spinner.stop()
		toot_btn.set_sensitive(True)
		toot_charnum_label.set_text('0')


	def on_tootImageFCButton_file_set(self, btn):
		img_path=btn.get_filename()
		add_image_to_flowbox(img_path)
		self.on_newTootTextBuffer_changed(None)

	def on_deleteImageButton_clicked(self, btn):
		child=toot_image_flowbox.get_selected_children()[0]
		print(child, images_to_toot.index(child.get_child().value))
		remove_image_from_flowbox(child)
		self.on_newTootTextBuffer_changed(None)

builder.connect_signals(Handler())


if __name__ == "__main__":
	app.run(sys.argv)
