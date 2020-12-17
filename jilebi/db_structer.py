from mongoengine import (
    EmbeddedDocument,
    EmbeddedDocumentField,
    Document,
    IntField,
    StringField,
    BooleanField,
    DictField,
    EmbeddedDocumentListField,
    ListField,
    FloatField,
)


class UserSelection(EmbeddedDocument):
    university = StringField()
    faculty = StringField()
    division = StringField()
    semester = StringField()


class Calendar(EmbeddedDocument):
    domain = StringField()
    userid = IntField()
    token = StringField()


class TeleUsers(Document):
    chat_id = IntField(required=True, primary_key=True)
    username = StringField(required=True)
    is_subscriber = BooleanField(default=False)
    is_image_result = BooleanField(default=True)
    selection = EmbeddedDocumentField(UserSelection)
    calendar = EmbeddedDocumentField(Calendar)
    position = IntField(choices=[0, 1, 2, 3, 4, 5])
    feedback = BooleanField(default=False)
    submit = BooleanField(default=False)
    user_submit = EmbeddedDocumentField(UserSelection)
    submit_position = IntField(choices=[0, 1, 2, 3, 4])


class Semester(EmbeddedDocument):
    name = StringField(required=True)
    donor_name = StringField()
    donor_calendar = EmbeddedDocumentField(Calendar)
    modules = DictField(required=True)


class Division(EmbeddedDocument):
    name = StringField(required=True)
    semester = EmbeddedDocumentListField(Semester, required=True)


class Faculty(EmbeddedDocument):
    name = StringField(required=True)
    division = EmbeddedDocumentListField(Division)
    semester = EmbeddedDocumentListField(Semester)


class University(Document):
    name = StringField(required=True, unique=True)
    faculty = EmbeddedDocumentListField(Faculty, required=True)


class Font(EmbeddedDocument):
    name = StringField(required=True)
    size = IntField()


class TextImage(EmbeddedDocument):
    size = ListField(IntField(), required=True)
    place = ListField(IntField(), required=True)
    angle = FloatField(default=0)


class Photo(Document):
    name = StringField(required=True, unique=True)
    font1 = EmbeddedDocumentField(Font)
    font2 = EmbeddedDocumentField(Font)

    meta = {"allow_inheritance": True}


class SingleEvent(Photo):
    image = EmbeddedDocumentField(TextImage)


class DoubleEvent(Photo):
    image1 = EmbeddedDocumentField(TextImage)
    image2 = EmbeddedDocumentField(TextImage)
