import bcrypt

password = 'passwort'.encode('utf-8')
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

print(hashed.decode('utf-8'))
