""" Holds classes for error messages """
class invalid_usage(Exception):
    """ returns a custom error message to client """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """ converts message to dictionary for conversion into json payload """
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
