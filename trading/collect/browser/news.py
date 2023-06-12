from collect.browser.frame import CollectBrowserFrame


from collect.news.engine import NewsReader
class CollectBrowserFrameNews(CollectBrowserFrame):
    READER_CLS = NewsReader
    NAMESPACED = True
    NAME = "News"
    reader: NewsReader

    def build(self, master):
        pass
