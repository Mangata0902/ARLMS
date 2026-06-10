from passlib.context import CryptContext

# 使用你后端实际使用的配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 我们将密码设置为 'Admin123456!'
password = "Admin123456!"
hashed = pwd_context.hash(password)

print(f"--- 请复制下面这行字符串 ---")
print(hashed)
print(f"--------------------------")
