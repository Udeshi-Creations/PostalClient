"""
A Wrapper for the Postal REST API.
"""

import base64
import mimetypes
import magic
import json



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

    def __init__(self, name: str=None):
        """Creates empty attachment"""
        if name:
            self.name = name


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



if __name__ == "__main__":
    myFile = Attachment()
    myFile.data = "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fWpIClT+yck779xJN3OYBeUM3v8HAAD//6odnIkAACk3SURBVO1dCXgURRZOuO87CacSubwCwUUhCIKoXKKwCiJELjkElcgRlABZBDXch4KAIKwgAnIqqOsBuAIKKAqiqNxIwhWWG4QgMPv31KSp9Mz0dPf0UTN54fuG6upX1a/+V13V9V69V5H33XdfhEN/VapUWb58OR5+9erVK1eueHNRokQJZH7++ecjR46U744YMeKxxx6TL8+cObNjx45t27Zt2rTp+PHjcj4So0ePbtGiBRIJCQk3btzgb4mT/v777y1lxkH5amnXRx99VKFCBTelKyIikk9AZM2aNbt8+TKrZ+DAgR2ffppRsBxWQFFMvmQ03K90Z9GiRW+++SaXaW2yYMGCHTt2xC8eg176ww8/BHyeFpqAlRABIUAIEAKEgF4E7r33Xr1FRKDfunUr2HjkkUfOnz+vl5+0MWkPNXto3LhxK1eu1FvWcXq902Uoynfw4OSnnuowZ86cd999Vy/gdevWnTVr1oEDBzp16qS3rAj0uUG+Ms6TJk1q1KjRb7/91rNnT7Zg6devX7fu3VetXInXE+KvHRc3fPjwtWvXokjp0qUXL16MX/QK9A25ktBKhLd8+/dPSkzs1KBBgkIocXFxz/Z4tliJ4ljOyAsWOaEgzr703D937tx//vMf1geyb4n7v175itsS4kwDAv6m165du77wwgusgszMzOeee+7o0aMa6rtJ8tdff8kXRYoUkdP2JKBcyp8/v89n1a9fn+WzbzAFjeKu4lJBjMu///4bU4B3vkU50K64XBhYPH/2A8sevGbNmujoKF7/g04ia/m+/vprxphihGSX+EUrHmzalFW1es2amOhoT3vc/53IzHycUxjyt6xL890VT3EKWNZA1jNluHgdGoeAjK6U2LBhw5AhQ7i7UrJHjx59+/Z97733Zs6cqbhl26X9wGa/1znw4dqLFygy0o0po7h48eKUyVM++fQT0ODze0RqauVKlZDG3XNnz44fP37dunVccU+yXLlyn376KTThjRs3VtwtVarUF198ce3atfvvv19xy8RL+4H1Zh7DbL78+Rs3aoRh0PuuKTkYxvEUm4dZcM7gjXRQHS+bW7C04Ad9BazoaqNGjeIzYT7p3LlzfHx8gQIF5Hz01HfeeQf6dNmyQuYWgOOgfGXRqCRga8GQxIYr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"
    print(myFile.sendFormat())

    sender = Addressee('Prem', 'info@udeshi.dev')
    myEmail = Email()
    myEmail.sender = sender
    myEmail.addReciever(Addressee('Prem Udeshi', 'premudeshi99@gmail.com'))

    myEmail.subject = "Hello World"
    myEmail.attachments.append(myFile)

    myEmail.plain_text = "This is an email test!"

    myEmail.tag = "Email Text"

    print(json.dumps(myEmail.makeEmail()))
