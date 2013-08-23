from autonomic import axon, alias, category, help, Dendrite
from time import mktime, localtime, strftime
from secrets import TWILIO_SID, TWILIO_TOKEN, TWILIO_NUMBER, SAFE_NUMBERS
from settings import CONTROL_KEY, CHANNEL
from twilio.rest import TwilioRestClient

@category("sms")
class Sms(Dendrite):
    def __init__(self, cortex):
        super(Sms, self).__init__(cortex)
        self.incoming = []
        self.i = 0
        self.errors = 0
        self.current = mktime(localtime())
        self.next_ = self.current + 10
        self.cx.addlive(self.ticker)
        return

    def ticker(self):
        self.current = mktime(localtime())

        if self.current == self.next_:
            self.next_ += 20
            try:
                messages = False
                client = TwilioRestClient(TWILIO_SID, TWILIO_TOKEN)
                messages = client.sms.messages.list(to="+16468635380")
                
                for item in messages:
                    message = item.from_ + ": " + item.body
                    sid = item.sid
                    if sid not in self.incoming:
                        self.incoming.append(sid)
                        if self.i > 0:
                            self.chat(message) 
                            #if item.body[:1] == CONTROL_KEY and item.from_ in SAFE_NUMBERS:
                            #   self.cx.command(SAFE_NUMBERS[item.from_], item.body) 
                    
                self.i += 1
            except:
                self.errors += 1
        
        return

    @axon
    @help("[NUMBER] [MESSAGE] <send an sms message to unsuspecting victim>")
    def sms(self):
        if self.context != CHANNEL:
            self.chat("No private sms abuse. Tsk tsk.")
            return

        if not self.values:
            self.chat("-sms <number> <message>")
            return

        to = self.values[0]
        msg = " ".join(self.values[1:])

        try:
            client = TwilioRestClient(TWILIO_SID, TWILIO_TOKEN)
            message = client.sms.messages.create(
                body=msg,
                to=to,
                from_=TWILIO_NUMBER
            )
            self.chat("Message sent: " + message.sid)
        except:
            self.chat("Done broke")
            return

    @axon
    @help("[FROM NUMBER] <check for sms replies to messages previously sent to unsuspecting victims>")
    def smsmsgs(self):

        if not self.values:
            self.chat("What number?")
            return

        num = self.values[0]

        try:
            client = TwilioRestClient(TWILIO_SID, TWILIO_TOKEN)
            messages = client.sms.messages.list(to="+16468635380",from_=num)
            for item in messages:
                self.chat(item.from_ + ": " + item.body)
        except:
            self.chat("Done broke")
            return
