# Data Pipeline Documentation

## Overview

This document provides a comprehensive guide to the data pipeline designed to transfer data from Microsoft SQL Server to PostgreSQL using Python. The pipeline consists of Docker containers to set up database instances, Python scripts for extraction, transformation, and loading (ETL) of data, and unit tests to ensure the correctness of the ETL process.

## Design

### Docker Setup

The `docker-compose.yml` file defines two services: `sql_server` for SQL Server and `postgresql` for PostgreSQL. Both services are isolated within a custom network named `data_pipeline_network`. The SQL Server service is based on the `mcr.microsoft.com/mssql/server:2019-latest` image, while the PostgreSQL service uses the `postgres:latest` image. Persistent volumes are used to store database data and initialization scripts for both services.

### ETL Application

The `etl_application.py` script performs the ETL process. It connects to the SQL Server database, extracts data, transforms it according to the PostgreSQL schema, and loads it into the PostgreSQL database. The extraction, transformation, and loading processes are parallelized using multiprocessing for improved performance.

### Unit Testing

The `test_etl_application.py` script contains unit tests for the ETL functions defined in `etl_application.py`. It uses the `unittest` framework and mocks external dependencies such as database connections to isolate and test individual components of the ETL process.

### Initialization Scripts

Initialization scripts (`postgresql/init.sql` and `sqlserver/init.sql`) define the schema for PostgreSQL and SQL Server databases, respectively. These scripts are mounted into the corresponding Docker containers to set up the database schema during container initialization.

## Usage

### Prerequisites

- Docker Engine installed on the host machine.
- Python 3.x installed on the host machine.

### Setup

1. Clone the repository containing the data pipeline scripts.
2. Navigate to the project directory.

### Running the Data Pipeline

1. Open a terminal window.
2. Navigate to the project directory.
3. Run the following command to start the Docker containers:

   ```bash
   docker-compose up -d
   ```
4. Once the containers are up and running, run the following command to setup the database and tables in SQL server:

    ```bash
    docker exec -it data-repository_sql_server_1 /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "admin_001@EHR" -i /docker-entrypoint-initdb.d/init.sql
    ```

5. Once the tables are setup, get the IP address of the SQL server and Postgres Sql containers and replace them in the as host in the connection strings. The following commands will give the IP addresses:
    ```bash
    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' data-repository_sql_server_1
    ```
    ```bash
    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' data-repository_postgresql_1

    ```

6. Now execute the ETL process by running the following command:

   ```bash
   python etl_application.py
   ```

7. Monitor the console for any errors or status messages regarding the data transfer process. Additionally, detailed error messages are logged to `etl.log` for further analysis.

### Unit Testing

1. Open a terminal window.
2. Navigate to the project directory.
3. Run the following command to execute unit tests:

   ```bash
   python test_etl_application.py
   ```

4. Review the test results to ensure the correctness of the ETL functions.

### Clean Up

1. To stop and remove the Docker containers, run the following command:

   ```bash
   docker-compose down
   ```

2. Optionally, delete the cloned repository from your system.

## Drawbacks and Enhancements

### Drawbacks

- Lack of error handling: Previous versions of the pipeline lacked comprehensive error handling, potentially leading to unexpected failures during data transfer.

### Enhancements

- **Enhanced Error Handling:** Error handling mechanisms have been implemented throughout the ETL process to catch and handle exceptions gracefully. Detailed error messages are logged to facilitate troubleshooting and analysis.

## Conclusion

The enhanced data pipeline provides a robust and reliable mechanism for transferring data from Microsoft SQL Server to PostgreSQL. By following the provided documentation, users can set up, execute, and test the pipeline effectively. The addition of comprehensive error handling mechanisms ensures resilience and facilitates troubleshooting, addressing a previous drawback of the pipeline.
