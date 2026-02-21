# Dockerfile for building backend container for deployment.

FROM openjdk:8-jre

COPY ./target/*.jar /app.jar

CMD ["java", "-jar", "/app.jar"]