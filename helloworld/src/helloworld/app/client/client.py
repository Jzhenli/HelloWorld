import toga

class client(toga.App):
    def startup(self):
        self.web_view = toga.WebView()
        self.web_view.url = f"http://127.0.0.1:9500/docs"
        self.main_window = toga.Window()
        self.main_window.content = self.web_view
        self.main_window.show()

def run_client():
    c = client("demo", "org.beeware.tutorial")
    c.main_loop()