#!/bin/sh

basedir=$(pwd)
docker system prune -f --all >> /"$basedir"/logdocker.txt 2>&1

for dir in $(ls)
do
        if [ -d "$dir" ]
        then
                cd "$dir" || exit
                if ls ./*docker-compose.yml* > /dev/null 2>&1
                then 
                        docker compose pull >> /"$basedir"/logdocker.txt 2>&1
                        docker compose up -d >> /"$basedir"/logdocker.txt 2>&1
                fi
                cd ..
        fi
done
