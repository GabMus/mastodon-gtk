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

# settings = Gtk.Settings.get_default()
# settings.set_property("gtk-application-prefer-dark-theme", True)

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

new_toot_textbuf=builder.get_object('newTootTextBuffer')

class Handler:

	def onDeleteWindow(self, *args):
		app.quit()

	def on_tootButton_clicked(self, btn):
		mastodon_cl.toot(
			new_toot_textbuf.get_text()
		)
		new_toot_textbuf.set_text('')


builder.connect_signals(Handler())


if __name__ == "__main__":
	app.run(sys.argv)
