SERVICE=$1
UPLOAD_TO_CLOUD=${2:-"false"}

echo "UPLOAD_TO_CLOUD: $UPLOAD_TO_CLOUD"

echo "Create docker image for service: $SERVICE"

#Build images
if [ $SERVICE = "profile" ] || [ $SERVICE = "booking" ] || [ $SERVICE = "inventory" ] || [ $SERVICE = "ui" ]
then
    rm -rf ../Dockerfile
    cp -rf services/$SERVICE/Dockerfile ../
    if [ $SERVICE = "booking" ]
    then
      cd services/booking
      mvn clean install 2> /dev/null
      cd ../..
    fi
    cd ..
    docker rmi $SERVICE 2> /dev/null
    docker image build -t couchbaseqe/gauntlet:$SERVICE . && docker push couchbaseqe/gauntlet:$SERVICE
    if [ $? != 0 ]
    then
        echo "Error creating the docker image for $SERVICE"
        exit 1
    fi
else
    if [ $SERVICE = "db" ]
    then
          cd database
          docker rmi $SERVICE 2> /dev/null
          docker image build -t couchbaseqe/gauntlet:$SERVICE .
          docker push couchbaseqe/gauntlet:$SERVICE

    else
          if [ $SERVICE = "dataloader" ]
              then
                    rm -rf ../Dockerfile
                    cp -rf clients/$SERVICE/Dockerfile ../
                    cd ..
                    docker rmi $SERVICE 2> /dev/null
                    docker image build -t docker push couchbaseqe/gauntlet:$SERVICE .
                    docker push couchbaseqe/gauntlet:$SERVICE
              else
                    echo "Not a valid service. Valid services are profile, booking,  inventory and ui only"
              exit 1
         fi
    fi
fi

cd $WORKDIR

if [ $UPLOAD_TO_CLOUD == "true" ]
then
    #Login to ECR
    echo "Logging into AWS ECR"

fi
