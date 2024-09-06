import pexpect
import sys

# Detail login OLT
host = "103.247.22.229"
username = "yayan"
password = "Yayan@12345"
output_file = "running_config.txt"
port = 234

# Mulai sesi telnet dengan pexpect
child = pexpect.spawn(f'telnet {host} {port}')

# Menunggu prompt login dan memasukkan username
child.expect("Username:")
child.sendline(username)

# Menunggu prompt password dan memasukkan password
child.expect("Password:")
child.sendline(password)

# Menunggu prompt setelah login berhasil
child.expect("#")
print('send command')
# Mengirimkan command 'show running config'
child.sendline("show running-config")

output = ""
while True:
    i = child.expect(["--More--", "#"], timeout=300)
    output += child.before.decode('ascii')
    if i == 0:  # Jika '--More--' ditemukan
        
        child.sendline(" ")  # Kirim space untuk melanjutkan
    elif i == 1:  # Jika '#' ditemukan
        break

# Menunggu output perintah selesai
# child.expect("#", timeout=300)  # timeout disesuaikan jika perlu
# output = child.before.decode('ascii')

# Menyimpan output ke dalam file teks
with open(output_file, 'w') as f:
    f.write(output.strip())

# Tutup sesi telnet
child.sendline("exit")
child.expect(pexpect.EOF)
