# importing schema and fields from Python marshmallow
from marshmallow import Schema, fields
# creating python class
class CreatingSchema(Schema):
    # first name as required input
    firstName = fields.Str(required = True)
    # last name and age as not required inputs
    lastName = fields.Str()
    email = fields.Email()
# creating information
info = {
    'firstName' : 'Bashir',
    'lastName' : 'Alam',
    'email' : 'baashir@gmail.com'
}
# serializing in Python
user_info = CreatingSchema().load(info)
print(user_info,type(user_info))