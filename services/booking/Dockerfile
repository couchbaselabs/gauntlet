FROM openjdk:8
VOLUME /tmp
EXPOSE 8080
ADD gauntlet/services/booking/target/*.jar bookingService.jar
ENTRYPOINT [ "sh", "-c", "java -jar /bookingService.jar" ]