Build Step :

docker-compose -f .\stack.yaml build

Run Step :

docker-compose -f .\stack.yaml up -d 

Run redis only : 
docker-compose -f .\stack.yaml up -d redis


To enter redis 

1-docker exec -it tic_toe_game-redis-1 bash
2-redis-cli
3- keys * 