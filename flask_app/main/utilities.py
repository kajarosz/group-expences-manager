from hashlib import md5
import re

MD5_SECRET = 'splitwise'

def hash_md5(password: str) -> str:
    result = md5(password.encode("utf-8"))
    result.update(MD5_SECRET.encode("utf-8"))
    return result.hexdigest()


regex_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def is_email_valid(email):
    if re.fullmatch(regex_email, email):
      return True
    else:
      return False

regex_pass = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

def is_pass_valid(password):
    if re.fullmatch(regex_pass, password):
      return True
    else:
      return False