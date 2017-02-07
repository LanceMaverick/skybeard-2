This beard processes each message that Skybeard receives
and creates a "sentiment score" using the Vader dataset.
The results are stored in an sqlite database. A report
of the chat's "sentiment" (how positive and negative
the messages are by user) by using the "/saltreport"
command.

No message text is stored in the database, only 
when a specific user sent a message and the sentiment
score of that message.

This requires the nltk Vader lexicon and twitter samples 
data.
To download data in nltk check out:
http://www.nltk.org/data.html
