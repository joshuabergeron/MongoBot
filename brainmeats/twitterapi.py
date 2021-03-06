import twitter

from autonomic import axon, alias, category, help, Dendrite
from settings import NICK
from secrets import (TWIT_USER, TWIT_PASS, TWIT_ACCESS_TOKEN, TWIT_ACCESS_SECRET,
    TWIT_CONSUMER_KEY, TWIT_CONSUMER_SECRET, TWIT_PAGE)


@category("twitter")
class Twitterapi(Dendrite):
    def __init__(self, cortex):
        super(Twitterapi, self).__init__(cortex)

        self.api = twitter.Api(consumer_key=TWIT_CONSUMER_KEY,
                               consumer_secret=TWIT_CONSUMER_SECRET,
                               access_token_key=TWIT_ACCESS_TOKEN,
                               access_token_secret=TWIT_ACCESS_SECRET)

    @axon
    @help("<show link to " + NICK + "'s twitter feed>")
    def totw(self):
        self.chat(TWIT_PAGE)

    @axon
    @help("MESSAGE <post to " + NICK + "'s twitter feed>")
    def tweet(self):
        if not self.values:
            self.chat("Tweet what?")
            return
        
        message = ' '.join(self.values)
        status = self.api.PostUpdate(message)
        self.chat('Tweeted "' + status.text + '"')
