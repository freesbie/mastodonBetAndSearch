from mastodon import Mastodon
from mastodon.streaming import StreamListener
import configparser
import lxml.html as html
import re

BLACKLIST = ["badguy@mastodon.example", "evilinstance.example"]
OFFER_BLACKLIST = ["bubaz", "waffe"]
MYNAME = "betsearch"
MYDOMAIN = "sueden.space"

class myListener(StreamListener):
    def on_notification(self,notification):
        try:
            qname = None
            qtype = None

            if notification['type'] == 'mention':
                id = notification['status']['id']
                sender = notification['account']['acct']
                # check if sender is in blacklist
                if sender in BLACKLIST:
                    self.log.info("Service refused to %s" % sender)
                    return
                # check if sender domain is in blacklist
                match = re.match("^.*@(.*)$", sender)
                if match:
                    sender_domain = match.group(1)
                    if sender_domain in BLACKLIST:
                        self.log.info("Service refused to %s" % sender)
                        return
                else:
                    # Probably local instance, without a domain name. Note that we cannot blacklist local users.
                    if sender == MYNAME:
                        print("Loop detected, sender is myself")
                        return
                visibility = notification['status']['visibility']
                spoiler_text = notification['status']['spoiler_text']
                doc = html.document_fromstring(notification['status']['content'])
                # Preserve end-of-lines
                for br in doc.xpath("*//br"):
                                br.tail = "\n" + br.tail if br.tail else "\n"
                for p in doc.xpath("*//p"):
                            p.tail = "\n" + p.tail if p.tail else "\n"
                body = doc.text_content()

                print(f"New mention from: {sender}, StatusID: {id}")
                print(f"Message {body}\n")

                #### parse the message #####
                # if helpme or howto in body then send the helptext as direct message: exit
                
                # if second line is: search, then extract the search string
                    # search in sqlite and send sender the status from the provider back: exit
                
                # if 2.line is: offer extract the subject
                    # 3.line: extract price
                    # 4.line: extract description
                    # save to sqlite
                    # inform sender that the offer is saved and for x days in service
                
        
        except KeyError as error:
            print("Malformed notification, missing %s" % error)
        except Exception as error: 
            print("%s %s/%s -> %s" % (sender, qname, qtype, error))

def mastodonConnect():
    config = configparser.ConfigParser()
    config.read('config.ini')
    mastodon = Mastodon(config['MASTODON']['client_id'], 
                config['MASTODON']['client_secret'],
                config['MASTODON']['access_token'],
                config['MASTODON']['base_url']
                )
    return mastodon

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    mastodon = mastodonConnect()
    listener = myListener()
    mastodon.stream_user(listener)


if __name__ == '__main__':
    main()
