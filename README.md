# PyNewsletter

Allows you to send newsletters (whose content is purely text) by email and handle the unsubscribing of users (removing them from the CSV emailing list and sending them a message when they unsubscribe if that option is enabled in the [config.py](config.py))

## Getting it up and Running


### Prerequisites

You will need Python3 and the Pandas library installed to use this <br/>
To install pandas on Python3 open a terminal and type:
```
pip3 install pandas
```

## Adapting it to your needs


All you need to do is modify the [config.py](config.py) file to get it to work for your needs<br/>
DISCLAIMER: This was only tested using a Gmail account it may not work for other email accounts

## How does it work?

* Load the contacts from the CSV file specified in the [config.py](config.py) - An example CSV file is provided to help understand the format it should take [contacts.csv](contacts.csv) (it must always contain a column named "Email")
* Check if anyone unsubscribed by accessing the email used to send the newsletters using the IMAP protocol, filtering by unseen messages with the subject specified in said config file (CANCEL_SUBJECT_KEYWORD)
* Contacts unsubscribed will be removed from CSV, if SEND_UNSUB_MESSAGE is true, they will get an email you can specify in the config file
* All the contacts that remain in the emailing list will be sent the newsletter specified in the config file

## Authors

* **Diogo Paulico** - *Initial work*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to all that made the examples from where I learned to use IMAP, SMTP and Pandas
