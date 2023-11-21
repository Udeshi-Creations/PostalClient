"""
A Wrapper for the Postal REST API.
"""

import base64
import email
import mimetypes
import magic
import json

import re

from email.utils import parseaddr


class Addressee:
    """Class for Storing name and Email Address, to allow easy creation of recipient headers"""
    name: str
    """The name of adressee."""

    email: str
    """The email address of adressee."""

    def __init__(self, name: str, email:str):
        """Make an addresse. Requires name and email"""
        self.name = name
        self.email = email

    def sendFormat(self, loud: bool = True):
        """Return appendable string"""
        return "{} <{}>".format(self.name, self.email)


class Attachment:
    """Attachment Class"""
    name: str
    """File name of file if available. Defaults to file"""
    data : str
    """Base64 data representation of file"""
    ext : str

    def __init__(self, name: str=None):
        """Creates empty attachment"""
        if name:
            self.name = name
        self.ext = None
        self.data = ''


    def sendFormat(self):
        """Creates an attachment array"""
        decoded_bytes = base64.b64decode(self.data)

        # Use python-magic to get the MIME type
        mime_type = magic.from_buffer(decoded_bytes, mime=True)

        #print(f'MIME type: {mime_type}')
        extension = mimetypes.guess_extension(mime_type)

        # Print the MIME type and extension
        #print(f'MIME type: {mime_type}')
        #print(f'Extension: {extension}')

        try:
            #print("{}.{}".format(self.name, extension))
            name = "{}{}".format(self.name, extension)
        except:
            #print("file{}".format(extension))
            name = "file{}".format(extension)

        return {"name":name, "data":self.data}

    def fixFile(self):
        """Function to fix base64"""
        self.data = self.data.replace('\n', '')

    def fileBytes(self):
        """Returns the file content in bytes format"""
        self.fixFile()
        return base64.b64decode(self.data)

    def makeFile(self):
        try:
            file_content = self.fileBytes()
            with open("file{}".format(self.ext), "wb") as f:
                f.write(file_content)
        except Exception as e:
            print(str(e))

class Email:
    """Email Class"""
    sender: Addressee
    """The sender name and email, uses Addresse Class"""

    srv_account: Addressee
    """The server name and email, uses Addresse Class"""

    rply_to: Addressee
    """The reply to email, uses Addresse Class"""

    reciever: list
    """Reciever List of addresse"""
    cc: list
    """CC List of addresse"""
    bcc:list
    """BCC List of addresse"""
    subject: str
    """Subject of email"""
    html:str
    """HTML content of email"""
    plain_text: str
    """Plain Text content of email"""
    attachments:list
    """List of all Attachments"""
    tag:str
    """Postal feature to add a tag to the email for easy debugging"""

    extra:dict
    """Dictionary of extra elements recieved from email.
    - date (datetime of email)
    - Second item
    - Third item
    - Fourth item
    """

    def __init__(self):
        self.sender = None
        self.srv_account =None
        self.rply_to = None
        self.reciever = []
        self.cc = []
        self.bcc = []
        self.subject = None
        self.html = None
        self.plain_text = None
        self.attachments = []
        self.tag = None
        self.extra = {}

    def addReciever(self, addressee:Addressee):
        """Add a reciever"""
        self.reciever.append(addressee)

    def addCC(self, addressee:Addressee):
        """Add a carbon copy (CC) reciever"""
        self.cc.append(addressee)

    def addBCC(self, addressee:Addressee):
        """Add a black carbon copy (BCC) reciever"""
        self.bcc.append(addressee)

    def makeEmail(self):
        """Function that creates the JSON Email, preparing the system to send emails."""

        data = {}
        #First create header info for senders

        recievers = []
        for person in self.reciever:
            recievers.append(person.sendFormat())
        data['to'] = recievers

        recievers = []
        for person in self.cc:
            recievers.append(person.sendFormat())
        data['cc'] = recievers

        recievers = []
        for person in self.bcc:
            recievers.append(person.sendFormat())
        data['bcc'] = recievers

        data['from'] = self.sender.sendFormat()
        if self.srv_account:
            data['sender'] = self.srv_account.sendFormat()

        if self.rply_to:
            data['reply_to'] = self.rply_to.sendFormat()

        if self.tag:
            data['tag'] = self.tag
        data['subject'] = self.subject

        if self.plain_text:
            data['plain_body'] = self.plain_text
        if self.html:
            data['html_body'] = self.html

        attachments = []
        for attachment in self.attachments:
            attachments.append(attachment.sendFormat())
        data['attachments'] = attachments

        return data

    def extractAddress(self, text):
        addresses = []

        pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

        matches = re.findall(pattern, text)

        for match in matches:
            start = text.find(match)
            end = start + len(match)
            name = text[:start].strip(", \"")
            email = match
            thisAdd = Addressee(cleanText(name), email)
            #print(f"Name: {cleanText(name)}, Email: {email}")
            addresses.append(thisAdd)
            text = text[end:]

        return addresses

    def importEmail(self, jsonString):
        data = json.loads(jsonString)

        sender = email.utils.parseaddr(data["from"])
        self.sender = Addressee(sender[0], sender[1])

        self.reciever = self.extractAddress(data['to'])

        if data['cc']:
            self.cc = self.extractAddress(data['cc'])
        self.extra['date'] = data['date']

        self.html = data['html_body']
        self.plain_text = data['plain_body']

        if data['attachment_quantity'] > 0:
            attachments = data['attachments']
            for attachment in attachments:
                myAttachment = Attachment()
                myAttachment.data = attachment['data']
                myAttachment.name = attachment['filename'].split(".")[0]
                myAttachment.ext = ".{}".format(attachment['filename'].split(".")[1])
                self.attachments.append(myAttachment)

        self.subject=data['subject']

        self.extra['id'] = data['id']

    def readSendFormat(self, input):
        """This function reads the sendFormat function output, for easy storage"""
        #data = json.loads(input)
        data = input
        for person in data['to']:
            personData = email.utils.parseaddr(person)
            self.reciever.append(Addressee(personData[0], personData[1]))

        for person in data['cc']:
            personData = email.utils.parseaddr(person)
            self.reciever.append(Addressee(personData[0], personData[1]))

        for person in data['bcc']:
            personData = email.utils.parseaddr(person)
            self.reciever.append(Addressee(personData[0], personData[1]))

        sender = email.utils.parseaddr(data['from'])
        self.sender = Addressee(sender[0], sender[1])

        if 'sender' in data:
            sender = email.utils.parseaddr(data['sender'])
            self.srv_account = Addressee(sender[0], sender[1])

        if 'reply_to' in data:
            sender = email.utils.parseaddr(data['reply_to'])
            self.rply_to = Addressee(sender[0], sender[1])

        if 'tag' in data:
            self.tag = data['tag']


        self.subject = data['subject']

        if 'plain_body' in data:
            self.plain_text = data['plain_body']

        if 'html_body' in data:
            self.html = data['html_body']

        for attachment in data['attachments']:
            myAttachment = Attachment()
            myAttachment.data = attachment['data']
            myAttachment.name = attachment['name'].split(".")[0]
            myAttachment.ext = ".{}".format(attachment['name'].split(".")[1])
            self.attachments.append(myAttachment)

        return data



def cleanText(text):
    bad_chars = [';', ':', '!', "*", "<", ">", '"', ","]
    for i in bad_chars:
        text = text.replace(i, '')
    return text


if __name__ == "__main__":
    myFile = Attachment()
    #print(myFile.sendFormat())

    sender = Addressee('Prem', 'info@udeshi.dev')
    myEmail = Email()
    myEmail.sender = sender
    myEmail.addReciever(Addressee('Prem Udeshi', 'premudeshi99@gmail.com'))

    myEmail.subject = "Hello World"
    #myEmail.attachments.append(myFile)
    #print(myEmail.makeEmail())

    myEmail.plain_text = "This is an email test!"

    myEmail.tag = "Email Text"

    newEmail = Email()
    newEmail.readSendFormat(myEmail.makeEmail())
    #print(newEmail.sender.sendFormat())

    #print(json.dumps(myEmail.makeEmail())




