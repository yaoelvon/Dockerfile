### HOWTO
---
docker run -d --restart=always -e "PASSWORD=<your_password>" -v /notebooks:/notebooks -p 8888:8888 zjqzero/jupyter-notebook

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out key.pem -subj "/C=XX/ST=XX/L=XX/O=dockergenerated/CN=dockergenerated"