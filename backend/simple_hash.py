import bcrypt

password = "Admin123456!"
# 将密码转为字节，生成 salt，然后加密
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

print(f"生成的哈希: {hashed.decode('utf-8')}")
