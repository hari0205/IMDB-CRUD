from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email()
    password = fields.Str(load_only=True)


class AdminSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email()
    password = fields.Str(load_only=True)
    is_admin = fields.Bool(dump_only=True)


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class AdminLoginSchema(UserLoginSchema):
    pass


class InputGenreSchema(Schema):
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class CreateMoviesSchema(Schema):
    name = fields.Str()
    director = fields.Str()
    imdb_score = fields.Float()
    _99popularity = fields.Float()
    genres = fields.List(fields.Str())


class UpdateMoviesSchema(CreateMoviesSchema):
    genres = fields.List(fields.Str())


class MovieResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    director = fields.Str()
    imdb_score = fields.Float()
    _99popularity = fields.Float()
    genres = fields.List(fields.Nested(GenreSchema))


class PaginatedResponseSchema(Schema):
    page = fields.Int(dump_only=True)
    per_page = fields.Int(dump_only=True)
    total = fields.Int(dump_only=True)
    movies = fields.Nested((MovieResponseSchema(many=True)))


class ErrorResponseSchema(Schema):
    code = fields.Int()
    message = fields.Str()
    status = fields.Str()


class LoginResponseSchema(Schema):
    access_token = fields.Str()
    message = fields.Str()


class DeleteResponseSchema(Schema):
    message = fields.Str()


class RegisterResponseSchema(Schema):
    code = fields.Int()
    message = fields.Str()


class RegisterAdminResponseSchema(RegisterResponseSchema):
    access_token = fields.Str()
    message = fields.Str()


class LoginAdminResponseSchema(LoginResponseSchema):
    access_token = fields.Str()
    message = fields.Str()
