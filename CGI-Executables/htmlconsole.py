#module for a console in html for debug printing

class HtmlConsole:
    def __init__(self):
        self.buffer = '' ;

    def append(self, str):
        self.buffer = self.buffer + '</br>' + str

    def display(self):
        print '<div class="DebugConsole">'
        print self.buffer
        print '</div>'

