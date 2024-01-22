# create docker base image

docker build -t ecom-base .





# create docker search image
docker build -t ecom-search -f docker/dev/Dockerfile .

docker run -p 8006:8005 ecom-search

