 apt-get install lsb-release curl gpg
curl -fsSL https://packages.redis.io/gpg |  gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
 chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" |  tee /etc/apt-get/sources.list.d/redis.list
 apt-get update
 apt-get install redis